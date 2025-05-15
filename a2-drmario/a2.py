from game import GameState

def main():
    # 1) Read rows (must be integer ≥4)
    while True:
        raw = input().strip()
        try:
            rows = int(raw)
            if rows < 4:
                print("Rows must be at least 4.")
                continue
            break
        except ValueError:
            print(f"‘{raw}’ is not a valid integer. Please enter a number.")

    # 2) Read cols (must be integer ≥3)
    while True:
        raw = input().strip()
        try:
            cols = int(raw)
            if cols < 3:
                print("Columns must be at least 3.")
                continue
            break
        except ValueError:
            print(f"‘{raw}’ is not a valid integer. Please enter a number.")

    # 3) Read init_mode (must be EMPTY or CONTENTS)
    while True:
        init_mode = input().strip().upper()
        if init_mode in ('EMPTY', 'CONTENTS'):
            break
        print("Invalid mode. Please type either EMPTY or CONTENTS.")

    # 4) Build the contents array as before
    contents = []
    if init_mode == 'EMPTY':
        contents = [[' ' for _ in range(cols)] for _ in range(rows)]
    else:  # CONTENTS
        for _ in range(rows):
            line = input()
            if len(line) < cols:
                line = line.ljust(cols)
            else:
                line = line[:cols]
            row = [(ch, 'single') if ch in 'RBY' else ch for ch in line]
            contents.append(row)

    game = GameState(rows, cols, contents)

    while True:
        for line in game.render():
            print(line)
        cmd = input().strip()
        if cmd == 'Q':
            break
        elif cmd.startswith('F '):
            parts = cmd.split()
            if len(parts) == 3:
                _, c1, c2 = parts
                game.create_faller(c1, c2)
        elif cmd == '':
            game.step()
        elif cmd == 'A':
            game.rotate_faller(clockwise=True)
        elif cmd == 'B':
            game.rotate_faller(clockwise=False)
        elif cmd == '<':
            game.move_faller_left()
        elif cmd == '>':
            game.move_faller_right()
        elif cmd.startswith('V '):
            parts = cmd.split()
            if len(parts) == 4:
                _, r_str, c_str, color = parts
                try:
                    row = int(r_str)
                    col = int(c_str)
                    game.insert_virus(row, col, color)
                except ValueError:
                    pass  # Ignore invalid numbers
        else:
            pass       
        if game.game_over:
            for line in game.render():
                print(line)
            return


if __name__ == '__main__':
    main()