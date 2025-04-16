#lab3.py

# Starter code for lab 3 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.
# Please see the README in this repository for the requirements of this lab exercise

# ALEX MADAS
# MADASA@UCI.EDU
# 39847840

from pathlib import Path

folder = input("Where should I save your notes? (Press enter for current folder): ").strip()
note_file = Path(folder) / "pynote.txt" if folder else Path("pynote.txt")

def load_notes():
    if note_file.exists():
        with open(note_file, "r") as file:
            return file.readlines()
    return []

def display_notes(notes):
    print("Welcome to PyNote!")
    print("Here are your notes:\n")
    for note in notes:
        print(note.strip())
    print()

def add_note(note):
    with open(note_file, "a") as file:
        file.write(note + "\n")

def main():
    notes = load_notes()
    display_notes(notes)

    while True:
        new_note = input("Please enter a new note (enter q to exit): ")
        if new_note.strip().lower() == "q":
            break
        add_note(new_note)

if __name__ == "__main__":
    main()
