from typing import List, Optional, Tuple

class Faller:
    def __init__(self, row: int, col: int, left: str, right: str):
        """
        Initialize a new Faller.
        :param row: row index of the bottom segment
        :param col: column index of the left segment
        :param left: color of the left (or top) segment
        :param right: color of the right (or bottom) segment
        """
        self.row = row
        self.col = col
        self.left = left
        self.right = right
        self.vertical = False
        self.landed = False
        self.top:    Optional[str] = None
        self.bottom: Optional[str] = None

    def move_down(self):
        """
        Drop the faller down by one row.
        """
        self.row += 1

    def land(self):
        """
        Mark the faller as landed, so that on the next step it will freeze.
        """
        self.landed = True

    def rotate(self, clockwise: bool):
        """
        Rotate the faller 90°.
        Vertical -> horizontal: always map bottom->left and top->right.
        Horizontal -> vertical:
          - Clockwise (A): top = right, bottom = left.
          - Counterclockwise (B): top = left, bottom = right.
        """
        if clockwise:
            if self.vertical:
                self.left, self.right = self.bottom, self.top
            else:
                self.top, self.bottom = self.left, self.right
        else:
            if self.vertical:
                self.left, self.right = self.top, self.bottom
            else:
                self.top, self.bottom = self.right, self.left
        
        self.vertical = not self.vertical

    def get_positions(self) -> List[Tuple[int,int,str]]:
        """
        Return a list of the two occupied cells as (row, col, color).
        Vertical: [(row-1,col,top), (row,col,bottom)].
        Horizontal: [(row,col,left), (row,col+1,right)].
        """
        if self.vertical:
            return [(self.row - 1, self.col, self.top),
                    (self.row,     self.col, self.bottom)]
        else:
            return [(self.row, self.col,     self.left),
                    (self.row, self.col + 1, self.right)]

    def can_move(self, dr: int, dc: int, field: List[List[object]]) -> bool:
        """
        True if shifting by (dr,dc) keeps both segments in bounds
        and on empty cells.
        """
        rows, cols = len(field), len(field[0])
        for r, c, _ in self.get_positions():
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols): 
                return False
            if field[nr][nc] != ' ':
                return False
        return True

    def move_left(self, field: List[List[object]]):
        """
        Move faller left if possible; reset landed status if moved.
        """
        if self.can_move(0, -1, field):
            self.col -= 1
            self.landed = False

    def move_right(self, field: List[List[object]]):
        """
        Move faller right if possible; reset landed status if moved.
        """
        if self.can_move(0, +1, field):
            self.col += 1
            self.landed = False

    def will_land(self, field: List[List[object]]) -> bool:
        """
        Return True if the faller should land on the next tick.
        Vertical fallers land when the bottom segment is blocked
        (either out of bounds or the cell below isn't empty).
        Horizontal fallers land when either half would collide
        if moved down. They can only move down when both
        halves have empty space beneath them.
        """
        rows, cols = len(field), len(field[0])

        if self.vertical:
            # Only check the bottom cell
            bottom_r, bottom_c, _ = (self.row, self.col, self.bottom)
            nr, nc = bottom_r + 1, bottom_c
            # Land if it'd go off the bottom or hit a non-space
            if nr >= rows or field[nr][nc] != ' ':
                return True
            else:
                return False
        else:
            # Existing logic: land when either half is blocked
            return not self.can_move(1, 0, field)

