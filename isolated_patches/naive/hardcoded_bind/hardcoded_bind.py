import socket
import os

def start_debug_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bind_address = os.getenv("BIND_ADDRESS", "127.0.0.1")
    s.bind((bind_address, 9999))
    return s