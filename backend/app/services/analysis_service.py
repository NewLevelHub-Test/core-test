import base64
import os
import random
import re
import chess
import chess.engine
from openai import OpenAI
from app import db
from app.models.game import Game
from app.models.move import Move
from app.models.mistake import Mistake
from app.models.exercise import Exercise
from app.models.topic import Topic
from app.services.chess_service import ChessService
from app.models.analysis_cache import AnalysisCache
from app.chess.pgn_utils import parse_pgn

MAX_KEY_MISTAKES = 3

CATEGORY_EXPLANATIONS = {
    'opening': [
        'В начале партии важно развивать фигуры. Попробуй быстрее вывести их в игру.',
        'Не забудь про центр. Старайся контролировать его своими фигурами.',
        'Лучше не ходить одной и той же фигурой много раз в начале.',
        'Попробуй сначала развить коней и слонов, а потом уже атаковать.',
        'Не выводи ферзя слишком рано. Его могут легко прогнать.',
        'Сделай рокировку пораньше, чтобы король был в безопасности.',
        'Старайся не оставлять фигуры без защиты в начале партии.',
        'Развивай фигуры так, чтобы они помогали друг другу.',
        'Не торопись с атакой. Сначала подготовь свои фигуры.',
        'Подумай, какие фигуры ещё не играют, и попробуй их развить.',
        'Хороший дебют это когда почти все фигуры участвуют в игре.',
        'Не перекрывай своим фигурам дорогу пешками.',
    ],

    'tactic': [
        'Ты пропустил возможность выиграть фигуру. Будь внимательнее.',
        'Попробуй искать шахи, взятия и угрозы на каждом ходу.',
        'Здесь можно было сделать хитрый ход и получить преимущество.',
        'Смотри, не оставляешь ли ты фигуры под ударом.',
        'Иногда один ход может всё изменить. Ищи такие моменты.',
        'Попробуй решать больше задач на тактику. Это поможет замечать такие идеи.',
        'Обрати внимание на связки и вилки. Это сильные приёмы.',
        'Ты мог поставить шах и создать угрозу одновременно.',
        'Иногда стоит остановиться и проверить, нет ли у соперника опасного хода.',
        'Ищи ходы, которые нападают сразу на две фигуры.',
        'Будь внимателен. Соперник может готовить ловушку.',
        'Попробуй находить комбинации из нескольких ходов вперёд.',
    ],

    'positional': [
        'Попробуй ставить фигуры на более активные позиции.',
        'Фигуры должны помогать друг другу. Обрати на это внимание.',
        'Не оставляй слабые поля без защиты.',
        'Старайся контролировать больше пространства на доске.',
        'Подумай, какая фигура стоит неудачно, и улучши её позицию.',
        'Не спеши. Иногда лучше сделать спокойный, но полезный ход.',
        'Хорошая позиция это когда твои фигуры активнее, чем у соперника.',
        'Попробуй ограничить движение фигур соперника.',
        'Сильные клетки это отличное место для твоих фигур.',
        'Следи за пешечной структурой. Она очень важна.',
        'Иногда лучше укрепить позицию, чем сразу атаковать.',
        'Подумай, какие у тебя есть слабости, и защити их.',
    ],

    'endgame': [
        'В эндшпиле важно активизировать короля. Не бойся им ходить.',
        'Пешки становятся очень сильными. Старайся продвигать их вперёд.',
        'Попробуй поставить короля ближе к центру доски.',
        'Не спеши. В конце партии важно играть точно.',
        'Старайся создавать проходные пешки.',
        'Король это сильная фигура в эндшпиле. Используй его.',
        'Подумай, как можно провести пешку в ферзи.',
        'Не отдавай пешки просто так. Они очень важны.',
        'Попробуй ограничить короля соперника.',
        'Даже маленькое преимущество можно превратить в победу.',
        'Старайся держать фигуры активными до самого конца.',
        'В эндшпиле важно считать ходы чуть вперёд.',
    ],
}

def _classify_move_phase(move_number):
    if move_number <= 10:
        return 'opening'
    elif move_number <= 30:
        return 'tactic'
    else:
        return 'endgame'


