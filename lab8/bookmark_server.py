import socket
from collections import namedtuple
from pathlib import Path
import bookmark_connection as bmc
from bookmark_connection import Connection, BookmarkServerError
from bookmarker import Bookmarker

BOOKMARK_PATH = "."
BOOKMARK_FILE = "pybookmark.txt"

PORT = 2024
HOST = "127.0.0.1"

def store(_conn: bmc.Connection, bm: Bookmarker, url: str) -> str:
    '''
    store will send the command specified by the parameters and return a response to the command. 

    url: the URL of the webpage to bookmark
    status: either 0 or 1 to indicate the status of the command specified in the url parameter
    '''
    try:
        # TODO: store the provided url in the pybookmark.txt file using the provided Bookmarker (bm parameter) object's _add_ function
        bm.add(url)
        status = 1
    except ValueError:
        status = 0

    bmc._write_command(_conn, str(status))
    return bmc._read_command(_conn)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    # the file used to store bookmarks
    p = Path(BOOKMARK_PATH) / BOOKMARK_FILE

    # if file does not exist, create it.
    if not p.exists():
        p.touch()

    # instantiate the bookmark class and pass to run 
    bm = Bookmarker(p)

    # TODO: using the srv object, bind to the server
    # specified by the HOST and PORT variables and start listening.
    srv.bind((HOST, PORT))
    srv.listen()  

    print("server listening on port", PORT)
    while True:
        connection, address = srv.accept()

        with connection:
            print("client connected")
            _bmc_conn = bmc.init(connection)

            while True:
                rec_msg = bmc.listen(_bmc_conn)
                
                # assume an empty message means client has disconnected so break
                # and wait for new connection
                if rec_msg == '': break

                print("message: ", rec_msg)

                try:
                    store(_bmc_conn, bm, rec_msg)
                except Exception as ex:
                    bmc.error(_bmc_conn)
                    print(ex)
                    break
            
            print("client disconnected")

