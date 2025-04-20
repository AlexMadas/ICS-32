# Starter code for assignment 1 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Alex Madas
# Madasa@uci.edu
# 39847840

from pathlib import Path
from command_parser import parse_command
from notebook import Notebook, Diary, NotebookFileError, IncorrectNotebookError

def main():
    """  
    Main entry point of the diary program.  
    Handles user input, command parsing, and execution until the user quits.  
    Manages the currently loaded notebook and its file path.  
    """  
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
            print("ERROR")
            continue

        command = parsed['command']

        if command == 'C':
            new_nb, new_path, output = command_c(parsed)
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

        elif command == 'E':
            if not current_notebook or not current_path:
                print("ERROR")
                continue
            output = command_e(parsed, current_notebook, current_path)
            if output:
                print(output)

        elif command == 'P':
            if not current_notebook or not current_path:
                print("ERROR")
                continue
            output = command_p(parsed, current_notebook, current_path)
            if output:
                print(output)

        else:
            print("ERROR")

def command_c(parsed):
    """  
    Handles the 'C' command to create a new notebook.  

    Args:  
        parsed: Parsed command components (dict with 'args', 'options', etc.).  

    Returns:  
        Tuple containing:  
        - New Notebook object (or None on error),  
        - Path to the new notebook (or None on error),  
        - Output message ("CREATED" or "ERROR").  

    Raises:  
        NotebookFileError: If the notebook file cannot be created.  
    """  
    args = parsed['args']
    options = parsed['options']
    
    if len(args) != 1 or '-n' not in options or not options['-n']:
        return None, None, "ERROR"
    
    dir_path = Path(args[0])
    diary_name = options['-n']
    full_path = dir_path / f"{diary_name}.json"

    if not dir_path.exists() or not dir_path.is_dir() or full_path.exists():
        return None, None, "ERROR"

    try:
        username = input("").strip()
        password = input("").strip()
        bio = input("").strip()
    except:
        return None, None, "ERROR"

    try:
        new_notebook = Notebook(username, password, bio)
        new_notebook.save(full_path)
        return new_notebook, full_path, f"{full_path.absolute()} CREATED"
    except:
        return None, None, "ERROR"

def command_d(parsed):
    """  
    Handles the 'D' command to delete a notebook file.  

    Args:  
        parsed: Parsed command components.  

    Returns:  
        Output message ("DELETED" or "ERROR").  
    """  
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
    """  
    Handles the 'O' command to load an existing notebook.  

    Args:  
        parsed: Parsed command components.  

    Returns:  
        Tuple containing:  
        - Loaded Notebook object (or None on error),  
        - Path to the loaded notebook (or None on error),  
        - Output message ("Notebook loaded." or "ERROR").  

    Raises:  
        IncorrectNotebookError: If the notebook file is invalid.  
    """  
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

def command_e(parsed, notebook, path):
    """  
    Handles the 'E' command to edit the loaded notebook.  

    Args:  
        parsed: Parsed command components.  
        notebook: Currently loaded Notebook object.  
        path: Path to the notebook file.  

    Returns:  
        "ERROR" if any operation fails; otherwise, an empty string.  
    """  
    if not notebook or not path:
        return "ERROR"

    error_flag = False

    for opt in parsed.get('options_order', []):
        value = parsed['options'].get(opt)

        if value is None or opt not in ['-usr', '-pwd', '-bio', '-add', '-del']:
            error_flag = True
            break

        try:
            if opt == '-usr':
                notebook.username = value
            elif opt == '-pwd':
                notebook.password = value
            elif opt == '-bio':
                notebook.bio = value
            elif opt == '-add':
                diary = Diary(entry=value)
                notebook.add_diary(diary)
            elif opt == '-del':
                idx = int(value)
                if not notebook.del_diary(idx):
                    error_flag = True
                    break

            notebook.save(path)
        except:
            error_flag = True
            break

    return "ERROR" if error_flag else ""

def command_p(parsed, notebook, path):
    """  
    Handles the 'P' command to print notebook information.  

    Args:  
        parsed: Parsed command components.  
        notebook: Currently loaded Notebook object.  
        path: Path to the notebook file (unused but included for consistency).  

    Returns:  
        Formatted output string or "ERROR".  
    """
    if not notebook or not path:
        return "ERROR"

    output_lines = []
    error_flag = False

    for opt in parsed.get('options_order', []):
        value = parsed['options'].get(opt)

        valid_options = ['-usr', '-pwd', '-bio', '-diaries', '-diary', '-all']
        if opt not in valid_options:
            error_flag = True
            break

        if opt == '-usr':
            output_lines.append(notebook.username)
        elif opt == '-pwd':
            output_lines.append(notebook.password)
        elif opt == '-bio':
            output_lines.append(notebook.bio)
        elif opt == '-diaries':
            for idx, diary in enumerate(notebook.get_diaries()):
                output_lines.append(f"{idx}: {diary.entry}")
        elif opt == '-diary':
            if value is None:
                error_flag = True
                break
            try:
                idx = int(value)
                diary = notebook.get_diaries()[idx]
                output_lines.append(diary.entry)
            except (ValueError, IndexError):
                error_flag = True
                break
        elif opt == '-all':
            output_lines.append(notebook.username)
            output_lines.append(notebook.password)
            output_lines.append(notebook.bio)
            for idx, diary in enumerate(notebook.get_diaries()):
                output_lines.append(f"{idx}: {diary.entry}")
        else:
            error_flag = True
            break

        if error_flag:
            break

    if error_flag:
        output_lines.append("ERROR")

    return '\n'.join(output_lines) if output_lines else "ERROR"

if __name__ == "__main__":
    main()