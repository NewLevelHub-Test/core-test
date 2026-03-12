import chess


def fen_to_matrix(fen):
    board = chess.Board(fen)
    matrix = []
    for rank in range(7, -1, -1):
        row = []
        for file in range(8):
            piece = board.piece_at(chess.square(file, rank))
            row.append(piece.symbol() if piece else '.')
        matrix.append(row)
    return matrix


def matrix_to_fen(matrix):
    rows = []
    for row in matrix:
        fen_row = ''
        empty = 0
        for cell in row:
            if cell == '.':
                empty += 1
            else:
                if empty > 0:
                    fen_row += str(empty)
                    empty = 0
                fen_row += cell
        if empty > 0:
            fen_row += str(empty)
        rows.append(fen_row)
    return '/'.join(rows) + ' w KQkq - 0 1'


def flip_board(fen):
    board = chess.Board(fen)
    return board.mirror().fen()


def get_piece_count(fen):
    board = chess.Board(fen)
    counts = {}
    for piece_type in chess.PIECE_TYPES:
        for color in chess.COLORS:
            piece = chess.Piece(piece_type, color)
            count = len(board.pieces(piece_type, color))
            if count > 0:
                counts[piece.symbol()] = count
    return counts
