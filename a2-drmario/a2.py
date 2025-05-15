from game import GameState

def main():
    rows = int(input())
    cols = int(input())
    contents = []

    init_mode = input().strip()
    if init_mode == 'EMPTY':
        contents = [[' ' for _ in range(cols)] for _ in range(rows)]
    elif init_mode == 'CONTENTS':
        for _ in range(rows):
            line = input()
            # Ensure exactly `cols` characters: pad with spaces or truncate
            if len(line) < cols:
                line = line.ljust(cols)
            else:
                line = line[:cols]

            row = []
            for char in line:
                if char in 'RBY':
                    row.append((char, 'single'))  # Tag capsule halves
                else:
                    row.append(char)               # Virus ('r','b','y') or empty ' '
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