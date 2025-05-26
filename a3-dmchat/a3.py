# a2.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Alex Madas
# Madasa
# 39847840

"""
a3.py

GUI front-end for the DSP chat client:
  - Login as a user (online or offline)
  - Send and receive direct messages
  - Persist contacts & history locally
"""

import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ds_messenger import DirectMessenger
from notebook import Notebook, NotebookFileError, IncorrectNotebookError

REFRESH_INTERVAL_MS = 5000  # auto-poll every 5 seconds

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DS Chat")

        # 1) Get credentials
        raw_user = simpledialog.askstring("Login", "Username:", parent=self)
        self.username = raw_user.strip().lower() if raw_user else None
        raw_pw = simpledialog.askstring("Login", "Password:", show="*", parent=self)
        self.password = raw_pw.strip() if raw_pw else None
        if not self.username or not self.password:
            messagebox.showerror("Error", "Username and password required")
            self.destroy()
            return

        # 2) Load notebook (always do this)
        self.notebook = Notebook(self.username, self.password, bio="")
        store_path = Path("store") / f"{self.username}.json"
        try:
            self.notebook.load(str(store_path))
        except (NotebookFileError, IncorrectNotebookError):
            pass  # first run or malformed

        # 3) Connect to server
        try:
            self.dm = DirectMessenger("127.0.0.1:3001", self.username, self.password)
            self.online = True
        except Exception:
            messagebox.showwarning("Offline", "Cannot connect to server — offline mode")
            self.dm = None
            self.online = False

        # 4) Build and populate the UI
        self._build_widgets()
        self._populate_contacts()

        # 5) Schedule refresh only if online
        if self.online:
            self._schedule_refresh()

        # 6) Save on exit
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_widgets(self):
        # layout: two columns
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Contacts treeview (left)
        self.tree = ttk.Treeview(self, show="tree", selectmode="browse")
        self.tree.bind("<<TreeviewSelect>>", self._on_contact_select)
        self.tree.grid(row=0, column=0, sticky="ns")

        # Messages display (right, top)
        self.text = tk.Text(self, wrap="word", state="disabled")
        # tags for styling
        self.text.tag_configure("sent", foreground="blue", justify="right")
        self.text.tag_configure("recv", foreground="green", justify="left")
        self.text.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Entry + buttons (right, bottom)
        bottom = ttk.Frame(self)
        bottom.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        bottom.columnconfigure(0, weight=1)

        self.entry = ttk.Entry(bottom)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", lambda e: self._send_message())

        send_btn = ttk.Button(bottom, text="Send", command=self._send_message)
        send_btn.grid(row=0, column=1, padx=(5,0))

        add_btn = ttk.Button(bottom, text="Add User", command=self._add_contact)
        add_btn.grid(row=0, column=2, padx=(5,0))

    def _populate_contacts(self):
        # 1) clear out the old items
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        # 2) re-insert each contact
        for contact in self.notebook.get_contacts():
            # skip any invalid entries
            if not contact:
                continue
            self.tree.insert("", "end", iid=contact, text=contact)

    def _on_contact_select(self, event=None):
        sel = self.tree.selection()
        if not sel: return
        contact = sel[0]
        self._display_history(contact)

    def _display_history(self, contact):
        # clear text
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        # load messages from notebook
        for msg in self.notebook.get_messages(contact):
            tag = "sent" if msg["sender"] == self.username else "recv"
            ts = time.strftime("%H:%M:%S", time.localtime(msg["timestamp"]))
            line = f"[{ts}] {msg['sender']}: {msg['entry']}\n"
            self.text.insert("end", line, tag)
        self.text.config(state="disabled")
        self.text.see("end")

    def _send_message(self):
        # Get the currently selected contact
        sel = self.tree.selection()
        # If no contact is selected, prompt the user and stop
        if not sel:
            messagebox.showwarning("No Contact", "Select a contact first")
            return

        # If the app is offline, show an error and stop
        if not self.online:
            messagebox.showerror("Offline", "Cannot send while offline")
            return

        # Extract the contact name and trimmed message text
        contact = sel[0]
        msg_text = self.entry.get().strip()
        # If the message is empty, do nothing
        if not msg_text:
            return

        # Send the message via the DirectMessenger
        success = self.dm.send(msg_text, contact)
        # If the send failed, notify the user
        if not success:
            messagebox.showerror("Send Failed", "Could not send message")
            return

        # Record the timestamped message locally
        now = time.time()
        raw = {
            "sender":    self.username,
            "recipient": contact,
            "entry":     msg_text,
            "timestamp": now
        }
        self.notebook.add_message(raw)
        # Refresh the display to include the new message
        self._display_history(contact)
        # Clear the input field
        self.entry.delete(0, "end")

    def _add_contact(self):
        # Prompt for a new contact username
        raw = simpledialog.askstring("Add Contact", "Username:", parent=self)
        if not raw:
            return
        # Normalize the username to lowercase
        contact = raw.strip().lower()
        # If the contact is new, add to notebook and treeview
        if contact not in self.notebook.get_contacts():
            self.notebook.add_contact(contact)
            self.tree.insert("", "end", iid=contact, text=contact)

    def _refresh(self):
        # Attempt to fetch unread messages from the server
        try:
            new_msgs = self.dm.retrieve_new()
        except Exception:
            # On any error, skip this refresh cycle
            return
        # Process each incoming message
        for dm in new_msgs:
            raw = {
                "sender":    dm.sender,
                "recipient": dm.recipient,
                "entry":     dm.message,
                "timestamp": dm.timestamp
            }
            # Store the message locally
            self.notebook.add_message(raw)
            # If the current chat matches the sender, update the view
            sel = self.tree.selection()
            if sel and sel[0] == dm.sender:
                self._display_history(dm.sender)
        # Schedule the next auto-refresh
        self._schedule_refresh()

    def _schedule_refresh(self):
        # Call _refresh again after the defined interval
        self.after(REFRESH_INTERVAL_MS, self._refresh)

    def _on_close(self):
        # Build the path for the notebook file
        store_path = Path("store") / f"{self.username}.json"
        # Attempt to save local data before exiting
        try:
            self.notebook.save(str(store_path))
        except Exception as e:
            print("Warning: failed to save notebook:", e)
        # Close the application window
        self.destroy()

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
