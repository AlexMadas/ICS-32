import json
import pytest # type: ignore
from ds_protocol import (
    build_authenticate,
    build_directmessage,
    build_fetch,
    parse_response,
    DSPResponse
)

def test_build_authenticate():
    s = build_authenticate("alice", "secret")
    obj = json.loads(s)
    assert "authenticate" in obj
    assert obj["authenticate"] == {"username": "alice", "password": "secret"}

def test_build_directmessage():
    ts = 1625078400.123
    s = build_directmessage("tok123", "Hi!", "bob", ts)
    obj = json.loads(s)
    assert obj["token"] == "tok123"
    dm = obj["directmessage"]
    assert dm == {
        "entry": "Hi!",
        "recipient": "bob",
        "timestamp": str(ts)
    }

@pytest.mark.parametrize("what", ["all", "unread"])
def test_build_fetch(what):
    s = build_fetch("tokenXYZ", what)
    obj = json.loads(s)
    assert obj == {"token": "tokenXYZ", "fetch": what}

def test_parse_response_full():
    payload = {
        "response": {
            "type": "ok",
            "message": "All good",
            "token": "tokABC",
            "messages": [{"sender": "alice", "entry": "Hey!"}]
        }
    }
    resp = parse_response(json.dumps(payload))
    assert isinstance(resp, DSPResponse)
    assert resp.type == "ok"
    assert resp.message == "All good"
    assert resp.token == "tokABC"
    assert resp.messages == [{"sender": "alice", "entry": "Hey!"}]

def test_parse_response_partial():
    payload = {"response": {"type": "error", "message": "Invalid token"}}
    resp = parse_response(json.dumps(payload))
    assert resp.type == "error"
    assert resp.message == "Invalid token"
    assert resp.token is None
    assert resp.messages is None

def test_parse_response_missing_response():
    with pytest.raises(ValueError) as exc:
        parse_response(json.dumps({"nope": {}}))
    assert "Missing 'response'" in str(exc.value)

def test_parse_response_invalid_json():
    with pytest.raises(ValueError) as exc:
        parse_response("}{ not valid json")
    assert "Invalid JSON" in str(exc.value)