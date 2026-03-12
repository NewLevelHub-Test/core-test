class FenGenerator:

    @staticmethod
    def generate(grid):
        rows = []
        for rank in grid:
            fen_row = ''
            empty = 0
            for cell in rank:
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

        position = '/'.join(rows)
        return f'{position} w KQkq - 0 1'

    @staticmethod
    def validate(fen):
        parts = fen.split()
        if len(parts) != 6:
            return False

        ranks = parts[0].split('/')
        if len(ranks) != 8:
            return False

        for rank in ranks:
            count = 0
            for ch in rank:
                if ch.isdigit():
                    count += int(ch)
                elif ch.lower() in 'kqrbnp':
                    count += 1
                else:
                    return False
            if count != 8:
                return False

        return True
