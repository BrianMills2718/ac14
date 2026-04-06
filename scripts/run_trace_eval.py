"""Run trace_eval against an AC14 attempt artifact.

Builds stage_outputs from the attempt directory using trace_eval_adapter,
writes a temporary outputs.json, and invokes trace-eval run.

Usage:
    python scripts/run_trace_eval.py .ac14_out/gate_4 4 1 --case tests/fixtures/cases/ac14_zeta_options/full_pipeline.yaml
    python scripts/run_trace_eval.py .ac14_out/gate_4 4 1 --case ... --json
    python scripts/run_trace_eval.py .ac14_out/gate_4 4 1 --case ... --evidence-dir .ac14_out/trace_eval_evidence/
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

# Ensure ac14 package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from ac14.trace_eval_adapter import build_stage_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output_dir", type=Path, help="Gate output directory (e.g. .ac14_out/gate_4)")
    parser.add_argument("trial", type=int, help="Trial number")
    parser.add_argument("attempt", type=int, help="Attempt number")
    parser.add_argument("--case", required=True, metavar="PATH", help="PipelineCase YAML file")
    parser.add_argument("--json", action="store_true", help="Emit JSON TraceResult output")
    parser.add_argument("--evidence-dir", metavar="DIR", default=None, help="Write evidence artifact to this directory")
    args = parser.parse_args()

    attempt_dir = args.output_dir / f"trial_{args.trial}" / "ac14" / f"attempt_{args.attempt}"
    if not attempt_dir.exists():
        print(f"ERROR: Attempt dir not found: {attempt_dir}", file=sys.stderr)
        sys.exit(1)

    stage_outputs = build_stage_outputs(attempt_dir)

    # Write to a temp file for trace-eval CLI
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(stage_outputs, tmp, indent=2)
        tmp_path = tmp.name

    # Use python -m to avoid PATH lookup issues across venvs
    cmd = [sys.executable, "-m", "trace_eval.cli", "run", "--case", str(args.case), "--outputs", tmp_path]
    if args.json:
        cmd.append("--json")
    if args.evidence_dir:
        cmd.extend(["--evidence-dir", str(args.evidence_dir)])

    result = subprocess.run(cmd)  # noqa: S603
    Path(tmp_path).unlink(missing_ok=True)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
