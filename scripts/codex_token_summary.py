"""Summarize Codex token usage from a generated/ directory's stderr files."""

from __future__ import annotations
import glob
import sys


def parse_tokens_used(stderr: str) -> int | None:
    lines = stderr.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "tokens used" and i + 1 < len(lines):
            raw = lines[i + 1].strip().replace(",", "")
            if raw.isdigit():
                return int(raw)
    return None


def main(gen_dir: str) -> None:
    files = glob.glob(f"{gen_dir}/*.codex_stderr.txt")
    if not files:
        return
    rows: list[tuple[str, int]] = []
    for f in files:
        component = f.replace(".codex_stderr.txt", "").split("/")[-1]
        try:
            tokens = parse_tokens_used(open(f).read())
        except Exception:
            tokens = None
        if tokens is not None:
            rows.append((component, tokens))
    if not rows:
        return
    total = sum(t for _, t in rows)
    avg = total // len(rows)
    top = sorted(rows, key=lambda x: -x[1])[:3]
    print(f"Tokens: {total:,} total, {avg:,} avg ({len(rows)} components)")
    for comp, t in top:
        print(f"  {t:>8,}  {comp}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
