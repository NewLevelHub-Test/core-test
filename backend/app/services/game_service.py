from datetime import datetime

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
        bot_level = data.get('bot_level', 5)
        time_control = data.get('time_control')

        if player_color == 'white':
            white_id = user_id
            black_id = data.get('opponent_id')
        else:
            white_id = data.get('opponent_id') or 0  # 0 = bot
            black_id = user_id

        game = Game(
            white_id=white_id,
            black_id=black_id,
            mode=mode,
            player_color=player_color,
            bot_level=bot_level,
            time_control=time_control,
        )
        db.session.add(game)
        db.session.commit()

        result = {'game': game.to_dict()}

        if mode == 'ai' and player_color == 'black':
            ai_result, _ = GameService._ai_move(game)
            if ai_result:
                result['ai_move'] = ai_result

        return result, 201

    @staticmethod
    def get_game(game_id):
        game = Game.query.get(game_id)
        if not game:
            return {'error': 'Игра не найдена'}, 404

        moves = [m.to_dict() for m in game.moves.all()]
        return {'game': game.to_dict(), 'moves': moves}, 200

    @staticmethod
    def make_move(user_id, game_id, data):
        game = Game.query.get(game_id)
        if not game:
            return {'error': 'Игра не найдена'}, 404

        if game.status != 'in_progress':
            return {'error': 'Игра уже завершена'}, 400

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
        best = ChessService.get_best_move(game.fen, depth=game.bot_level)
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
    def _finish_game(game, game_over, last_move_number):
        game.status = 'finished'
        game.finished_at = datetime.utcnow()
        if game_over['is_checkmate']:
            game.result = '1-0' if last_move_number % 2 == 1 else '0-1'
        else:
            game.result = '1/2-1/2'

    @staticmethod
    def resign(user_id, game_id):
        game = Game.query.get(game_id)
        if not game:
            return {'error': 'Игра не найдена'}, 404

        game.status = 'finished'
        game.finished_at = datetime.utcnow()
        game.result = '0-1' if game.white_id == user_id else '1-0'
        db.session.commit()

        return {'game': game.to_dict()}, 200

    @staticmethod
    def get_user_games(user_id, page=1):
        pagination = Game.query.filter(
            (Game.white_id == user_id) | (Game.black_id == user_id)
        ).order_by(Game.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

        return {
            'games': [g.to_dict() for g in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
        }, 200

    @staticmethod
    def get_game_moves(game_id):
        game = Game.query.get(game_id)
        if not game:
            return {'error': 'Игра не найдена'}, 404

        moves = game.moves.order_by(Move.move_number).all()
        return {'moves': [m.to_dict() for m in moves]}, 200

    @staticmethod
    def export_pgn(game_id):
        game = Game.query.get(game_id)
        if not game:
            return {'error': 'Игра не найдена'}, 404

        moves = game.moves.order_by(Move.move_number).all()

        white = User.query.get(game.white_id)
        black = User.query.get(game.black_id) if game.black_id else None

        headers = {
            'Event': 'Chess Learning Platform',
            'Date': game.created_at.strftime('%Y.%m.%d'),
            'White': white.username if white else 'Bot',
            'Black': black.username if black else 'Bot',
            'Result': game.result or '*',
        }

        move_data = [{'notation': m.notation} for m in moves]
        pgn_str = moves_to_pgn(move_data, headers)

        return {'pgn': pgn_str}, 200
