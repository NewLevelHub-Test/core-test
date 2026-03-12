import chess
import chess.engine

from flask import current_app


class StockfishEngine:

    def __init__(self):
        self.path = current_app.config.get('STOCKFISH_PATH', '/usr/local/bin/stockfish')

    def get_best_move(self, fen, depth=15):
        board = chess.Board(fen)
        try:
            with chess.engine.SimpleEngine.popen_uci(self.path) as engine:
                result = engine.play(board, chess.engine.Limit(depth=depth))
                return result.move.uci() if result.move else None
        except Exception:
            return None

    def evaluate(self, fen, depth=15):
        board = chess.Board(fen)
        try:
            with chess.engine.SimpleEngine.popen_uci(self.path) as engine:
                info = engine.analyse(board, chess.engine.Limit(depth=depth))
                score = info['score'].relative
                if score.is_mate():
                    return 100.0 if score.mate() > 0 else -100.0
                return score.score() / 100.0
        except Exception:
            return None

    def get_top_moves(self, fen, count=3, depth=15):
        board = chess.Board(fen)
        try:
            with chess.engine.SimpleEngine.popen_uci(self.path) as engine:
                results = engine.analyse(
                    board,
                    chess.engine.Limit(depth=depth),
                    multipv=count,
                )
                moves = []
                for info in results:
                    move = info['pv'][0].uci() if info.get('pv') else None
                    score = info['score'].relative
                    cp = score.score() / 100.0 if not score.is_mate() else (100 if score.mate() > 0 else -100)
                    moves.append({'move': move, 'evaluation': cp})
                return moves
        except Exception:
            return []
