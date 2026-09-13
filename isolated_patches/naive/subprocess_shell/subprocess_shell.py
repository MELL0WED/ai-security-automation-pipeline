import shutil
import os

def cleanup_temp_files(directory):
    """
    Remove all files and subdirectories within the given directory safely.
    """
    # Delete the directory and recreate it to ensure all contents are removed.
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.makedirs(directory, exist_ok=True)
