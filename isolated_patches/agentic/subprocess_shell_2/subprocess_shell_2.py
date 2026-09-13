import subprocess

def archive_logs(log_dir, dest):
    subprocess.Popen(["tar", "-czf", dest, log_dir], shell=False)
