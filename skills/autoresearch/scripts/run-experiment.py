#!/usr/bin/env python3
"""
Autoresearch result parser and recorder.
Extracts metrics from experiment output and appends to results.tsv.
"""

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

def extract_metric(output: str, pattern: str) -> float | None:
    """Extract metric value from command output using various strategies."""
    strategies = [
        # Direct grep pattern like "val_loss: 0.95"
        lambda o, p: float(re.search(rf'{re.escape(p)}\s*[:=]\s*([0-9]+\.?[0-9]*)', o).group(1))
            if re.search(rf'{re.escape(p)}\s*[:=]\s*([0-9]+\.?[0-9]*)', o) else None,
        # Number after a keyword
        lambda o, p: float(re.search(rf'{re.escape(p)}\s+([0-9]+\.?[0-9]*)', o).group(1))
            if re.search(rf'{re.escape(p)}\s+([0-9]+\.?[0-9]*)', o) else None,
        # Last number on lines containing keyword
        lambda o, p: float(re.findall(rf'.*{re.escape(p)}.*?([0-9]+\.?[0-9]*)', o)[-1])
            if re.findall(rf'.*{re.escape(p)}.*?([0-9]+\.?[0-9]*)', o) else None,
    ]
    for strategy in strategies:
        try:
            result = strategy(output, pattern)
            if result is not None:
                return result
        except (ValueError, IndexError):
            continue
    return None


