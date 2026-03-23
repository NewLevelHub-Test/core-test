import chess
import chess.engine
import queue
import threading
import os

class StockfishPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, path=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StockfishPool, cls).__new__(cls)
                cls._instance._init_pool(path)
        return cls._instance

    def _init_pool(self, path=None):
        if not path:
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            backend_root = os.path.abspath(os.path.join(current_file_dir, "..", ".."))
            self.path = os.path.join(backend_root, 'bin', 'stockfish.exe')
        else:
            self.path = path
        
        self.pool_size = 4
        self.engines = queue.Queue()

        for _ in range(self.pool_size):
            try:
                engine = chess.engine.SimpleEngine.popen_uci(self.path)
                self.engines.put(engine)
            except Exception as e:
                print(f"Engine start error: {e}")

    def _map_level(self, engine, bot_level):
        skill = max(0, min(20, int(bot_level)))
        engine.configure({"Skill Level": skill})

    def get_best_move(self, fen, bot_level=5):
        engine = self.engines.get()
        try:
            board = chess.Board(fen)
            self._map_level(engine, bot_level)
            result = engine.play(board, chess.engine.Limit(time=0.1))
            return result.move.uci() if result.move else None
        except Exception:
            return None
        finally:
            self.engines.put(engine)

    def evaluate(self, fen, bot_level=20):
        engine = self.engines.get()
        try:
            board = chess.Board(fen)
            self._map_level(engine, bot_level)
            info = engine.analyse(board, chess.engine.Limit(time=0.1))
            score = info['score'].relative
            if score.is_mate():
                return 100.0 if score.mate() > 0 else -100.0
            return score.score() / 100.0
        except Exception:
            return None
        finally:
            self.engines.put(engine)

    def get_top_moves(self, fen, count=3, bot_level=20):
        engine = self.engines.get()
        try:
            board = chess.Board(fen)
            self._map_level(engine, bot_level)
            results = engine.analyse(board, chess.engine.Limit(time=0.1), multipv=count)
            moves = []
            for info in results:
                move = info['pv'][0].uci() if info.get('pv') else None
                score = info['score'].relative
                cp = score.score() / 100.0 if not score.is_mate() else (100 if score.mate() > 0 else -100)
                moves.append({'move': move, 'evaluation': cp})
            return moves
        except Exception:
            return []
        finally:
            self.engines.put(engine)

    def shutdown(self):
        with self._lock:
            while not self.engines.empty():
                try:
                    engine = self.engines.get_nowait()
                    engine.quit()
                except:
                    pass

StockfishEngine = StockfishPool