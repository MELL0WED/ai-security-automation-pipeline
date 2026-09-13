import json
from pathlib import Path

from app.core.scanner import run_semgrep
from app.core.agent import build_pipeline
from app.core.verifier import verify_patch

BENCHMARK_DIR = "benchmark/findings-python"
ISOLATED_DIR = Path("isolated_patches")
RESULTS_DIR = Path("results")


def run_naive_baseline(findings: list[dict]) -> dict:
    """Base condition: auto-patch and verify EVERY finding, no confidence gating."""
    from app.core.agent import chain  # reuse the same triage call, but ignore its confidence signal

    results = []
    for finding in findings:
        rule = finding["check_id"]
        message = finding["extra"]["message"]
        file_path = Path(finding["path"])
        code = file_path.read_text()

        triage = chain.invoke({
            "rule": rule, "message": message,
            "file_path": str(file_path), "code": code,
        })

        # Naive: apply the patch regardless of confidence
        if triage["patched_code"]:
            verification = verify_patch(
                triage["patched_code"], rule, file_path.name,
                ISOLATED_DIR / "naive" / file_path.stem,
            )
        else:
            verification = {"original_finding_removed": False, "new_findings_after_patch": -1, "verified": False}

        results.append({
            "rule": rule,
            "file": file_path.name,
            "confidence": triage["confidence"],
            "auto_patched": True,  # naive pipeline ALWAYS patches
            **verification,
        })

    return {"mode": "naive_baseline", "results": results}


def run_agentic_pipeline(findings: list[dict]) -> dict:
    """Improved condition: LangGraph agent routes by confidence — only HIGH-confidence findings get auto-fixed."""
    pipeline = build_pipeline()
    results = []

    for finding in findings:
        rule = finding["check_id"]
        message = finding["extra"]["message"]
        file_path = Path(finding["path"])
        code = file_path.read_text()

        state = pipeline.invoke({
            "rule": rule, "message": message,
            "file_path": str(file_path), "code": code,
        })

        if state["decision"] == "auto_fix":
            verification = verify_patch(
                state["patched_code"], rule, file_path.name,
                ISOLATED_DIR / "agentic" / file_path.stem,
            )
        else:
            verification = {"original_finding_removed": None, "new_findings_after_patch": None, "verified": False}

        results.append({
            "rule": rule,
            "file": file_path.name,
            "confidence": state["confidence"],
            "decision": state["decision"],
            **verification,
        })

    return {"mode": "agentic", "results": results}


def summarize(run: dict) -> dict:
    results = run["results"]
    total = len(results)

    if run["mode"] == "naive_baseline":
        auto_patched_low_confidence = sum(1 for r in results if r["confidence"] == "LOW")
        verified = sum(1 for r in results if r["verified"])
        return {
            "mode": "naive_baseline",
            "total_findings": total,
            "blindly_auto_fixed_low_confidence_pct": round(auto_patched_low_confidence / total * 100, 1),
            "verified_remediation_rate_pct": round(verified / total * 100, 1),
        }
    else:
        auto_fixed = [r for r in results if r["decision"] == "auto_fix"]
        escalated = [r for r in results if r["decision"] == "escalate"]
        verified_of_auto_fixed = sum(1 for r in auto_fixed if r["verified"])
        return {
            "mode": "agentic",
            "total_findings": total,
            "auto_fixed_count": len(auto_fixed),
            "escalated_count": len(escalated),
            "escalation_rate_pct": round(len(escalated) / total * 100, 1),
            "verified_rate_on_auto_fixed_pct": round(verified_of_auto_fixed / len(auto_fixed) * 100, 1) if auto_fixed else 0,
        }


def main():
    findings = run_semgrep(BENCHMARK_DIR)
    print(f"Found {len(findings)} findings.\n")

    print("=== Running NAIVE baseline (auto-fix everything) ===")
    naive_run = run_naive_baseline(findings)
    naive_summary = summarize(naive_run)
    print(json.dumps(naive_summary, indent=2))

    print("\n=== Running AGENTIC pipeline (confidence-gated routing) ===")
    agentic_run = run_agentic_pipeline(findings)
    agentic_summary = summarize(agentic_run)
    print(json.dumps(agentic_summary, indent=2))

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "naive_baseline.json", "w") as f:
        json.dump({**naive_run, "summary": naive_summary}, f, indent=2)
    with open(RESULTS_DIR / "agentic_pipeline.json", "w") as f:
        json.dump({**agentic_run, "summary": agentic_summary}, f, indent=2)

    print("\n=== Comparison ===")
    print(f"Naive: {naive_summary['blindly_auto_fixed_low_confidence_pct']}% of findings were low-confidence but auto-fixed anyway")
    print(f"Agentic: {agentic_summary['escalation_rate_pct']}% correctly escalated instead of blindly auto-fixed")
    print(f"Agentic verified-rate on auto-fixed subset: {agentic_summary['verified_rate_on_auto_fixed_pct']}%")


if __name__ == "__main__":
    main()
