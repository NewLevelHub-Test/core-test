import chess

from app.chess.stockfish_engine import StockfishEngine


class ChessService:

    @staticmethod
    def validate_move(fen, move_uci):
        board = chess.Board(fen)
        try:
            move = chess.Move.from_uci(move_uci)
            return move in board.legal_moves
        except ValueError:
            return False

    @staticmethod
    def get_best_move(fen, bot_level=5):
        pool = StockfishEngine() 
        return pool.get_best_move(fen, bot_level)

    @staticmethod
    def evaluate_position(fen, bot_level=20):
        engine = StockfishEngine()
        return engine.evaluate(fen, bot_level=bot_level)

    @staticmethod
    def get_legal_moves(fen):
        board = chess.Board(fen)
        return [move.uci() for move in board.legal_moves]

    @staticmethod
    def is_game_over(fen):
        board = chess.Board(fen)
        return {
            'is_over': board.is_game_over(),
            'is_checkmate': board.is_checkmate(),
            'is_stalemate': board.is_stalemate(),
            'is_draw': board.is_insufficient_material() or board.is_fifty_moves(),
        }

    @staticmethod
    def apply_move(fen, move_uci):
        board = chess.Board(fen)
        move = chess.Move.from_uci(move_uci)
        if move not in board.legal_moves:
            return None
        board.push(move)
        return board.fen()
