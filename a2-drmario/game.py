from typing import List, Optional

class GameState:
    def __init__(self, rows, cols, contents=None):
        """
        Initialize the game field.
        :param rows: Number of rows in the field.
        :param cols: Number of columns in the field.
        :param contents: Initial field contents, or None for empty.
        """
        self.rows = rows
        self.cols = cols
        self.field = contents if contents else [[' ' for _ in range(cols)] for _ in range(rows)]
        self.faller = None
        self.game_over = False

    def render(self) -> List[str]:
        result = []
        faller_cells = {}
        if self.faller:
            row, col = self.faller['row'], self.faller['col']
            if self.faller['landed']:
                faller_cells[(row, col)] = f"|{self.faller['left']}"
                faller_cells[(row, col + 1)] = f"--{self.faller['right']}|"
            else:
                faller_cells[(row, col)] = f"[{self.faller['left']}"
                faller_cells[(row, col + 1)] = f"--{self.faller['right']}]"

        for r, row in enumerate(self.field):
            line = '|'
            for c, cell in enumerate(row):
                if (r, c) in faller_cells:
                    line += faller_cells[(r, c)]
                elif cell == ' ':
                    line += '   '
                elif cell in 'RBY':
                    line += f' {cell} '
                elif cell in 'rby':
                    line += f' {cell} '
                else:
                    line += ' ? '  # unexpected, for debugging
            line += '|'
            result.append(line)

        result.append(' ' + '-' * (3 * self.cols) + ' ')
        if not any(cell in 'rby' for row in self.field for cell in row):
            result.append('LEVEL CLEARED')
        if self.game_over:
            result.append('GAME OVER')
        return result
    
    def create_faller(self, left: str, right: str) -> None:
        """
        Creates a new horizontal faller with given left and right colors.
        Placed on the second row, centered in the field.
        """
        if self.faller is not None:
            return  # A faller already exists

        mid = self.cols // 2
        if self.cols % 2 == 0:
            mid -= 1  # Use the left-middle cell for even columns

        # Check for GAME OVER condition
        if self.field[0][mid] != ' ' or self.field[0][mid + 1] != ' ':
            self.game_over = True
            return

        self.faller = {
            'row': 1,           # second row (0-indexed)
            'col': mid,         # left segment goes here
            'left': left,
            'right': right,
            'landed': False
        }

    def step(self):
        """
        Handle time passing: move faller down, land it, or freeze it.
        """
        if not self.faller:
            return  # Nothing to update

        row = self.faller['row']
        col = self.faller['col']

        # Check if next row is available and empty
        if row + 1 >= self.rows or self.field[row + 1][col] != ' ' or self.field[row + 1][col + 1] != ' ':
            if self.faller['landed']:
                # Freeze faller into the grid
                self.field[row][col] = self.faller['left']
                self.field[row][col + 1] = self.faller['right']
                self.faller = None
            else:
                # Mark as landed
                self.faller['landed'] = True
        else:
            # Move faller down
            self.faller['row'] += 1