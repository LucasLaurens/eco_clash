"""Naming rule, made executable: every function name starts with an action verb, no one-letter names.

Scans GDScript (src/, tests/) with a line parser and Python (tools/) with the ast module.
Usage (from the repo root):  python3 tools/ci/check_naming.py
Exit code 1 with one line per offence.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# First word of a function name. A verb that is true for what the function does, never a noun.
VERBS = frozenset(
    """
    add animate append apply assert attach bind build can cancel change check choose clear collect compute
    configure confirm convert count crop create decide decode delete dispose draw drop emit encode ensure fill find
    finish format freeze generate get has hide hit instrument is jump knock land launch list load lose main
    make map measure merge mix move open paint parse paste pause place play press print put quit read receive
    refresh register remove render repeat reset resolve respawn resume run save scale scan search select set
    should show solve sort spawn split start step sync test tick tint to trigger try update would write
""".split()
)

# Engine-owned or framework-owned names: Godot virtuals, Python dunders.
GODOT_VIRTUALS = frozenset(
    {
        "_ready",
        "_init",
        "_process",
        "_physics_process",
        "_input",
        "_unhandled_input",
        "_enter_tree",
        "_exit_tree",
        "_draw",
        "_notification",
        "_to_string",
    }
)
SHORT_NAMES_ALLOWED = frozenset({"x", "y", "_"})

GD_FUNC = re.compile(r"^\s*(?:@\w+\s+)*(?:static\s+)?func\s+(\w+)\s*\(")
GD_VAR = re.compile(r"^\s*(?:@\w+\s+)*(?:static\s+)?var\s+(\w+)")
GD_FOR = re.compile(r"^\s*for\s+(\w+)\s*(?::\s*[\w\[\]]+)?\s+in\b")
GD_PARAMS = re.compile(r"func\s*\w*\s*\(([^)]*)\)")


def check_function_name(name: str) -> str | None:
    """Returns why the name breaks the rule, or None when it is fine."""
    if name in GODOT_VIRTUALS or name.startswith("_on_") or (name.startswith("__") and name.endswith("__")):
        return None
    first_word = name.lstrip("_").split("_")[0]
    if first_word in VERBS:
        return None
    return f"function '{name}' does not start with an action verb ('{first_word}')"


def check_short_name(name: str) -> str | None:
    if len(name) == 1 and name not in SHORT_NAMES_ALLOWED:
        return f"one-letter name '{name}'"
    return None


def scan_gdscript(path: Path) -> list[str]:
    """O(lines) time, O(1) extra space per line."""
    offences: list[str] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        reasons: list[str | None] = []
        if function := GD_FUNC.match(line):
            reasons.append(check_function_name(function.group(1)))
        for pattern in (GD_VAR, GD_FOR):
            if variable := pattern.match(line):
                reasons.append(check_short_name(variable.group(1)))
        for params in GD_PARAMS.finditer(line):
            for param in filter(None, (part.strip() for part in params.group(1).split(","))):
                reasons.append(check_short_name(re.split(r"[\s:=]", param)[0]))
        offences.extend(f"{path.relative_to(ROOT)}:{number}: {reason}" for reason in reasons if reason)
    return offences


def scan_python(path: Path) -> list[str]:
    """O(nodes) time over the module's syntax tree."""
    offences: list[str] = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        reason = None
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_property = any(
                isinstance(decorator, ast.Name) and decorator.id == "property" for decorator in node.decorator_list
            )
            reason = None if is_property else check_function_name(node.name)
            for argument in node.args.args + node.args.kwonlyargs:
                offences.extend(_format(path, node.lineno, check_short_name(argument.arg)))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            reason = check_short_name(node.id)
        offences.extend(_format(path, getattr(node, "lineno", 0), reason))
    return offences


def _format(path: Path, line: int, reason: str | None) -> list[str]:
    return [f"{path.relative_to(ROOT)}:{line}: {reason}"] if reason else []


def collect_offences(root: Path = ROOT) -> list[str]:
    offences: list[str] = []
    for folder in ("src", "tests"):
        for path in sorted((root / folder).rglob("*.gd")):
            offences.extend(scan_gdscript(path))
    for path in sorted((root / "tools").rglob("*.py")):
        offences.extend(scan_python(path))
    return offences


def main() -> int:
    offences = collect_offences()
    for offence in offences:
        print(offence)
    print(f"naming: {len(offences)} offence(s)")
    return 1 if offences else 0


if __name__ == "__main__":
    sys.exit(main())
