import json
import socket
from io import StringIO
import pytest # type: ignore
from ds_messenger import DirectMessenger, DirectMessage

class DummySocket:
    def __init__(self, responses):
        # responses: list of JSON‐lines
        self.reader = StringIO("\r\n".join(responses) + "\r\n")
        self.writer = StringIO()
    def makefile(self, mode):
        return self.reader if "r" in mode else self.writer

@pytest.fixture
def fake_socket(monkeypatch):
    def _setup(responses):
        dummy = DummySocket(responses)
        monkeypatch.setattr(socket, "create_connection", lambda addr: dummy)
        return dummy
    return _setup

def test_full_direct_messenger_flow(fake_socket):
    # 1) Auth OK
    auth = json.dumps({"response":{"type":"ok","message":"Welcome","token":"tok"}})
    # 2) send() OK
    send_ok = json.dumps({"response":{"type":"ok","message":"Sent"}})
    # 3) fetch-unread
    unread = json.dumps({
        "response":{
            "type":"ok",
            "messages":[
                {"from":"alice","recipient":"bob","message":"Hi!","timestamp":"100.5"}
            ]
        }
    })
    # 4) fetch-all (same payload)
    all_msgs = unread

    sock = fake_socket([auth, send_ok, unread, all_msgs])

    dm = DirectMessenger("host:1", "bob", "pw")
    assert dm.token == "tok"

    # send
    assert dm.send("Hello!", "alice") is True

    # retrieve_new
    new = dm.retrieve_new()
    assert isinstance(new, list) and len(new) == 1
    msg = new[0]
    assert isinstance(msg, DirectMessage)
    assert msg.sender == "alice"
    assert msg.recipient == "bob"
    assert msg.message == "Hi!"
    assert msg.timestamp == 100.5

    # retrieve_all
    all_list = dm.retrieve_all()
    assert len(all_list) == 1
    assert all_list[0].message == "Hi!"

    # Check what was sent over the socket
    lines = sock.writer.getvalue().splitlines()
    # first two are fine
    assert '"authenticate"' in lines[0]
    assert '"directmessage"' in lines[1]

    # parse the JSON to avoid whitespace issues
    req_unread = json.loads(lines[2])
    assert req_unread["fetch"] == "unread"
    req_all = json.loads(lines[3])
    assert req_all["fetch"] == "all"

def test_send_error_path(fake_socket):
    auth = json.dumps({"response":{"type":"ok","message":"Hi","token":"T"}})
    err  = json.dumps({"response":{"type":"error","message":"Nope"}})
    sock = fake_socket([auth, err])
    dm = DirectMessenger("h:1", "u", "p")
    assert dm.send("hey","bob") is False

@pytest.mark.parametrize("payload", [
    {"response":{"type":"ok"}},                # no messages
    {"response":{"type":"ok","messages":[]}},   # empty list
    {"response":{"type":"error","messages":[{}]}}
])
def test_retrieve_new_error_empty(fake_socket, payload):
    auth = json.dumps({"response":{"type":"ok","message":"OK","token":"X"}})
    sock = fake_socket([auth, json.dumps(payload)])
    dm = DirectMessenger("h:1","u","p")
    assert dm.retrieve_new() == []

@pytest.mark.parametrize("payload", [
    {"response":{"type":"ok"}},
    {"response":{"type":"ok","messages":[]}},
    {"response":{"type":"error","messages":[{}]}}
])
def test_retrieve_all_error_empty(fake_socket, payload):
    auth = json.dumps({"response":{"type":"ok","message":"OK","token":"X"}})
    sock = fake_socket([auth, json.dumps(payload)])
    dm = DirectMessenger("h:1","u","p")
    assert dm.retrieve_all() == []

def test_init_authentication_fails(fake_socket):
    # Server first reply: authentication error
    auth_err = json.dumps({
        "response": {"type":"error", "message":"Bad credentials"}
    })
    fake_socket([auth_err])

    # Expect to raise ValueError
    with pytest.raises(ValueError) as exc:
        DirectMessenger("host:1", "alice", "wrongpw")
    assert "Authentication failed" in str(exc.value)