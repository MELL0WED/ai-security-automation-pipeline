import subprocess

def archive_logs(log_dir, dest):
    subprocess.Popen(f"tar -czf {dest} {log_dir}", shell=True)
