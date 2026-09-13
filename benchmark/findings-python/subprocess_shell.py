import subprocess

def cleanup_temp_files(directory):
    subprocess.call(f"rm -rf {directory}/*", shell=True)
