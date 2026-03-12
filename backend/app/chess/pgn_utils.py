import io

import chess
import chess.pgn


def parse_pgn(pgn_string):
    pgn_io = io.StringIO(pgn_string)
    game = chess.pgn.read_game(pgn_io)
    if not game:
        return None

    moves = []
    board = game.board()
    for i, move in enumerate(game.mainline_moves()):
        san = board.san(move)
        board.push(move)
        moves.append({
            'number': i + 1,
            'notation': san,
            'uci': move.uci(),
            'fen_after': board.fen(),
        })

    return {
        'headers': dict(game.headers),
        'moves': moves,
        'result': game.headers.get('Result', '*'),
    }


def moves_to_pgn(moves, headers=None):
    game = chess.pgn.Game()

    if headers:
        for key, value in headers.items():
            game.headers[key] = value

    node = game
    board = chess.Board()
    for move_data in moves:
        uci = move_data.get('uci') or move_data.get('notation')
        try:
            move = chess.Move.from_uci(uci)
        except ValueError:
            move = board.parse_san(uci)
        node = node.add_variation(move)
        board.push(move)

    return str(game)
