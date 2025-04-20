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

        elif command == 'D':
            output = command_d(parsed)
            print(output)
        
        elif command == 'O':
            new_nb, new_path, output = command_o(parsed)
            print(output)
            if "Notebook loaded." in output:
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

def command_d(parsed):
    args = parsed.get('args', [])
    
    if len(args) != 1:
        return "ERROR"
    
    target_path = Path(args[0])
    
    if (
        not target_path.exists() or
        not target_path.is_file() or
        target_path.suffix != '.json'
    ):
        return "ERROR"
    
    try:
        absolute_path = target_path.absolute()
        target_path.unlink()
        return f"{absolute_path} DELETED"
    except:
        return "ERROR"

def command_o(parsed):
    args = parsed.get('args', [])
    
    if len(args) != 1:
        return None, None, "ERROR"
    
    path = Path(args[0])
    
    if not path.exists() or not path.is_file() or path.suffix != '.json':
        return None, None, "ERROR"
    
    try:
        username = input().strip()
        password = input().strip()
    except:
        return None, None, "ERROR"
    
    try:
        notebook = Notebook("", "", "")
        notebook.load(path)
        
        if notebook.username == username and notebook.password == password:
            return notebook, path, f"Notebook loaded.\n{username}\n{notebook.bio}"
        else:
            return None, None, "ERROR"
    except (NotebookFileError, IncorrectNotebookError):
        return None, None, "ERROR"

def command_e():
    pass

def command_p():
    pass

if __name__ == "__main__":
    main()