# NAME
# EMAIL
# STUDENT ID

import urllib
import urllib.request
import urllib.parse
import bookmark_connection as bmc
from bookmark_connection import BookmarkProtocol

"""
The following code snippets can be used to help you prepare your test function:
The url to use for testing.
Be sure to run bookmark_server.py before making requests!

url = 'http://localhost:8000'

The format to use for your request data.
Don't forget to encode before sending a request!

json = {'data':bmc.BookmarkProtocol.format(
                                BookmarkProtocol(BookmarkProtocol.ADD, data))}
"""

def http_api_test():
    # TODO: write your http connection code here. You can use the above snippets to help
    """
    Send a series of ADD requests over HTTP to the local PyBookmarker server.
    Prints the server response for each URL.
    """
    base_url = 'http://localhost:8000'
    test_urls = [
        'http://example.com',
        'https://youtube.com',
        'http://uci.edu'
    ]

    for url in test_urls:
        # Format the protocol command: "2|<url>"
        proto_msg = BookmarkProtocol.format(
            BookmarkProtocol(BookmarkProtocol.ADD, url)
        )
        # Encode as form data under the key 'data'
        form_data = urllib.parse.urlencode({'data': proto_msg}).encode('utf-8')
        # Build and send the POST request
        req = urllib.request.Request(base_url, data=form_data)
        try:
            with urllib.request.urlopen(req) as resp:
                result = resp.read().decode('utf-8')
        except Exception as e:
            result = f"ERROR: {e}"
        # Print outcome
        print(f"POST ADD {url:<25} → {result}")

if __name__ == '__main__':
    # TODO: call your test code from here. You might try writing a few different url tests.
    print("Running HTTP API tests...")
    http_api_test()
