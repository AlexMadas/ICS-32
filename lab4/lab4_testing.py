"""
This program enables a user to input short one line notes and have them stored in a file called pynote.txt
"""

from pathlib import Path

NOTES_PATH = "."
NOTES_FILE = "pynote.txt"

def is_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def save_note(note: str):
    # create path obj to notes storage file
    p = Path(NOTES_PATH) / NOTES_FILE

    # check if storage file exists, if not create it.
    if not p.exists():
        p.touch(exist_ok=True)
    
    # open and write user note to file
    f = p.open('a')
    f.write(note + '\n')
    f.close()

def read_notes():
    p = Path(NOTES_PATH) / NOTES_FILE

    # check if storage file exists, if not return.
    if not p.exists():
        return
    
    print("Here are your notes: \n")
    # open and write user note to file
    f = p.open()
    for line in f:
        print(line)
    f.close()

def remove_note() -> str:
    p = Path(NOTES_PATH) / NOTES_FILE

    # check if storage file exists, if not return.
    if not p.exists():
        raise FileNotFoundError("pynote.txt does not exist")
    
    print("Here are your notes: \n")
    # open and write user note to file
    f = p.open()
    id = 1
    lines = []

    # print each note with an id and store each line in a list
    for line in f:
        lines.append(line)
        print(f"{id}: {line}")
        id = id+1
    f.close()

    remove_id = input("Enter the number of the note you would like to remove: ")
    if not is_int(remove_id):
        print ("Not a valid number, cancelling operation.")
        return ""

    # open as write to overwrite existing notes, add notes back while skipping user selection 
    f = p.open('w')
    id = 1
    removed_note = ""

    for line in lines:
        if id == int(remove_id):
            removed_note = line
        else:
            f.write(line)
        id = id+1
    f.close()

    return removed_note

def run():
    note = input("Please enter a note (enter :d to delete a note or :q to exit):  ")
    if note == ":d":
        note = remove_note()
        if note == "":
                print()
        else:
            print(f"The following note has been removed: \n\n {note}")
    elif note == ":q":
        return
    else:    
        save_note(note)
    run()


if __name__ == "__main__":
    print("Welcome to PyNote! \n")
    read_notes()

    p = Path(NOTES_PATH) / NOTES_FILE
    if p.exists():
        p.unlink()

    try:
        remove_note()
        assert False, "Expected FileNotFoundError but it was not raised"
    except FileNotFoundError:
        pass

    assert is_int(43) == True
    assert is_int("00000123") == True
    assert is_int("+123") == True
    assert is_int("123") == True
    assert is_int("-10") == True
    assert is_int("0") == True
    assert is_int("1.5") == False
    assert is_int("abc") == False
    assert is_int("") == False
    assert is_int(None) == False
    assert is_int([]) == False
    assert is_int(3.14) == False  

    run()

