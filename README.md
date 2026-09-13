# AI Security Automation Pipeline

An agentic security-remediation system: Semgrep finds real vulnerabilities, a LangGraph
agent triages each one and decides whether to auto-fix (high confidence) or escalate for
human review (low confidence), and every auto-fix is independently verified by re-running
Semgrep on the patched code in isolation.

Built to directly address a gap in a companion project (threat-intel-agent): hands-on
static-analysis-tool integration with AI-driven triage and CI/CD automation.

## Problem
Automated security remediation is only as trustworthy as its verification. Blindly
auto-patching every static-analysis finding risks silently shipping incomplete or wrong
fixes. This project measures that risk directly, and tests whether confidence-gated
routing (only auto-fix what you're sure about, escalate the rest) meaningfully improves
reliability.

## Architecture

Semgrep scan (16 real findings, 21 deliberately vulnerable Python files)
  -> LangGraph agent: triage each finding -> confidence assessment
       -> HIGH confidence -> auto-fix -> isolated patch -> Semgrep re-scan -> verified / not verified
       -> LOW confidence  -> escalate (no auto-fix, flagged for human review)

## Tech Stack
Python, Semgrep, LangGraph (genuine conditional routing via add_conditional_edges),
LangChain (langchain-groq), Pydantic (structured output), Groq API (openai/gpt-oss-120b),
GitHub Actions (CI), built and run in WSL2/Ubuntu.

## Evaluation Methodology
An earlier version of this idea compared LLM severity judgments against Semgrep's own
impact metadata field. That was abandoned after finding Semgrep does not publish an
objective rubric for LOW/MEDIUM/HIGH impact — each rule author sets it subjectively, so
agreement with it isn't a meaningful accuracy measure.

This project instead compares two pipeline strategies on the same real findings:
- Naive baseline: auto-patch every finding regardless of confidence.
- Agentic pipeline: LangGraph routes by the model's own stated confidence — only
  high-confidence findings get auto-patched; low-confidence ones are escalated.

Both are verified identically: re-run Semgrep on the patched file in isolation. A fix
only counts as verified if the original finding disappears AND no new finding is
introduced. This is a deterministic, external check — not an LLM's opinion of its own
success.

## Results (n=16 real Semgrep findings, 21 benchmark files)

| Pipeline | Findings auto-fixed | Verified-fix rate |
|---|---|---|
| Naive (fix everything) | 16/16 (100%) | 50.0% |
| Agentic (confidence-gated) | 7/16 (43.8%) | 100.0% |

The naive pipeline auto-patched every finding, but only half of those patches actually
verified clean on re-scan — meaning half of all blind fixes either failed to remove the
issue or introduced a new one, with no human ever knowing. The agentic pipeline only
auto-fixed findings it was confident about, correctly escalating 56.2% of findings
instead of guessing — and every auto-fixed finding verified clean.

## CI/CD
A GitHub Actions workflow (.github/workflows/security-pipeline.yml) runs the full
scan + triage + verification pipeline on every push and pull request, posts a live
summary to the GitHub Actions UI, and uploads full results as a downloadable artifact.
See a real passing run: https://github.com/MELL0WED/ai-security-automation-pipeline/actions/runs/34762336901

## Failure Cases / Limitations
- Sample size (16 findings, 21 files) is real but modest — limited by Semgrep's free-tier
  ruleset and project time constraints.
- Confidence is the LLM's own self-reported judgment, not independently calibrated
  against a ground truth — a genuinely low-confidence-but-actually-fine finding would
  still be escalated unnecessarily, and vice versa.
- Results vary slightly run-to-run even at temperature 0 (e.g., escalation rate was
  56.2% in one run and 50.0% in another) — LLM output isn't perfectly deterministic
  in practice, worth knowing rather than treating any single run's number as exact.
- Verification checks only that Semgrep's specific rule stops firing — does not confirm
  patched code still passes original functionality/tests (out of scope for this build).

## Running Locally
python3 run_pipeline.py

Requires GROQ_API_KEY in .env and Semgrep installed.
