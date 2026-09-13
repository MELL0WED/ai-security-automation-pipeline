import subprocess

def archive_logs(log_dir, dest):
    # Use a list of arguments and disable the shell to prevent injection attacks
    subprocess.Popen(["tar", "-czf", dest, log_dir], shell=False)
