from app import db
from app.models.game import Game
from app.models.move import Move
from app.models.mistake import Mistake
from app.models.exercise import Exercise
from app.models.topic import Topic
from app.services.chess_service import ChessService

MAX_KEY_MISTAKES = 3

CATEGORY_EXPLANATIONS = {
    'opening': 'Ошибка в дебюте — попробуй запомнить основные принципы начала партии.',
    'tactic': 'Ты пропустил тактический приём. Решай больше задач на тактику!',
    'positional': 'Позиционная ошибка — обрати внимание на расположение фигур.',
    'endgame': 'Ошибка в эндшпиле — повтори основные окончания.',
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
    def analyze_game(user_id, game_id):
        game = Game.query.get(game_id)
        if not game:
            return {'error': 'Игра не найдена'}, 404

        if game.status != 'finished':
            return {'error': 'Анализ доступен только после завершения партии'}, 400

        moves = game.moves.order_by(Move.move_number).all()

        analysis = []
        blunders = []

        prev_eval = 0.0
        for move in moves:
            eval_score = ChessService.evaluate_position(move.fen_after)
            best = ChessService.get_best_move(move.fen_after)

            if eval_score is not None:
                move.evaluation = eval_score
                loss = abs(eval_score - prev_eval)

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

                prev_eval = eval_score

            analysis.append({
                'move': move.to_dict(),
                'evaluation': eval_score,
                'best_move': best,
            })

        blunders.sort(key=lambda x: x['loss'], reverse=True)
        key_mistakes = blunders[:MAX_KEY_MISTAKES]

        saved_mistakes = []
        for km in key_mistakes:
            m = km['move']
            category = _classify_move_phase(m.move_number)
            explanation = CATEGORY_EXPLANATIONS.get(category, '')

            topic = Topic.query.filter(
                Topic.name.ilike(f'%{category}%')
            ).first()

            mistake = Mistake(
                user_id=user_id,
                game_id=game_id,
                fen=m.fen_after,
                move_played=m.notation,
                best_move=km['best_move'],
                explanation=f'Лучший ход: {km["best_move"]}. {explanation}',
                category=category,
                topic_id=topic.id if topic else None,
                evaluation_loss=km['loss'],
            )
            db.session.add(mistake)
            saved_mistakes.append({
                'fen': m.fen_after,
                'move_played': m.notation,
                'best_move': km['best_move'],
                'explanation': mistake.explanation,
                'category': category,
                'evaluation_loss': km['loss'],
            })

        db.session.commit()

        return {
            'analysis': analysis,
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
    def get_user_mistakes(user_id):
        mistakes = Mistake.query.filter_by(
            user_id=user_id
        ).order_by(Mistake.created_at.desc()).all()

        return {'mistakes': [m.to_dict() for m in mistakes]}, 200

    @staticmethod
    def get_exercises_for_mistake(mistake_id):
        mistake = Mistake.query.get(mistake_id)
        if not mistake:
            return {'error': 'Ошибка не найдена'}, 404

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
            exercises = Exercise.query.filter_by(
                difficulty=mistake.category or 'beginner'
            ).limit(5).all()

        return {
            'mistake': mistake.to_dict(),
            'recommended_exercises': [e.to_dict() for e in exercises],
        }, 200
