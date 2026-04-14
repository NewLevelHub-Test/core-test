from datetime import datetime
import secrets
import chess

from app import db
from app.models.game import Game
from app.models.move import Move
from app.models.user import User
from app.services.chess_service import ChessService
from app.chess.pgn_utils import moves_to_pgn


class GameService:
    @staticmethod
    def create_game(user_id, data):
        mode = data.get('mode', 'ai')
        player_color = data.get('color', 'white')

        difficulty = data.get('difficulty')
        DIFFICULTY_MAP = {1: 1, 2: 10, 3: 20}
        if difficulty and int(difficulty) in DIFFICULTY_MAP:
            bot_level = DIFFICULTY_MAP[int(difficulty)]
        else:
            bot_level = data.get('bot_level', 5)

        time_control = data.get('time_control') or data.get('time_limit')

        bot_user = User.query.filter_by(username="ChessBot").first()
        
        if not bot_user:
            bot_user = User(
                username="ChessBot", 
                email="bot@system.chess",
                role="bot",
                elo_rating=1500
            )

            bot_user.set_password(secrets.token_hex(24))
            
            db.session.add(bot_user)
            db.session.commit()

        bot_id = bot_user.id

        if player_color == 'white':
            white_id = user_id
            black_id = bot_id
        else:
            white_id = bot_id
            black_id = user_id

        game = Game(
            white_id=white_id,
            black_id=black_id,
            mode=mode,
            player_color=player_color,
            bot_level=bot_level,
            time_control=int(time_control) if time_control else None,
            status='in_progress',
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        
        db.session.add(game)
        db.session.commit()

        result = {'game': game.to_dict()}

        if mode == 'ai' and player_color == 'black':
            ai_result, _ = GameService._ai_move(game)
            if ai_result:
                result['ai_move'] = ai_result
                db.session.commit() 

        return result, 201

    @staticmethod
    def get_game(user_id, game_id):
        game = Game.query.get(game_id)
        if not game:
            return {'error': 'Игра не найдена'}, 404
        if int(user_id) not in (int(game.white_id), int(game.black_id)):
            return {'error': 'Доступ запрещён'}, 403

        moves = [m.to_dict() for m in game.moves.order_by(Move.move_number).all()]
        return {'game': game.to_dict(), 'moves': moves}, 200

    @staticmethod
    def make_move(user_id, game_id, data):
        game = Game.query.get(game_id)
        if not game:
            return {'error': 'Игра не найдена'}, 404

        if game.status != 'in_progress':
            return {'error': 'Игра уже завершена'}, 400
        if int(user_id) not in (int(game.white_id), int(game.black_id)):
            return {'error': 'Вы не участник этой партии'}, 403

        move_uci = data.get('move')
        if not ChessService.validate_move(game.fen, move_uci):
            return {'error': 'Недопустимый ход'}, 400

        new_fen = ChessService.apply_move(game.fen, move_uci)
        move_number = game.moves.count() + 1

        board = chess.Board(game.fen)
        san = board.san(chess.Move.from_uci(move_uci))

        move = Move(
            game_id=game_id,
            move_number=move_number,
            notation=san,
            fen_after=new_fen,
            color='white' if board.turn == chess.WHITE else 'black',
        )
        db.session.add(move)
        game.fen = new_fen

        game_over = ChessService.is_game_over(new_fen)
        if game_over['is_over']:
            GameService._finish_game(game, game_over, move_number)

        ai_move_data = None
        if game.mode == 'ai' and game.status == 'in_progress':
            ai_move_data, _ = GameService._ai_move(game)

        db.session.commit()

        result = {
            'move': move.to_dict(),
            'fen': game.fen,
            'status': game.status,
            'result': game.result,
        }
        if ai_move_data:
            result['ai_move'] = ai_move_data

        return result, 200

    @staticmethod
    def _ai_move(game):
        best = ChessService.get_best_move(game.fen, bot_level=game.bot_level)
        if not best:
            return None, 200

        ai_fen = ChessService.apply_move(game.fen, best)
        board = chess.Board(game.fen)
        san = board.san(chess.Move.from_uci(best))
        move_number = game.moves.count() + 1

        ai_move = Move(
            game_id=game.id,
            move_number=move_number,
            notation=san,
            fen_after=ai_fen,
            color='white' if board.turn == chess.WHITE else 'black',
        )
        db.session.add(ai_move)
        game.fen = ai_fen

        game_over = ChessService.is_game_over(ai_fen)
        if game_over['is_over']:
            GameService._finish_game(game, game_over, move_number)

        return ai_move.to_dict(), 200

    @staticmethod
    def _finish_game(game, game_over, last_move_number=None):
        game.status = 'finished'
        game.finished_at = datetime.utcnow()

        
        if game_over.get('is_resign') or game_over.get('is_timeout'):
            winner_id = game_over['winner_id']
            game.result = '1-0' if winner_id == game.white_id else '0-1'
        elif game_over.get('is_checkmate'):
            board = chess.Board(game.fen)
            game.result = '0-1' if board.turn == chess.WHITE else '1-0'
        elif game_over.get('is_draw') or game_over.get('is_stalemate'):
            game.result = '1/2-1/2'
        else:
            game.result = '1/2-1/2'

       
        moves = game.moves.order_by(Move.move_number).all()
        white_user = User.query.get(game.white_id)
        black_user = User.query.get(game.black_id) if game.black_id else None

        headers = {
            'Event': 'Шахматная платформа - Партия',
            'Date': game.created_at.strftime('%Y.%m.%d'),
            'White': white_user.username if white_user else 'Игрок 1',
            'Black': black_user.username if black_user else f'Бот (Уровень {game.bot_level})',
            'Result': game.result,
        }

        move_data = [{'notation': m.notation} for m in moves]
        game.pgn = moves_to_pgn(move_data, headers)

        # Обновление ЭЛО
        from app.utils.helpers import elo_update

        if game.mode == 'ai':
            is_white_player = (game.player_color == 'white')
            player_user = white_user if is_white_player else black_user

            if player_user:
                if game.result == '1/2-1/2':
                    player_score = 0.5
                elif (game.result == '1-0' and is_white_player) or (game.result == '0-1' and not is_white_player):
                    player_score = 1.0
                else:
                    player_score = 0.0

                ai_rating = 600 + (game.bot_level * 100)
                new_player_elo, _ = elo_update(player_user.elo_rating, ai_rating, player_score)
                player_user.elo_rating = new_player_elo

        elif game.mode == 'pvp' and white_user and black_user:
            score_white = 1.0 if game.result == '1-0' else (0.0 if game.result == '0-1' else 0.5)
            new_w, new_b = elo_update(white_user.elo_rating, black_user.elo_rating, score_white)
            white_user.elo_rating = new_w
            black_user.elo_rating = new_b

    @staticmethod
    def resign(user_id, game_id):
        game = Game.query.get(game_id)
        if not game or game.status != 'in_progress':
            return {'error': 'Игра не найдена или уже завершена'}, 400
        if int(user_id) not in (int(game.white_id), int(game.black_id)):
            return {'error': 'Вы не участник этой партии'}, 403

 
        loser_id = user_id
        winner_id = game.white_id if user_id == game.black_id else game.black_id

        
        GameService._finish_game(game, {'is_resign': True, 'winner_id': winner_id})
        db.session.commit()

        return {'game': game.to_dict()}, 200

    @staticmethod
    def timeout_loss(user_id, game_id):
        game = Game.query.get(game_id)
        if not game or game.status != 'in_progress':
            return {'error': 'Игра не найдена или уже завершена'}, 400
        if int(user_id) not in (int(game.white_id), int(game.black_id)):
            return {'error': 'Вы не участник этой партии'}, 403

        winner_id = game.white_id if int(user_id) == int(game.black_id) else game.black_id
        GameService._finish_game(game, {'is_timeout': True, 'winner_id': winner_id})
        db.session.commit()
        return {'game': game.to_dict()}, 200

    @staticmethod
    def get_user_games(user_id, page=1):
        pagination = Game.query.filter(
            ((Game.white_id == user_id) | (Game.black_id == user_id)) &
            (Game.status == 'finished')
        ).order_by(Game.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

        return {
            'games': [g.to_dict() for g in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
        }, 200

    @staticmethod
    def get_game_moves(user_id, game_id):
        game = Game.query.get(game_id)
        if not game:
            return {'error': 'Игра не найдена'}, 404
        if int(user_id) not in (int(game.white_id), int(game.black_id)):
            return {'error': 'Доступ запрещён'}, 403

        moves = game.moves.order_by(Move.move_number).all()
        return {'moves': [m.to_dict() for m in moves]}, 200

    @staticmethod
    def export_pgn(user_id, game_id):
        game = Game.query.get(game_id)
        if not game:
            return {'error': 'Игра не найдена'}, 404
        if int(user_id) not in (int(game.white_id), int(game.black_id)):
            return {'error': 'Доступ запрещён'}, 403

        moves = game.moves.order_by(Move.move_number).all()

        white = User.query.get(game.white_id)
        black = User.query.get(game.black_id) if game.black_id else None

        headers = {
            'Event': 'Шахматная платформа',
            'Date': game.created_at.strftime('%Y.%m.%d'),
            'White': white.username if white else 'Bot',
            'Black': black.username if black else 'Bot',
            'Result': game.result or '*',
        }

        move_data = [{'notation': m.notation} for m in moves]
        pgn_str = moves_to_pgn(move_data, headers)

        return {'pgn': pgn_str}, 200