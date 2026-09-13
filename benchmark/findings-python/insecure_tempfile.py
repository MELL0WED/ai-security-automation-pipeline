import os

def create_temp_file(content):
    path = "/tmp/upload_" + str(os.getpid())
    with open(path, "w") as f:
        f.write(content)
    return path