class GameState:
    def __init__(self, rows: int, cols: int, contents: Optional[List[List[object]]] = None):
        """
        Initialize the game field and state.
        :param rows: number of rows
        :param cols: number of columns
        :param contents: prefilled grid (or None for empty)
        """
        self.rows = rows
        self.cols = cols
        self.field = contents if contents is not None else [[' ']*cols for _ in range(rows)]
        self.faller: Optional[Faller] = None
        self.game_over = False
        self.matched_cells = set()

    def render(self) -> List[str]:
        """
        Render the current field (with faller overlay and matches).
        Returns a list of text lines to print.
        """
        self.check_matches()  # update matched_cells

        # build a map of faller cells -> their render strings
        faller_cells = {}
        if self.faller:
            f = self.faller
            r, c = f.row, f.col
            if not f.vertical:
                # horizontal
                if f.landed:
                    faller_cells[(r, c    )] = f"|{f.left}-"
                    faller_cells[(r, c + 1)] = f"-{f.right}|"
                else:
                    faller_cells[(r, c    )] = f"[{f.left}-"
                    faller_cells[(r, c + 1)] = f"-{f.right}]"
            else:
                # vertical
                if f.landed:
                    faller_cells[(r - 1, c)] = f"|{f.top}|"
                    faller_cells[(r,     c)] = f"|{f.bottom}|"
                else:
                    faller_cells[(r - 1, c)] = f"[{f.top}]"
                    faller_cells[(r,     c)] = f"[{f.bottom}]"

        out: List[str] = []
        for r in range(self.rows):
            line = '|'
            for c in range(self.cols):
                if (r, c) in faller_cells:
                    line += faller_cells[(r, c)]
                elif (r, c) in self.matched_cells:
                    # highlight matched cells
                    val = self.field[r][c]
                    if isinstance(val, tuple):
                        val = val[0]
                    line += f"*{val}*"
                else:
                    cell = self.field[r][c]
                    if cell == ' ':
                        line += '   '
                    elif isinstance(cell, tuple):
                        color, part = cell
                        if part == 'left':
                            line += f' {color}-'
                        elif part == 'right':
                            line += f'-{color} '
                        else:
                            line += f' {color} '
                    else:
                        line += f' {cell} '
            line += '|'
            out.append(line)

        # bottom border
        out.append(' ' + '-'*(3*self.cols) + ' ')

        # LEVEL CLEARED?
        if not any((cell if isinstance(cell, str) else cell[0]) in 'rby'
                   for row in self.field for cell in row):
            out.append('LEVEL CLEARED')

        # GAME OVER?
        if self.game_over:
            out.append('GAME OVER')

        return out

    def create_faller(self, left: str, right: str) -> None:
        """
        Spawn a new capsule at the top center or end game if blocked.
        Format: "F left right"
        """
        if self.faller:
            return

        mid = (self.cols // 2) - (1 if self.cols % 2 == 0 else 0)
        # Check both the invisible top barrier (row 0) AND the actual spawn row (row 1)
        if (self.field[0][mid]   != ' '
         or self.field[0][mid+1] != ' '
         or self.field[1][mid]   != ' '
         or self.field[1][mid+1] != ' '):
            self.game_over = True
            return

        # Once all conditions are met, create a new faller
        self.faller = Faller(row=1, col=mid, left=left, right=right)

    def move_faller_left(self) -> None:
        """
        Handle the "<" command: move the faller left if possible.
        """
        if self.faller:
            self.faller.move_left(self.field)

    def move_faller_right(self) -> None:
        """
        Handle the ">" command: move the faller right if possible.
        """
        if self.faller:
            self.faller.move_right(self.field)

    def step(self) -> None:
        """
        Advance the game by one tick (blank input):
        A) Move or freeze the faller
        B) If no faller, run match/clear
        C) Then apply one-step gravity
        """
        # A) Faller logic
        if self.faller:
            if not self.faller.landed and not self.faller.will_land(self.field):
                self.faller.move_down()
            if self.faller.will_land(self.field):
                if not self.faller.landed:
                    self.faller.land()
                else:
                    # freeze both segments into the field
                    for r, c, color in self.faller.get_positions():
                        if self.faller.vertical:
                            tag = 'top' if r == self.faller.row-1 else 'bottom'
                        else:
                            tag = 'left' if c == self.faller.col else 'right'
                        self.field[r][c] = (color, tag)
                    self.faller = None
            return

        # B) Matching & clearing
        if self.matched_cells:
            self.clear_matches()
        else:
            self.check_matches()

        # C) Gravity
        #if self.faller != None and not self.faller.landed:
        self.apply_gravity()

    def rotate_faller(self, clockwise: bool) -> None:
        """
        Handle "A" (clockwise) or "B" (counterclockwise) rotation,
        including a simple wall‐kick to the left if needed.
        """
        if not self.faller:
            return
        before = self.faller.col
        self.faller.rotate(clockwise)
        pts = self.faller.get_positions()
        bad = any(
            r < 0 or r >= self.rows or c < 0 or c >= self.cols or self.field[r][c] != ' '
            for r, c, _ in pts
        )
        if bad:
            # try kicking left
            self.faller.col = before - 1
            pts = self.faller.get_positions()
            if any(r < 0 or r >= self.rows or c < 0 or c >= self.cols or self.field[r][c] != ' '
                   for r, c, _ in pts):
                # rollback
                self.faller.col = before
                self.faller.rotate(not clockwise)

    def insert_virus(self, row: int, col: int, color: str) -> None:
        """
        Handle the "V row col color" command: insert a virus (r,b,y)
        at the given cell if it’s empty.
        """
        c = color.lower()
        if c in ('r','b','y') and self.field[row][col] == ' ':
            self.field[row][col] = c

    def get_color(self, cell: object) -> str:
        """
        Helper: extract the color character from a cell,
        whether it's a string ('r',' ') or a tuple (('R','left')).
        """
        return cell[0] if isinstance(cell, tuple) else cell

    def check_matches(self) -> None:
        """
        Identify and mark any horizontal or vertical runs of 4+
        same‐color cells (case‐insensitive). Store positions in matched_cells.
        """
        marked = set()

        # horizontal
        for r in range(self.rows):
            c = 0
            while c <= self.cols - 4:
                cell = self.field[r][c]
                curr = (cell[0] if isinstance(cell, tuple) else cell).upper()
                if curr != ' ':
                    length = 1
                    while c + length < self.cols:
                        nxt = self.field[r][c + length]
                        if ((nxt[0] if isinstance(nxt, tuple) else nxt).upper() == curr):
                            length += 1
                        else:
                            break
                    if length >= 4:
                        for i in range(length):
                            marked.add((r, c + i))
                    c += length
                else:
                    c += 1

        # vertical
        for c in range(self.cols):
            r = 0
            while r <= self.rows - 4:
                cell = self.field[r][c]
                curr = (cell[0] if isinstance(cell, tuple) else cell).upper()
                if curr != ' ':
                    length = 1
                    while r + length < self.rows:
                        nxt = self.field[r + length][c]
                        if ((nxt[0] if isinstance(nxt, tuple) else nxt).upper() == curr):
                            length += 1
                        else:
                            break
                    if length >= 4:
                        for i in range(length):
                            marked.add((r + i, c))
                    r += length
                else:
                    r += 1

        self.matched_cells = marked

    def clear_matches(self) -> None:
        """
        Remove all matched cells (set them to empty) and clear the matched list.
        """
        for r, c in self.matched_cells:
            cell = self.field[r][c]

            # If we're deleting a capsule half, orphan its mate.
            if isinstance(cell, tuple):
                color, tag = cell

                # Determine partner's coordinates
                if tag in ('left', 'right'):
                    dc =  1 if tag == 'left' else -1
                    pr, pc = r, c + dc
                elif tag in ('top', 'bottom'):
                    dr =  1 if tag == 'top'  else -1
                    pr, pc = r + dr, c
                else:
                    pr = pc = None

                # If the partner is still a tuple, demote it to a single segment
                if pr is not None and 0 <= pr < self.rows and 0 <= pc < self.cols:
                    partner = self.field[pr][pc]
                    if isinstance(partner, tuple):
                        # Strip off its tag so gravity treats it as a lone segment
                        self.field[pr][pc] = partner[0]

            # Finally clear this matched cell
            self.field[r][c] = ' '

        self.matched_cells.clear()

    def apply_gravity(self) -> None:
        """
        Apply exactly one step of gravity:
        - Horizontal pairs (left+right) fall together if both below cells are empty.
        - Single segments fall one cell if the cell below is empty.
        """
        moved = set()
        for r in range(self.rows - 2, -1, -1):
            for c in range(self.cols):
                if (r, c) in moved:
                    continue
                curr = self.field[r][c]

                # Try horizontal pair first
                if isinstance(curr, tuple) and curr[1] == 'left':
                    if c + 1 < self.cols:
                        right = self.field[r][c + 1]
                        if isinstance(right, tuple) and right[1] == 'right':
                            if self.field[r + 1][c] == ' ' and self.field[r + 1][c + 1] == ' ':
                                # move both segments down
                                self.field[r + 1][c]     = curr
                                self.field[r + 1][c + 1] = right
                                self.field[r][c]         = ' '
                                self.field[r][c + 1]     = ' '
                                moved |= {(r + 1, c), (r + 1, c + 1)}
                                continue
                """
                # Otherwise, single‐segment gravity
                color = curr[0] if isinstance(curr, tuple) else curr
                if color in 'RBY' and self.field[r + 1][c] == ' ':
                    self.field[r + 1][c] = curr
                    self.field[r][c]     = ' '
                    moved.add((r + 1, c))
                """
                # Single‐segment gravity: only for things that aren't still in a horizontal capsule
                if not (isinstance(curr, tuple) and curr[1] in ('left', 'right')):
                    color = curr[0] if isinstance(curr, tuple) else curr
                    if color in 'RBY' and self.field[r + 1][c] == ' ':
                        self.field[r + 1][c] = curr
                        self.field[r][c]     = ' '
                        moved.add((r + 1, c))