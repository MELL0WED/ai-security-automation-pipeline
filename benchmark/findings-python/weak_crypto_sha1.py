import hashlib

def generate_token(user_id):
    return hashlib.sha1(str(user_id).encode()).hexdigest()
