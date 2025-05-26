# ICS 32
# Assignment #1: Diary
#
# Author: Aaron Imani
#
# v0.1.0

# You should review this code to identify what features you need to support
# in your program for assignment 1.
#
# YOU DO NOT NEED TO READ OR UNDERSTAND THE JSON SERIALIZATION ASPECTS OF THIS CODE 
# RIGHT NOW, though can you certainly take a look at it if you are curious since we 
# already covered a bit of the JSON format in class.

"""
notebook.py

Manages persistent storage of user credentials, contacts, messages, and diary entries.
"""

import json
import time
from pathlib import Path

class NotebookFileError(Exception):
    """
    NotebookFileError is a custom exception handler that you should catch in your own code. It
    is raised when attempting to load or save Notebook objects to file the system.
    """
    pass

class IncorrectNotebookError(Exception):
    """
    NotebookError is a custom exception handler that you should catch in your own code. It
    is raised when attempting to deserialize a notebook file to a Notebook object.
    """
    pass

class Diary(dict):
    """ 
    The Diary class is responsible for working with individual user diaries. It currently 
    supports two features: A timestamp property that is set upon instantiation and 
    when the entry object is set and an entry property that stores the diary message.
    """
    def __init__(self, entry:str = None, timestamp:float = 0):
        self._timestamp = timestamp
        self.set_entry(entry)

        # Subclass dict to expose Diary properties for serialization
        # Don't worry about this!
        dict.__init__(self, entry=self._entry, timestamp=self._timestamp)
    
    def set_entry(self, entry):
        self._entry = entry
        dict.__setitem__(self, 'entry', entry)

        # If timestamp has not been set, generate a new from time module
        if self._timestamp == 0:
            self._timestamp = time.time()

    def get_entry(self):
        return self._entry
    
    def set_time(self, time:float):
        self._timestamp = time
        dict.__setitem__(self, 'timestamp', time)
    
    def get_time(self):
        return self._timestamp

    """
    The property method is used to support get and set capability for entry and 
    time values. When the value for entry is changed, or set, the timestamp field is 
    updated to the current time.
    """ 
    entry = property(get_entry, set_entry)
    timestamp = property(get_time, set_time)
    
    
class Notebook:
    """Notebook is a class that can be used to manage a diary notebook."""

    def __init__(self, username: str, password: str, bio: str):
        """Creates a new Notebook object. 
        Args:
            username (str): The username of the user.
            password (str): The password of the user.
            bio (str): The bio of the user.
        """
        self.username = username
        self.password = password
        self.bio = bio
        self._diaries = []
        self._contacts = []
        self._messages = {}

    def add_diary(self, diary: Diary) -> None:
        """Accepts a Diary object as parameter and appends it to the diary list. Diaries 
        are stored in a list object in the order they are added. So if multiple Diary objects 
        are created, but added to the Profile in a different order, it is possible for the 
        list to not be sorted by the Diary.timestamp property. So take caution as to how you 
        implement your add_diary code.

        """
        self._diaries.append(diary)

    def del_diary(self, index: int) -> bool:
        """
        Removes a Diary at a given index and returns `True` if successful and `False` if an invalid index was supplied. 

        To determine which diary to delete you must implement your own search operation on 
        the diary returned from the get_diaries function to find the correct index.

        """
        try:
            del self._diaries[index]
            return True
        except IndexError:
            return False

    def get_diaries(self) -> list[Diary]:
        """Returns the list object containing all diaries that have been added to the Notebook object"""
        return self._diaries

    def add_contact(self, contact: str) -> None:
        """
        Record a new contact if not already present.
        """
        c = contact.strip().lower()
        if c and c not in self._contacts:
            self._contacts.append(c)

    def get_contacts(self) -> list[str]:
        """
        Return the list of stored contacts.
        """
        return self._contacts

    def add_message(self, msg: dict) -> None:
        """
        Store a message locally. `msg` should have keys: sender, recipient, entry, timestamp.
        Automatically adds the other party as a contact and appends the raw dict.
        """
        # Determine which user is the contact
        s = (msg.get("sender") or "").strip().lower()
        r = (msg.get("recipient") or "").strip().lower()
        contact = r if s == self.username else s
        if contact:
            self.add_contact(contact)
            self._messages.setdefault(contact, []).append(msg)

    def get_messages(self, contact: str) -> list[dict]:
        """
        Return the conversation history with `contact`.
        """
        return self._messages.get(contact, [])

    def save(self, path: str) -> None:
        """
        Accepts an existing notebook file to save the current instance of Notebook to the file system.

        Example usage:
        ```
        notebook = Notebook('jo)
        notebook.save('/path/to/file.json')
        ```
        Raises NotebookFileError, IncorrectNotebookError
        """
        p = Path(path)

        if p.suffix != '.json':
            raise NotebookFileError("Notebook file must have a .json extension")
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'username': self.username,
            'password': self.password,
            'bio': self.bio,
            '_contacts': self._contacts,
            '_messages': self._messages,
            '_diaries': [dict(d) for d in self._diaries]
        }
        try:
            with p.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as ex:
            raise NotebookFileError("Failed to write notebook file") from ex

    def load(self, path: str) -> None:
        """
        Populates the current instance of Notebook with data stored in a notebook file.
        Example usage: 
        ```
        notebook = Notebook()
        notebook.load('/path/to/file.json')
        ```
        Raises NotebookFileError, IncorrectNotebookError
        """
        p = Path(path)
        if not p.exists() or p.suffix != '.json':
            raise NotebookFileError(f"{path} not found or not a .json file")

        try:
            with p.open('r', encoding='utf-8') as f:
                obj = json.load(f)

            self.username = obj['username']
            self.password = obj['password']
            self.bio      = obj['bio']
            self._contacts = obj.get('_contacts', [])
            self._messages = obj.get('_messages', [])

            self._diaries = [
                Diary(d['entry'], d['timestamp'])
                for d in obj.get('_diaries', [])
            ]
        except (KeyError, json.JSONDecodeError) as e:
            raise IncorrectNotebookError(f"Bad notebook format: {e}")
        except Exception as e:
            raise IncorrectNotebookError(f"Could not load notebook: {e}") from e
