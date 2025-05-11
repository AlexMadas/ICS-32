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
        self.matched_cells = set()

    def render(self) -> List[str]:
        result = []
        faller_cells = {}
        if self.faller:
            row, col = self.faller['row'], self.faller['col']
            if self.faller.get('vertical'):
                top = self.faller.get('top')
                bottom = self.faller.get('bottom')
                if row - 1 >= 0:
                    if self.faller['landed']:
                        faller_cells[(row - 1, col)] = f"|{top}|"
                        faller_cells[(row, col)] = f"|{bottom}|"
                    else:
                        faller_cells[(row - 1, col)] = f"[{top}]"
                        faller_cells[(row, col)] = f"[{bottom}]"
            else:
                if self.faller['landed']:
                    faller_cells[(row, col)] = f"|{self.faller['left']}"
                    faller_cells[(row, col + 1)] = f"--{self.faller['right']}|"
                else:
                    faller_cells[(row, col)] = f"[{self.faller['left']}"
                    faller_cells[(row, col + 1)] = f"--{self.faller['right']}]"

        for r, row in enumerate(self.field):
            line = '|'
            for c, cell in enumerate(row):
                if (r, c) in self.matched_cells:
                    line += f"*{self.field[r][c]}*"
                    continue
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
            'landed': False,
            'vertical': False   # Default: horizontal
        }

    def step(self) -> None:
        """
        Progress one frame of game logic:
        - Move faller (if any)
        - Freeze faller (if landed)
        - Detect and show matches
        - Clear matched cells on next step
        """
        if self.faller:
            row = self.faller['row']
            col = self.faller['col']

            # Check if the faller can move down
            blocked = (
                row + 1 >= self.rows or
                self.field[row + 1][col] != ' ' or
                (not self.faller.get('vertical') and self.field[row + 1][col + 1] != ' ')
            )

            if blocked:
                if self.faller['landed']:
                    # Freeze into the field
                    if self.faller.get('vertical'):
                        self.field[row - 1][col] = self.faller['top']
                        self.field[row][col] = self.faller['bottom']
                    else:
                        self.field[row][col] = self.faller['left']
                        self.field[row][col + 1] = self.faller['right']
                    self.faller = None
                else:
                    self.faller['landed'] = True
            else:
                self.faller['row'] += 1

            return  # Exit now, no matching yet


        # Handle match-clearing cycle
        if self.matched_cells:
            self.clear_matches()
            self.apply_gravity()
            return  # allow field to show cleared state before rechecking

        self.check_matches()


    def rotate_faller(self, clockwise: bool) -> None:
        """
        Rotate the faller 90 degrees.
        A = clockwise, B = counterclockwise
        """
        if not self.faller:
            return

        row = self.faller['row']
        col = self.faller['col']
        left = self.faller['left']
        right = self.faller['right']

        if self.faller.get('vertical'):
            # Vertical → rotate to horizontal
            new_col = col
            if col + 1 >= self.cols or self.field[row][col + 1] != ' ':
                # Wall kick to left if possible
                if col - 1 >= 0 and self.field[row][col - 1] == ' ':
                    new_col = col - 1
                else:
                    return  # Cannot rotate
            self.faller['col'] = new_col
            if clockwise:
                self.faller['left'], self.faller['right'] = self.faller['right'], self.faller['left']
            self.faller['vertical'] = False

        else:
            # Horizontal → rotate to vertical
            if row - 1 < 0 or self.field[row - 1][col] != ' ':
                return  # No space above
            self.faller['vertical'] = True
            if clockwise:
                self.faller['top'] = self.faller['right']
                self.faller['bottom'] = self.faller['left']
            else:
                self.faller['top'] = self.faller['left']
                self.faller['bottom'] = self.faller['right']

    def insert_virus(self, row: int, col: int, color: str) -> None:
        """
        Insert a virus (r, b, y) at a specific cell, if empty.
        """
        color = color.lower()
        if color not in ('r', 'b', 'y'):
            return  # Invalid color input
        if self.field[row][col] == ' ':
            self.field[row][col] = color

    def check_matches(self) -> None:
        """
        Identify and mark matches of 4+ same-color cells.
        """
        marked = set()

        # Horizontal
        for r in range(self.rows):
            c = 0
            while c <= self.cols - 4:
                current = self.field[r][c]
                if current != ' ':
                    same = 1
                    while c + same < self.cols and self.field[r][c + same] == current:
                        same += 1
                    if same >= 4:
                        for i in range(same):
                            marked.add((r, c + i))
                    c += same
                else:
                    c += 1

        # Vertical
        for c in range(self.cols):
            r = 0
            while r <= self.rows - 4:
                current = self.field[r][c]
                if current != ' ':
                    same = 1
                    while r + same < self.rows and self.field[r + same][c] == current:
                        same += 1
                    if same >= 4:
                        for i in range(same):
                            marked.add((r + i, c))
                    r += same
                else:
                    r += 1

        self.matched_cells = marked

    def clear_matches(self) -> None:
        """
        Clear all matched cells from the field.
        """
        for r, c in self.matched_cells:
            self.field[r][c] = ' '
        self.matched_cells.clear()

    def apply_gravity(self) -> None:
        """
        Apply gravity to vitamin capsule segments after clearing.
        Only R, Y, B fall — viruses stay in place.
        """
        for c in range(self.cols):
            for r in range(self.rows - 2, -1, -1):  # Bottom-up
                current = self.field[r][c]
                if current in 'RBY':
                    row_below = r
                    while (row_below + 1 < self.rows) and self.field[row_below + 1][c] == ' ':
                        row_below += 1
                    if row_below != r:
                        self.field[row_below][c] = current
                        self.field[r][c] = ' '