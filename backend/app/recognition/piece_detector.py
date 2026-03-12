import cv2
import numpy as np


class PieceDetector:
    """
    Detects chess pieces on a board image.
    Splits the board into 8x8 cells and classifies each cell.
    """

    PIECE_MAP = {
        'white_king': 'K', 'white_queen': 'Q', 'white_rook': 'R',
        'white_bishop': 'B', 'white_knight': 'N', 'white_pawn': 'P',
        'black_king': 'k', 'black_queen': 'q', 'black_rook': 'r',
        'black_bishop': 'b', 'black_knight': 'n', 'black_pawn': 'p',
        'empty': '.',
    }

    @staticmethod
    def detect(board_image):
        h, w = board_image.shape[:2]
        cell_h, cell_w = h // 8, w // 8

        grid = []
        for row in range(8):
            rank = []
            for col in range(8):
                x1, y1 = col * cell_w, row * cell_h
                x2, y2 = x1 + cell_w, y1 + cell_h
                cell = board_image[y1:y2, x1:x2]
                piece = PieceDetector._classify_cell(cell, row, col)
                rank.append(piece)
            grid.append(rank)

        return grid

    @staticmethod
    def _classify_cell(cell, row, col):
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        mean_val = np.mean(gray)
        std_val = np.std(gray)

        is_light_square = (row + col) % 2 == 0
        base = 180 if is_light_square else 120

        if std_val < 15:
            return '.'

        if mean_val > base + 30:
            return 'P'
        elif mean_val < base - 30:
            return 'p'

        return '.'
