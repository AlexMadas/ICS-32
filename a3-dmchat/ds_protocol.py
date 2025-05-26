# ds_protocol.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Alex Madas
# Madasa
# 39847840

"""
ds_protocol.py

Implements JSON builders and parser for the Direct Messaging Protocol.
"""

import json
from collections import namedtuple
from json import JSONDecodeError

# Define a simple tuple-like class to hold every server response
DSPResponse = namedtuple('DSPResponse', ['type', 'message', 'token', 'messages'])

def build_authenticate(username: str, password: str) -> str:
    """
    Build a JSON string to authenticate a user.
    """
    payload = {
        "authenticate": {
            "username": username,
            "password": password
        }
    }
    return json.dumps(payload)

def build_directmessage(token: str, entry: str, recipient: str, timestamp: float) -> str:
    """
    Build a JSON string to send a direct message.
    `timestamp` will be converted to a string.
    """
    payload = {
        "token": token,
        "directmessage": {
            "entry": entry,
            "recipient": recipient,
            "timestamp": str(timestamp)
        }
    }
    return json.dumps(payload)

def build_fetch(token: str, what: str) -> str:
    """
    Build a JSON string to fetch messages.
    `what` must be either "all" or "unread".
    """
    payload = {
        "token": token,
        "fetch": what
    }
    return json.dumps(payload)

def parse_response(json_msg: str) -> DSPResponse:
    """
    Parse any server response JSON string into a DSPResponse.
    Raises ValueError if the input is not valid JSON or missing fields.
    """
    try:
        obj = json.loads(json_msg)
    except JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {e}") from e

    # All valid responses wrap their data under the "response" key
    if 'response' not in obj:
        raise ValueError("Missing 'response' object in server reply")

    resp = obj['response']
    resp_type = resp.get('type')       # "ok" or "error"
    message   = resp.get('message')    # human-readable info
    token     = resp.get('token')      # only present after authenticate
    messages  = resp.get('messages')   # only present after fetch

    return DSPResponse(resp_type, message, token, messages)
