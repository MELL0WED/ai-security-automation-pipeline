import pickle

def restore_session(session_data):
    session = pickle.loads(session_data)
    return session
