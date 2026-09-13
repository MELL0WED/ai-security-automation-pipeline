import json
import subprocess


def run_semgrep(target_dir: str) -> list[dict]:
    result = subprocess.run(
        ["semgrep", "--config=auto", target_dir, "--json"],
        capture_output=True, text=True,
    )
    data = json.loads(result.stdout)
    return data["results"]
