import importlib

def load_handler(handler_name):
    return importlib.import_module(handler_name)
