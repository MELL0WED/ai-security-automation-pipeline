import subprocess

def run_backup_script():
    # command is hardcoded, not user-influenced, but subprocess use often flagged
    subprocess.run(["backup.sh", "--full"], shell=False)
