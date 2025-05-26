# ds_messenger.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Alex Madas
# Madasa
# 39847840

"""
ds_messenger.py

Provides DirectMessenger for the DSP server protocol and
a DirectMessage container class.
"""

import socket
import time
from typing import List
from ds_protocol import (
    build_authenticate,
    build_directmessage,
    build_fetch,
    parse_response
)

class DirectMessage:
    """
    A simple container for one direct message.
    """
    def __init__(self):
        self.recipient: str = None
        self.sender:    str = None
        self.message:   str = None
        self.timestamp: float = None

class DirectMessenger:
    """
    A client for the DSP server.  Connects once in __init__, authenticates,
    then lets you send and fetch messages using the same connection and token.
    """
    def __init__(self,
                 dsuserver: str = "127.0.0.1:3001",
                 username:  str = None,
                 password:  str = None):
        """
        Open a TCP connection to the DSP server at host:port,
        authenticate immediately, and save the returned token.

        Raises:
            ValueError: if authentication fails.
        """
        # parse "host:port"
        host, port_str = dsuserver.split(":")
        port = int(port_str)

        # 1) establish socket connection once
        self._sock   = socket.create_connection((host, port))
        # 2) file-like wrappers for line-based I/O
        self._send_f = self._sock.makefile("w")
        self._recv_f = self._sock.makefile("r")

        # 3) authenticate and store token
        auth_json = build_authenticate(username, password)
        self._send_raw(auth_json)
        resp = parse_response(self._recv_raw())
        if resp.type != "ok":
            raise ValueError(f"Authentication failed: {resp.message}")
        self.token = resp.token

    def _send_raw(self, json_str: str) -> None:
        """
        Write one JSON request line (with CRLF) and flush.
        """
        self._send_f.write(json_str + "\r\n")
        self._send_f.flush()

    def _recv_raw(self) -> str:
        """
        Read one line (up to CRLF) from the server.
        """
        return self._recv_f.readline().strip()

    def send(self, message: str, recipient: str) -> bool:
        """
        Send `message` to `recipient`.  Returns True if the server
        acknowledges with type=="ok", False otherwise.
        """
        ts = time.time()
        dm_json = build_directmessage(self.token, message, recipient, ts)
        self._send_raw(dm_json)
        resp = parse_response(self._recv_raw())
        return resp.type == "ok"

    def _dict_to_dm(self, data: dict) -> DirectMessage:
        """
        Convert a raw message dict from the server into a DirectMessage.
        """
        dm = DirectMessage()
        raw_from = data.get("from") or data.get("sender") or ""
        dm.sender    = raw_from.strip().lower()
        raw_to       = data.get("recipient") or ""
        dm.recipient = raw_to.strip().lower()
        dm.message   = data.get("message") or data.get("entry")
        dm.timestamp = float(data.get("timestamp", 0))
        return dm

    def retrieve_new(self) -> List[DirectMessage]:
        """
        Fetch only unread messages (`fetch:"unread"`) and return
        them as a list of DirectMessage objects.
        """
        self._send_raw(build_fetch(self.token, "unread"))
        resp = parse_response(self._recv_raw())
        if resp.type != "ok" or not resp.messages:
            return []
        return [self._dict_to_dm(d) for d in resp.messages]

    def retrieve_all(self) -> List[DirectMessage]:
        """
        Fetch all messages (`fetch:"all"`) and return
        them as a list of DirectMessage objects.
        """
        self._send_raw(build_fetch(self.token, "all"))
        resp = parse_response(self._recv_raw())
        if resp.type != "ok" or not resp.messages:
            return []
        return [self._dict_to_dm(d) for d in resp.messages]
    