# Starter code for assignment 1 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Alex Madas
# Madasa@uci.edu
# 39847840

import sys
from pathlib import Path
from command_parser import parse_command
from notebook import Notebook, Diary, NotebookFileError, IncorrectNotebookError

def main():
    current_notebook = None
    current_path = None

    while True:
        input_str = input("").strip()
        if not input_str:
            continue
        if input_str.upper() == 'Q':
            break

        parsed = parse_command(input_str)
        if not parsed:
            print("INPUT ERROR")
            continue

        command = parsed['command']

        if command == 'C':
            new_nb, new_path, output = command_c(
                parsed, current_notebook, current_path
            )
            print(output)
            current_notebook = new_nb
            current_path = new_path

        else:
            print("COMMAND ERROR")

def command_c(parsed, current_notebook, current_path):
    args = parsed['args']
    options = parsed['options']
    
    if len(args) != 1 or '-n' not in options or not options['-n']:
        return current_notebook, current_path, "CREATION ERROR"
    
    dir_path = Path(args[0])
    diary_name = options['-n']
    full_path = dir_path / f"{diary_name}.json"

    if not dir_path.exists() or not dir_path.is_dir():
        print("DIRECTORY ERROR")
    if full_path.exists():
        print("FILE ALREADY EXISTS")

    try:
        username = input("").strip()
        password = input("").strip()
        bio = input("").strip()
    except:
        return current_notebook, current_path, "CREDENTIAL ERROR"

    try:
        new_notebook = Notebook(username, password, bio)
        new_notebook.save(full_path)
        return new_notebook, full_path, f"{full_path.absolute()} CREATED"
    except:
        return current_notebook, current_path, "PATH ERROR"

def command_d():
    pass

def command_o():
    pass

def command_e():
    pass

def command_p():
    pass

if __name__ == "__main__":
    main()