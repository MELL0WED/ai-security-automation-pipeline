from pathlib import Path
from app.core.scanner import run_semgrep


def verify_patch(patched_code: str, original_rule: str, file_name: str, isolated_dir: Path) -> dict:
    isolated_dir.mkdir(parents=True, exist_ok=True)
    patched_file = isolated_dir / file_name
    patched_file.write_text(patched_code)

    rescan_findings = run_semgrep(str(isolated_dir))
    original_still_present = any(f["check_id"] == original_rule for f in rescan_findings)
    verified = (not original_still_present) and (len(rescan_findings) == 0)

    return {
        "original_finding_removed": not original_still_present,
        "new_findings_after_patch": len(rescan_findings),
        "verified": verified,
    }
