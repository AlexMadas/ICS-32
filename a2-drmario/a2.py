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
            contents.append(list(line))

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

if __name__ == '__main__':
    main()