def get_git_commit(short: bool = True) -> str:
    """Get current git commit hash."""
    length = 7 if short else 40
    try:
        result = subprocess.run(
            ["git", "rev-parse", f"--short={length}", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "unknown"


def get_peak_memory_mb(pid: int) -> float:
    """Get peak memory usage of a process in MB (Linux only)."""
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmPeak:"):
                    kb = int(line.split()[1])
                    return round(kb / 1024, 1)
    except (FileNotFoundError, PermissionError, ValueError):
        pass
    return 0.0


def record_result(tsv_path: Path, commit: str, metric: float, memory_mb: float,
                  status: str, description: str):
    """Append a result row to results.tsv."""
    line = f"{commit}\t{metric:.6f}\t{memory_mb}\t{status}\t{description}\n"
    with open(tsv_path, "a") as f:
        f.write(line)


def run_experiment(command: str, timeout: int, cwd: str = ".") -> tuple[str, int, float, bool]:
    """Run experiment command and return (output, returncode, memory_mb, timed_out)."""
    start = time.time()
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=cwd
        )
        output = result.stdout + "\n" + result.stderr
        return output, result.returncode, 0.0, False
    except subprocess.TimeoutExpired:
        return f"TIMEOUT after {timeout}s", -1, 0.0, True
    except Exception as e:
        return f"ERROR: {e}", -1, 0.0, False


def main():
    parser = argparse.ArgumentParser(description="Run and record an autoresearch experiment")
    parser.add_argument("--command", "-c", help="Experiment command (overrides project.md)")
    parser.add_argument("--parse", "-p", help="Metric parse pattern (overrides project.md)")
    parser.add_argument("--direction", "-d", choices=["lower", "higher"], default="lower",
                        help="Is lower or higher better?")
    parser.add_argument("--timeout", "-t", type=int, default=600, help="Max seconds")
    parser.add_argument("--project-dir", default=".", help="Project directory")
    parser.add_argument("--description", default="", help="Experiment description")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--baseline", action="store_true", help="Record as baseline (keep)")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    tsv_path = project_dir / "autoresearch" / "results.tsv"

    if not tsv_path.exists():
        print(f"❌ Not initialized. Run init-project.py first.")
        sys.exit(1)

    command = args.command
    parse_pattern = args.parse

    # Read from project.md if not provided
    if not command or not parse_pattern:
        md_path = project_dir / "autoresearch" / "project.md"
        if not md_path.exists():
            print(f"❌ project.md not found")
            sys.exit(1)
        content = md_path.read_text()
        if not command:
            m = re.search(r'Command:\s*`(.+?)`', content)
            if not m:
                m = re.search(r'Command:\s*(.+)', content)
            command = m.group(1).strip() if m else None
        if not parse_pattern:
            m = re.search(r'Parse:\s*(.+)', content)
            parse_pattern = m.group(1).strip() if m else None

    if not command:
        print("❌ No experiment command specified")
        sys.exit(1)

    if args.dry_run:
        print(f"📋 Dry run:")
        print(f"   Command: {command}")
        print(f"   Parse: {parse_pattern or '(extract all numbers)'}")
        print(f"   Direction: {args.direction}")
        print(f"   Timeout: {args.timeout}s")
        print(f"   Description: {args.description or '(auto)'}")
        sys.exit(0)

    print(f"🚀 Running: {command}")
    print(f"   Timeout: {args.timeout}s")
    sys.stdout.flush()

    output, returncode, memory_mb, timed_out = run_experiment(
        command, args.timeout, cwd=str(project_dir)
    )

    elapsed = time.time() - start
    print(f"   Done in {elapsed:.1f}s")

    if timed_out:
        print(f"⏰ TIMEOUT — experiment killed")
        commit = get_git_commit()
        record_result(tsv_path, commit, 0.0, 0.0, "crash",
                      f"timeout after {args.timeout}s: {args.description}")
        sys.exit(1)

    if returncode != 0:
        # Try to extract metric anyway (some tools exit non-zero but still output results)
        print(f"⚠️  Exit code: {returncode}")

    # Extract metric
    metric = None
    if parse_pattern:
        metric = extract_metric(output, parse_pattern)

    if metric is None:
        # Fallback: try to find any reasonable number in output
        numbers = re.findall(r'(?:score|loss|accuracy|latency|time|error)[:\s=]+([0-9]+\.?[0-9]*)',
                            output, re.IGNORECASE)
        if numbers:
            metric = float(numbers[-1])
            print(f"   ⚠️  Fallback extraction: {metric}")

    if metric is None:
        print(f"❌ Could not extract metric from output")
        print(f"   Last 20 lines of output:")
        for line in output.strip().split("\n")[-20:]:
            print(f"   {line}")
        commit = get_git_commit()
        record_result(tsv_path, commit, 0.0, 0.0, "crash",
                      f"metric parse failed: {args.description}")
        sys.exit(1)

    print(f"   Metric: {metric:.6f}")

    # Determine status
    status = "keep" if args.baseline else "unknown"
    commit = get_git_commit()

    # Read previous best for comparison
    previous_best = None
    if tsv_path.exists() and not args.baseline:
        lines = tsv_path.read_text().strip().split("\n")[1:]  # skip header
        for line in lines:
            if line.strip():
                parts = line.split("\t")
                if len(parts) >= 2 and parts[3] == "keep":
                    try:
                        val = float(parts[1])
                        if previous_best is None:
                            previous_best = val
                        elif args.direction == "lower" and val < previous_best:
                            previous_best = val
                        elif args.direction == "higher" and val > previous_best:
                            previous_best = val
                    except ValueError:
                        pass

    if previous_best is not None:
        if args.direction == "lower":
            improved = metric < previous_best
            diff = previous_best - metric
        else:
            improved = metric > previous_best
            diff = metric - previous_best

        status = "keep" if improved else "discard"
        symbol = "📈" if improved else "📉"
        print(f"   {symbol} vs best ({previous_best:.6f}): {'+' if diff > 0 else ''}{diff:.6f}")
    else:
        print(f"   📝 Baseline recorded")

    description = args.description or f"metric={metric:.6f}"
    record_result(tsv_path, commit, metric, memory_mb, status, description)
    print(f"   Status: {status}")
    print(f"   Recorded to {tsv_path}")


if __name__ == "__main__":
    main()
