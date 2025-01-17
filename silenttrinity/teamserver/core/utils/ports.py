# silenttrinity/silenttrinity/teamserver/utils/ports.py

import socket

def find_free_port():
    """
    Bind to '0' which tells the OS to pick a free port.
    Return that port number.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
