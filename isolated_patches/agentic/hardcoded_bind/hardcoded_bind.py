import socket

def start_debug_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to localhost to avoid exposing the service on all interfaces
    s.bind(("127.0.0.1", 9999))
    return s