class AnalysisService:
    @staticmethod
    def _move_color_by_index(move_number):
        return 'white' if move_number % 2 == 1 else 'black'

    @staticmethod
    def _analyze_parsed_moves(parsed_moves):
        from app.chess.stockfish_engine import StockfishEngine
        pool = StockfishEngine()
        engine = pool._acquire()

        analysis_list = []
        blunders = []
        prev_eval_white = 0.0

        try:
            for idx, move in enumerate(parsed_moves, start=1):
                fen_after = move.get('fen_after')
                if not fen_after:
                    continue

                cached = AnalysisCache.query.filter_by(fen=fen_after).first()
                if cached:
                    eval_score = cached.evaluation
                    best = cached.best_move
                else:
                    board = chess.Board(fen_after)
                    info = engine.analyse(board, chess.engine.Limit(depth=14))
                    score_obj = info['score'].white()
                    if score_obj.is_mate():
                        eval_score = 100.0 if score_obj.mate() > 0 else -100.0
                    else:
                        eval_score = score_obj.score() / 100.0
                    best = info['pv'][0].uci() if info.get('pv') else None
                    db.session.add(AnalysisCache(fen=fen_after, evaluation=eval_score, best_move=best))

                move_color = AnalysisService._move_color_by_index(idx)
                if move_color == 'white':
                    loss = prev_eval_white - eval_score
                else:
                    loss = eval_score - prev_eval_white
                loss = max(0, loss)

                is_blunder = loss > 1.5
                is_mistake = loss > 0.8 and not is_blunder

                if is_blunder or is_mistake:
                    blunders.append({
                        'move_number': idx,
                        'move_played': move.get('notation'),
                        'fen': fen_after,
                        'loss': loss,
                        'best_move': best,
                        'category': _classify_move_phase(idx)
                    })

                prev_eval_white = eval_score

                is_white_move = (idx % 2 == 1)
                analysis_list.append({
                    'move_number': idx,
                    'move_played': move.get('notation'),
                    'evaluation': eval_score,
                    'best_move': best,
                    'fen_after': fen_after,
                    'uci': move.get('uci', ''),
                    'is_blunder': is_blunder,
                    'is_mistake': is_mistake,
                })
        finally:
            pool.engines.put(engine)

        blunders.sort(key=lambda x: x['loss'], reverse=True)
        key_mistakes = blunders[:MAX_KEY_MISTAKES]

        formatted_mistakes = []
        train_focus = []
        for km in key_mistakes:
            templates = CATEGORY_EXPLANATIONS.get(km['category'], ["Хорошая попытка!"])
            advice = random.choice(templates)
            formatted_mistakes.append({
                'move_number': km['move_number'],
                'move_played': km['move_played'],
                'best_move': km['best_move'],
                'fen': km['fen'],
                'category': km['category'],
                'evaluation_loss': km['loss'],
                'explanation': f"{advice} (Лучше было: {km['best_move']})"
            })
            train_focus.append(km['category'])

        total_moves = len(analysis_list)
        blunders_count = sum(1 for a in analysis_list if a.get('is_blunder'))
        mistakes_count = sum(1 for a in analysis_list if a.get('is_mistake'))

        db.session.commit()
        return {
            'analysis': analysis_list,
            'key_mistakes': formatted_mistakes,
            'train_focus': sorted(list(set(train_focus))) or ['tactic'],
            'total_moves': total_moves,
            'blunders_count': blunders_count,
            'mistakes_count': mistakes_count,
        }

    @staticmethod
    def analyze_pgn_text(pgn_text):
        if not pgn_text or not isinstance(pgn_text, str):
            return {'error': 'PGN не передан'}, 400

        parsed = parse_pgn(pgn_text)
        if not parsed or not parsed.get('moves'):
            return {'error': 'Не удалось распарсить PGN'}, 400

        result = AnalysisService._analyze_parsed_moves(parsed['moves'])
        return {
            'parsed_headers': parsed.get('headers', {}),
            'result': parsed.get('result'),
            'moves_count': len(parsed.get('moves', [])),
            **result
        }, 200

    @staticmethod
    def extract_pgn_from_handwritten_image(image_file):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {'error': 'OPENAI_API_KEY не настроен'}, 503

        image_bytes = image_file.read()
        if not image_bytes:
            return {'error': 'Пустой файл изображения'}, 400

        b64 = base64.b64encode(image_bytes).decode("utf-8")
        client = OpenAI(api_key=api_key)

        prompt = (
            "Это фото шахматной записи партии, возможно рукописной. "
            "Извлеки чистый PGN. Исправь очевидные OCR-ошибки (например 0-0/O-O, 1/l, лишние пробелы), "
            "но не выдумывай ходы. Верни ТОЛЬКО PGN текст."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты помощник по распознаванию шахматной нотации."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]}
            ],
            temperature=0.0,
            max_tokens=1200
        )
        text = (response.choices[0].message.content or "").strip()
        text = re.sub(r'^```(?:pgn)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return {'pgn': text}, 200

    @staticmethod
    def analyze_game(user_id, game_id):
        game = Game.query.get(game_id)
        if not game:
            return {'error': 'Игра не найдена'}, 404
        if int(user_id) not in (int(game.white_id), int(game.black_id)):
            return {'error': 'Доступ запрещён'}, 403

        if game.status != 'finished':
            return {'error': 'Анализ доступен только после завершения партии'}, 400

        Mistake.query.filter_by(user_id=user_id, game_id=game_id).delete()

        moves = game.moves.order_by(Move.move_number).all()

        from app.chess.stockfish_engine import StockfishEngine
        pool = StockfishEngine()
        engine = pool._acquire()

        analysis_list = []
        blunders = []
        prev_eval_white = 0.0

        try:
            for move in moves:
                cached = AnalysisCache.query.filter_by(fen=move.fen_after).first()

                if cached:
                    eval_score = cached.evaluation
                    best = cached.best_move
                else:
                    board = chess.Board(move.fen_after)
                    info = engine.analyse(board, chess.engine.Limit(depth=14))

                    score_obj = info['score'].white()
                    if score_obj.is_mate():
                        eval_score = 100.0 if score_obj.mate() > 0 else -100.0
                    else:
                        eval_score = score_obj.score() / 100.0

                    best = info['pv'][0].uci() if info.get('pv') else None

                    new_cache = AnalysisCache(
                        fen=move.fen_after,
                        evaluation=eval_score,
                        best_move=best
                    )
                    db.session.add(new_cache)

                move.evaluation = eval_score

                is_white_move = (move.color == 'white')
                if is_white_move:
                    loss = prev_eval_white - eval_score
                else:
                    loss = eval_score - prev_eval_white

                loss = max(0, loss)

                is_blunder = loss > 1.5
                is_mistake = loss > 0.8 and not is_blunder

                move.is_blunder = is_blunder
                move.is_mistake = is_mistake

                if is_blunder or is_mistake:
                    blunders.append({
                        'move': move,
                        'loss': loss,
                        'best_move': best,
                        'eval': eval_score,
                    })

                prev_eval_white = eval_score
                analysis_list.append({
                    'move': move.to_dict(),
                    'evaluation': eval_score,
                    'best_move': best,
                })
        finally:
            pool.engines.put(engine)

        blunders.sort(key=lambda x: x['loss'], reverse=True)
        key_mistakes = blunders[:MAX_KEY_MISTAKES]

        saved_mistakes = []
        for km in key_mistakes:
            m = km['move']
            category = _classify_move_phase(m.move_number)

            templates = CATEGORY_EXPLANATIONS.get(category, ["Хорошая попытка! В следующий раз получится лучше."])
            random_advice = random.choice(templates)

            friendly_explanation = f"{random_advice} (Лучше было пойти: {km['best_move']})"

            topic = Topic.query.filter(Topic.name.ilike(f'%{category}%')).first()

            mistake = Mistake(
                user_id=user_id,
                game_id=game_id,
                fen=m.fen_after,
                move_played=m.notation,
                best_move=km['best_move'],
                explanation=friendly_explanation,
                category=category,
                topic_id=topic.id if topic else None,
                evaluation_loss=km['loss'],
            )
            db.session.add(mistake)
            db.session.flush()

            saved_mistakes.append({
                'id': mistake.id,
                'fen': m.fen_after,
                'move_played': m.notation,
                'best_move': km['best_move'],
                'explanation': friendly_explanation,
                'category': category,
                'evaluation_loss': km['loss'],
            })

        db.session.commit()

        return {
            'analysis': analysis_list,
            'key_mistakes': saved_mistakes,
            'total_moves': len(moves),
            'blunders_count': sum(1 for m in moves if m.is_blunder),
            'mistakes_count': sum(1 for m in moves if m.is_mistake),
        }, 200


    @staticmethod
    def analyze_position(fen):
        if not fen:
            return {'error': 'FEN не указан'}, 400

        evaluation = ChessService.evaluate_position(fen)
        best_move = ChessService.get_best_move(fen)
        legal_moves = ChessService.get_legal_moves(fen)

        explanation = 'Позиция равна.'
        if evaluation is not None:
            if evaluation > 1.5:
                explanation = 'У белых значительное преимущество.'
            elif evaluation > 0.5:
                explanation = 'У белых небольшое преимущество.'
            elif evaluation < -1.5:
                explanation = 'У чёрных значительное преимущество.'
            elif evaluation < -0.5:
                explanation = 'У чёрных небольшое преимущество.'

        return {
            'fen': fen,
            'evaluation': evaluation,
            'best_move': best_move,
            'explanation': explanation,
            'legal_moves': legal_moves,
        }, 200

    @staticmethod
    def get_user_mistakes(user_id, page=1):
        pagination = Mistake.query.filter_by(
        user_id=user_id
        ).order_by(Mistake.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )

        return {
        'mistakes': [m.to_dict() for m in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
        }, 200

    @staticmethod
    def get_exercises_for_mistake(user_id, mistake_id):
        mistake = Mistake.query.get(mistake_id)
        if not mistake:
            return {'error': 'Ошибка не найдена'}, 404
        if int(mistake.user_id) != int(user_id):
            return {'error': 'Доступ запрещён'}, 403

        exercises = []
        if mistake.topic_id:
            from app.models.lesson import Lesson
            lessons = Lesson.query.filter_by(topic_id=mistake.topic_id).all()
            lesson_ids = [l.id for l in lessons]
            if lesson_ids:
                exercises = Exercise.query.filter(
                    Exercise.lesson_id.in_(lesson_ids)
                ).limit(5).all()

        if not exercises:
            exercises = Exercise.query.limit(5).all()

        return {
            'mistake': mistake.to_dict(),
            'recommended_exercises': [e.to_dict() for e in exercises],
        }, 200
