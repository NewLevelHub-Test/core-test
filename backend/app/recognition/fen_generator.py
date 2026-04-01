class FenGenerator:
    @staticmethod
    def generate(grid):
        fen_rows = []
        for row in grid:
            empty = 0
            row_str = ""
            for cell in row:
                if cell == '.':
                    empty += 1
                else:
                    if empty > 0:
                        row_str += str(empty)
                        empty = 0
                    row_str += cell
            if empty > 0:
                row_str += str(empty)
            fen_rows.append(row_str)
        # Возвращаем стандартную FEN строку
        return "/".join(fen_rows) + " w KQkq - 0 1"

    @staticmethod
    def validate(fen):
        return len(fen) > 15