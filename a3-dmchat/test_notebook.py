import json
import time
import pytest # type: ignore
import pathlib
from notebook import Notebook, Diary, NotebookFileError, IncorrectNotebookError

def test_contacts_initially_empty():
    nb = Notebook("user","pw","bio")
    assert nb.get_contacts() == []

def test_add_and_get_contacts():
    nb = Notebook("u","p","b")
    nb.add_contact("Alice")
    assert nb.get_contacts() == ["alice"]
    nb.add_contact("ALICE")
    assert nb.get_contacts() == ["alice"]
    nb.add_contact("bob")
    assert nb.get_contacts() == ["alice","bob"]

def test_messages_initially_empty():
    nb = Notebook("u","p","b")
    assert nb.get_messages("alice") == []

def test_add_message_and_get_messages():
    nb = Notebook("user","pw","bio")
    msg1 = {"sender":"alice","recipient":"user","entry":"Hello","timestamp":1.23}
    nb.add_message(msg1.copy())
    assert nb.get_contacts() == ["alice"]
    assert nb.get_messages("alice") == [msg1]

    msg2 = {"sender":"user","recipient":"bob","entry":"Hi","timestamp":2.34}
    nb.add_message(msg2.copy())
    assert "bob" in nb.get_contacts()
    assert nb.get_messages("bob") == [msg2]

def test_diary_methods():
    nb = Notebook("u","p","b")
    d1 = Diary("entry1", 10.0)
    nb.add_diary(d1)
    assert nb.get_diaries() == [d1]
    d2 = Diary("entry2", 20.0)
    nb.add_diary(d2)
    assert len(nb.get_diaries()) == 2
    assert nb.del_diary(0) is True
    assert nb.get_diaries() == [d2]
    assert nb.del_diary(5) is False
    assert nb.get_diaries() == [d2]

def test_save_and_load_round_trip(tmp_path):
    nb1 = Notebook("user","pw","bio")
    nb1.add_contact("alice")
    msg = {"sender":"alice","recipient":"user","entry":"Hi","timestamp":3.14}
    nb1.add_message(msg.copy())
    d = Diary("note", 30.0)
    nb1.add_diary(d)

    p = tmp_path / "note.json"
    nb1.save(str(p))

    nb2 = Notebook("other","x","y")
    nb2.load(str(p))
    assert nb2.username == "user"
    assert nb2.password == "pw"
    assert nb2.bio == "bio"
    assert nb2.get_contacts() == ["alice"]
    assert nb2.get_messages("alice") == [msg]
    diaries = nb2.get_diaries()
    assert len(diaries) == 1
    assert diaries[0].entry == "note"
    assert diaries[0].timestamp == 30.0

def test_save_invalid_extension(tmp_path):
    nb = Notebook("u","p","b")
    p = tmp_path / "bad.txt"
    with pytest.raises(NotebookFileError):
        nb.save(str(p))

def test_load_missing_file(tmp_path):
    nb = Notebook("u","p","b")
    missing = tmp_path / "no.json"
    with pytest.raises(NotebookFileError):
        nb.load(str(missing))

def test_load_invalid_json(tmp_path):
    nb = Notebook("u","p","b")
    bad = tmp_path / "bad.json"
    bad.write_text("not valid json")
    with pytest.raises(IncorrectNotebookError):
        nb.load(str(bad))

def test_load_missing_keys(tmp_path):
    nb = Notebook("u","p","b")
    path = tmp_path / "missing.json"
    path.write_text(json.dumps({"foo":"bar"}))
    with pytest.raises(IncorrectNotebookError):
        nb.load(str(path))

def test_diary_auto_timestamp_and_entry_dict():
    before = time.time()
    d = Diary("hello world")
    after = time.time()
    assert before <= d.timestamp <= after
    assert d["timestamp"] == d.timestamp
    assert d["entry"] == "hello world"

def test_diary_set_time_and_entry_update():
    d = Diary("foo", timestamp=123.0)
    # Overwrite via property
    d.timestamp = 42.0
    assert d.timestamp == 42.0
    assert d["timestamp"] == 42.0

    # Change the entry via property, dict updates too
    d.entry = "bar"
    assert d.entry == "bar"
    assert d["entry"] == "bar"

def test_load_existing_bad_extension(tmp_path):
    # Create a .txt file (so suffix != '.json')
    data = tmp_path / "notebook.txt"
    data.write_text('{"username":"u","password":"p","bio":""}')
    nb = Notebook("u","p","b")
    with pytest.raises(NotebookFileError):
        nb.load(str(data))

def test_save_io_error(monkeypatch, tmp_path):
    nb = Notebook("u","p","b")
    out = tmp_path / "fail.json"
    # Monkey‐patch Path.open to always raise
    monkeypatch.setattr(pathlib.Path, "open", lambda *args, **kwargs: (_ for _ in ()).throw(IOError("disk full")))
    with pytest.raises(NotebookFileError) as exc:
        nb.save(str(out))
    assert "Failed to write notebook file" in str(exc.value)