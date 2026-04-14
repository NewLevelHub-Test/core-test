import chess
import chess.engine
import queue
import threading
import os
import logging
import shutil

logger = logging.getLogger(__name__)

ENGINE_ACQUIRE_TIMEOUT = 10  # seconds


def _resolve_stockfish_path(path=None):
    if path:
        return path

    env_path = os.environ.get('STOCKFISH_PATH')
    if env_path and os.path.isfile(env_path):
        return env_path

    system_path = shutil.which('stockfish')
    if system_path:
        return system_path

    for candidate in ('/usr/games/stockfish', '/usr/bin/stockfish', '/usr/local/bin/stockfish'):
        if os.path.isfile(candidate):
            return candidate

    return 'stockfish'


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
        self.path = _resolve_stockfish_path(path)
        self.pool_size = 2
        self.engines = queue.Queue()
        self._healthy = False

        started = 0
        for _ in range(self.pool_size):
            try:
                engine = chess.engine.SimpleEngine.popen_uci(self.path)
                engine.configure({"Threads": 1, "Hash": 32})
                self.engines.put(engine)
                started += 1
            except Exception as e:
                logger.error("Engine start error (path=%s): %s", self.path, e)

        if started > 0:
            self._healthy = True
            logger.info("Stockfish pool ready: %d/%d engines (path=%s)", started, self.pool_size, self.path)
        else:
            logger.error("Stockfish pool EMPTY — no engines started (path=%s)", self.path)

    def _acquire(self):
        if not self._healthy:
            raise RuntimeError("Stockfish pool is not available")
        try:
            return self.engines.get(timeout=ENGINE_ACQUIRE_TIMEOUT)
        except queue.Empty:
            raise RuntimeError("Stockfish engine pool exhausted (timeout)")

    def _map_level(self, engine, bot_level):
        skill = max(0, min(20, int(bot_level)))
        engine.configure({"Skill Level": skill})

    def _limit_for_level(self, bot_level):
        lvl = int(bot_level)
        if lvl <= 3:
            return chess.engine.Limit(depth=2, time=0.05)
        elif lvl <= 6:
            return chess.engine.Limit(depth=4, time=0.1)
        elif lvl <= 12:
            return chess.engine.Limit(depth=8, time=0.4)
        elif lvl <= 17:
            return chess.engine.Limit(depth=12, time=0.8)
        else:
            return chess.engine.Limit(depth=18, time=1.5)

    def get_best_move(self, fen, bot_level=5):
        engine = self._acquire()
        try:
            board = chess.Board(fen)
            self._map_level(engine, bot_level)
            limit = self._limit_for_level(bot_level)
            result = engine.play(board, limit)
            return result.move.uci() if result.move else None
        except Exception:
            return None
        finally:
            self.engines.put(engine)

    def evaluate(self, fen, bot_level=20):
        engine = self._acquire()
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
        engine = self._acquire()
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
            self._healthy = False
            while not self.engines.empty():
                try:
                    engine = self.engines.get_nowait()
                    engine.quit()
                except Exception:
                    pass

StockfishEngine = StockfishPool