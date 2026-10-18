"""GDScript function coverage: which functions of src/ ran during the test suites.

Godot 4 has no line-coverage tool, so this measures the next best thing, honestly named:
1. copy the project to a temp folder (the real sources are never touched);
2. insert `CoverageProbe.hit("<file>:<function>")` as the first statement of every function in src/;
3. run every test suite (unit + features) headless in the copy;
4. report covered / total functions per file, and fail under a threshold.

Usage (from the repo root):
    python3 tools/ci/gd_coverage.py [--godot godot] [--fail-under 80]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INSTRUMENTED_DIR = "src"
COPY_IGNORE = shutil.ignore_patterns(".git", "graft", "__pycache__")
RUNNER_PATH = "tests/test_runner.gd"
RUNNER_QUIT = "\tget_tree().quit(1 if _failed > 0 or _total == 0 else 0)"
REPORT_ENV = "GD_COVERAGE_OUT"
PROBE_PATH = "tests/coverage_probe.gd"
PROBE_SOURCE = """class_name CoverageProbe
extends RefCounted
## Written by tools/ci/gd_coverage.py into a throwaway copy of the project. Never committed.

static var hits: Dictionary = {}


static func hit(function_id: String) -> void:
	hits[function_id] = true


static func write_report(path: String) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(hits.keys()))
"""
FUNC_HEADER = re.compile(r"^(?P<indent>\s*)(?:@\w+\s+)*(?:static\s+)?func\s+(?P<name>\w+)\s*\(")


@dataclass
class FileCoverage:
    path: str
    functions: list[str] = field(default_factory=list)
    hits: set[str] = field(default_factory=set)

    @property
    def covered(self) -> int:
        return sum(1 for function in self.functions if function in self.hits)

    @property
    def missed(self) -> list[str]:
        return [function for function in self.functions if function not in self.hits]


def instrument_source(source: str, relative_path: str) -> tuple[str, list[str]]:
    """Returns the source with a probe at the top of each function body, and the function ids.

    Handles signatures wrapped over several lines (gdformat does that past the line length).
    Abstract functions have no body and are not counted. O(lines) time and space.
    """
    lines = source.split("\n")
    output: list[str] = []
    function_ids: list[str] = []
    index = 0
    while index < len(lines):
        header = FUNC_HEADER.match(lines[index])
        if not header or lines[index].lstrip().startswith("#"):
            output.append(lines[index])
            index += 1
            continue
        end = _find_header_end(lines, index)
        output.extend(lines[index : end + 1])
        index = end + 1
        if not lines[end].rstrip().endswith(":"):
            continue
        body_start = index
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1
        if body_start >= len(lines):
            continue
        body_indent = lines[body_start][: len(lines[body_start]) - len(lines[body_start].lstrip())]
        if len(body_indent) <= len(header.group("indent")):
            continue
        function_id = f"{relative_path}:{header.group('name')}"
        function_ids.append(function_id)
        output.extend(lines[index:body_start])
        output.append(f'{body_indent}CoverageProbe.hit("{function_id}")')
        index = body_start
    return "\n".join(output), function_ids


def _find_header_end(lines: list[str], start: int) -> int:
    """Index of the line closing the signature: parentheses balanced again."""
    depth = 0
    for index in range(start, len(lines)):
        depth += lines[index].count("(") - lines[index].count(")")
        if depth <= 0:
            return index
    return start


def instrument_project(copy_root: Path) -> list[FileCoverage]:
    files: list[FileCoverage] = []
    for path in sorted((copy_root / INSTRUMENTED_DIR).rglob("*.gd")):
        relative_path = path.relative_to(copy_root).as_posix()
        instrumented, function_ids = instrument_source(path.read_text(encoding="utf-8"), relative_path)
        path.write_text(instrumented, encoding="utf-8")
        files.append(FileCoverage(relative_path, function_ids))
    (copy_root / PROBE_PATH).write_text(PROBE_SOURCE, encoding="utf-8")
    runner = copy_root / RUNNER_PATH
    runner_source = runner.read_text(encoding="utf-8")
    if RUNNER_QUIT not in runner_source:
        raise SystemExit(f"{RUNNER_PATH} changed: cannot find the quit line to hook the coverage report")
    hook = f'\tCoverageProbe.write_report(OS.get_environment("{REPORT_ENV}"))\n{RUNNER_QUIT}'
    runner.write_text(runner_source.replace(RUNNER_QUIT, hook), encoding="utf-8")
    return files


def run_tests(copy_root: Path, godot: str, report_path: Path) -> int:
    subprocess.run([godot, "--headless", "--path", str(copy_root), "--import"], check=False, capture_output=True)
    environment = {**os.environ, REPORT_ENV: str(report_path)}
    command = [godot, "--headless", "--path", str(copy_root), "--fixed-fps", "60", "res://tests/test_runner.tscn"]
    result = subprocess.run(command, env=environment, check=False, capture_output=True, text=True)
    print(result.stdout[-2000:])
    return result.returncode


def format_report(files: list[FileCoverage]) -> tuple[str, float]:
    total = sum(len(file.functions) for file in files)
    covered = sum(file.covered for file in files)
    percent = 100.0 * covered / total if total else 0.0
    rows = ["| File | Functions | Covered | % |", "|---|---|---|---|"]
    for file in files:
        file_percent = 100.0 * file.covered / len(file.functions) if file.functions else 100.0
        rows.append(f"| `{file.path}` | {len(file.functions)} | {file.covered} | {file_percent:.0f} |")
    rows.append(f"| **Total** | **{total}** | **{covered}** | **{percent:.1f}** |")
    missed = [function for file in files for function in file.missed]
    report = "\n".join(["## GDScript function coverage", "", *rows, "", f"Missed ({len(missed)}):", *missed])
    return report, percent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--godot", default=os.environ.get("GODOT", "godot"))
    parser.add_argument("--fail-under", type=float, default=0.0)
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory() as temp_dir:
        copy_root = Path(temp_dir) / "project"
        shutil.copytree(ROOT, copy_root, ignore=COPY_IGNORE)
        files = instrument_project(copy_root)
        report_path = Path(temp_dir) / "hits.json"
        tests_exit = run_tests(copy_root, arguments.godot, report_path)
        if not report_path.exists():
            print("coverage: no report written, the test run crashed")
            return 1
        hits = set(json.loads(report_path.read_text(encoding="utf-8")))
    for file in files:
        file.hits = hits
    report, percent = format_report(files)
    print(report)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(report + "\n")
    if tests_exit != 0:
        print("coverage: the test suites failed")
        return tests_exit
    if percent < arguments.fail_under:
        print(f"coverage: {percent:.1f}% is under the {arguments.fail_under:.0f}% threshold")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
