import random

def generate_session_id():
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=16))
