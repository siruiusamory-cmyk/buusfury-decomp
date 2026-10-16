"""Repository purity: where each kind of file is allowed to live.

The public repository mixes a shipping product, a desktop editor, a reverse
engineering laboratory, a runtime toolbox and a progress site. Each of those has
a home, and the value of naming the homes is that a file in the wrong one is
usually a mistake that is cheaper to catch than to debug:

* a research probe that drifted into the shipping package,
* a test that was placed inside a production package,
* generated output or a machine-local ROM that was committed by accident,
* an editor artifact checked into the site's source.

Every rule here answers one question with a fact git can prove, so the report is
deterministic and the same tree always produces the same document. A rule may be
a hard violation, which fails the run, or an observation, which does not: the
shipping package is large, and a size measurement is a reading list rather than
a defect.

This module does not decide what the project should contain. It decides where a
file may live once the project has decided to contain it.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

from tools.quality import _local_state_paths as _local_state

#: Bumped when the report document's shape changes in a way a reader must notice.
SCHEMA = 1

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: The directory that ships as the product. Everything else is either support
#: tooling, documentation, tests, or repository configuration.
SHIPPING_ROOT = "tools/webfoot"

#: The desktop application. It presents the shipping package, so it may use it.
PRODUCT_ROOT = "tools/dragonbyte"

#: The beta desktop package. It is reference for the application, never a
#: dependency of it: what it proved lives in the SDK or in the application.
BETA_ROOT = "tools.webfoot.workbench"

#: Top-level directories a tracked file may live under. A new top-level
#: directory is a deliberate decision, so it is listed here rather than inferred.
ALLOWED_ROOTS = (
    ".github",
    "ci",
    "config",
    "docs",
    "public",
    "scripts",
    "src",
    "tests",
    "tools",
)

#: Naming that marks a one-off research probe. A probe belongs in tools/runtime
#: or tools/research, where it is allowed to need a particular save state and a
#: particular memory layout; it does not belong in the shipping package, where
#: every module is expected to have a current contract.
PROBE_NAME = re.compile(r"(?:^|/)(?:p\d{3}_|rom\d{3}_|toolkit\d{3}_|auto\d{3}_).*|.*_probe\.[a-z]+$")

#: Suffixes that are never project content. A tracked file with one of these is
#: either proprietary or a generated derivative.
NEVER_TRACKED_SUFFIXES = (
    ".gba", ".agb", ".gbc", ".sav", ".srm", ".mss", ".ss0", ".ss1", ".ss2",
    ".ss3", ".state", ".dump", ".raw",
)

#: Local working state. These are ignored from .git/info/exclude rather than the
#: tracked ignore file, so the rule below is what keeps one from being published.
#: The names themselves live encoded in ``_local_state_paths`` so that the guard
#: is not a place the forbidden vocabulary appears in public tracked text.
LOCAL_STATE_PATHS = _local_state.LOCAL_STATE_NAMES
LOCAL_STATE_PREFIXES = _local_state.LOCAL_STATE_PREFIXES

#: Import roots that only a test may use. A shipping module that imports one has
#: taken a development dependency into the product.
TEST_ONLY_IMPORTS = ("pytest", "hypothesis", "tests")

#: Site source is TypeScript and Astro; the SDK is Python. Neither may appear in
#: the other's tree.
SITE_SUFFIXES = (".astro", ".ts", ".tsx", ".css")


def _git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(arguments)} failed: {result.stderr.strip()}")
    return result.stdout


def tracked_files() -> list[str]:
    return sorted(name for name in _git("ls-files", "-z").split("\0") if name)


def _is_shipping(path: str) -> bool:
    return path == SHIPPING_ROOT or path.startswith(SHIPPING_ROOT + "/")


def _rule_top_level_roots(files: list[str]) -> list[dict]:
    findings = []
    for name in files:
        if "/" not in name:
            continue
        root = name.split("/", 1)[0]
        if root not in ALLOWED_ROOTS:
            findings.append(
                {
                    "rule": "roots",
                    "path": name,
                    "detail": f"lives under {root}/, which is not a declared top-level root",
                }
            )
    return findings


def _rule_python_package_source(files: list[str]) -> list[dict]:
    """Every file under the shipping package is Python or its packaged data."""
    findings = []
    for name in files:
        if not _is_shipping(name):
            continue
        suffix = Path(name).suffix.lower()
        if suffix in {".py", ".yaml", ".yml"} or name.endswith("__init__.py"):
            continue
        findings.append(
            {
                "rule": "shipping-language",
                "path": name,
                "detail": f"unexpected {suffix or 'extensionless'} file in the shipping package",
            }
        )
    return findings


def _rule_no_tests_in_production(files: list[str]) -> list[dict]:
    findings = []
    for name in files:
        if not _is_shipping(name):
            continue
        stem = Path(name).stem
        if stem.startswith("test_") or stem.endswith("_test") or "/tests/" in name:
            findings.append(
                {
                    "rule": "no-tests-in-production",
                    "path": name,
                    "detail": "test module inside the shipping package; tests belong under tests/",
                }
            )
    return findings


def _rule_no_probes_in_production(files: list[str]) -> list[dict]:
    findings = []
    for name in files:
        if not _is_shipping(name):
            continue
        if PROBE_NAME.search(name):
            findings.append(
                {
                    "rule": "no-probes-in-production",
                    "path": name,
                    "detail": "research-probe naming inside the shipping package",
                }
            )
    return findings


def _rule_nothing_generated_is_tracked(files: list[str]) -> list[dict]:
    """A tracked file that the ignore rules match was committed by accident."""
    ignored = _git("ls-files", "-i", "-c", "--exclude-standard", "-z").split("\0")
    return [
        {
            "rule": "nothing-generated-tracked",
            "path": name,
            "detail": "tracked even though an ignore rule matches it",
        }
        for name in sorted(entry for entry in ignored if entry)
    ]


def _rule_no_proprietary_artifacts(files: list[str]) -> list[dict]:
    findings = []
    for name in files:
        lowered = name.lower()
        if lowered.endswith(NEVER_TRACKED_SUFFIXES):
            findings.append(
                {
                    "rule": "no-proprietary-artifacts",
                    "path": name,
                    "detail": "proprietary or generated binary with a never-tracked suffix",
                }
            )
        if lowered.startswith("extern/") or "/extern/" in lowered:
            findings.append(
                {
                    "rule": "no-upstream-checkout",
                    "path": name,
                    "detail": "upstream checkout committed instead of fetched into an ignored directory",
                }
            )
    return findings


def _rule_no_local_state_tracked(files: list[str]) -> list[dict]:
    findings = []
    for name in files:
        if name in LOCAL_STATE_PATHS or name.startswith(LOCAL_STATE_PREFIXES):
            findings.append(
                {
                    "rule": "no-local-state",
                    "path": name,
                    "detail": "local working state is tracked; it belongs in .git/info/exclude",
                }
            )
    return findings


def _rule_site_and_sdk_are_separate(files: list[str]) -> list[dict]:
    findings = []
    for name in files:
        if name.startswith("src/") and name.endswith(".py"):
            findings.append(
                {
                    "rule": "site-sdk-separation",
                    "path": name,
                    "detail": "Python in the progress-site tree",
                }
            )
        if _is_shipping(name) and name.lower().endswith(SITE_SUFFIXES):
            findings.append(
                {
                    "rule": "site-sdk-separation",
                    "path": name,
                    "detail": "site asset inside the shipping package",
                }
            )
    return findings


def _rule_no_test_imports_in_production(files: list[str]) -> list[dict]:
    findings = []
    pattern = re.compile(
        r"^\s*(?:import|from)\s+(" + "|".join(TEST_ONLY_IMPORTS) + r")\b"
    )
    for name in files:
        if not _is_shipping(name) or not name.endswith(".py"):
            continue
        try:
            text = (REPOSITORY_ROOT / name).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                findings.append(
                    {
                        "rule": "no-test-imports-in-production",
                        "path": name,
                        "line": number,
                        "detail": f"test-only import in shipping source: {line.strip()[:80]}",
                    }
                )
    return findings


def _module_name(name: str) -> str:
    """The dotted module name of a tracked Python file."""
    path = name[: -len(".py")]
    if path.endswith("/__init__"):
        path = path[: -len("/__init__")]
    return path.replace("/", ".")


def _imported_modules(name: str, tree: ast.AST) -> list[tuple[str, int]]:
    """Every module a file imports, as ``(dotted name, line)`` pairs.

    A relative import is resolved against the file's own package, so a spelling
    that never writes the target's name still resolves to it. A name imported
    FROM a package resolves to the package joined with that name, so
    ``from tools.webfoot import workbench`` counts as importing
    ``tools.webfoot.workbench``.
    """
    module = _module_name(name)
    package = (
        module if name.endswith("/__init__.py") else module.rsplit(".", 1)[0]
    )
    found: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend((alias.name, node.lineno) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = package.split(".")
                # Level 1 is the file's own package; each further level climbs one.
                climb = node.level - 1
                parts = parts[: len(parts) - climb] if climb else parts
                target = ".".join(part for part in parts if part)
                if node.module:
                    target = f"{target}.{node.module}" if target else node.module
            else:
                target = node.module or ""
            if not target:
                continue
            found.append((target, node.lineno))
            found.extend(
                (f"{target}.{alias.name}", node.lineno) for alias in node.names
            )
    return found


def _rule_import_direction(files: list[str]) -> list[dict]:
    """The import direction between the application and the shipping package.

    One edge each way, and both are load-bearing:

    * nothing under the shipping package imports the application, because the
      SDK does not depend on the thing that presents it;
    * the application never imports the beta desktop package, because the beta
      is reference rather than a dependency.

    The file is parsed, so a module name inside a comment or a string can
    neither satisfy the rule nor trip it. The ceiling that follows from parsing
    is a name assembled at run time: an import built from a variable, a
    concatenation or a call is outside what a parse can see.
    """
    # The roots above are paths; an import names a module, so the forbidden
    # side of each edge is the dotted spelling of the same root.
    directions = (
        (
            SHIPPING_ROOT,
            PRODUCT_ROOT.replace("/", "."),
            "the shipping package must not import the application",
        ),
        (
            PRODUCT_ROOT,
            BETA_ROOT.replace("/", "."),
            "the application must not import the beta desktop package",
        ),
    )
    findings = []
    for name in files:
        if not name.endswith(".py"):
            continue
        match = next(
            (
                (forbidden, detail)
                for root, forbidden, detail in directions
                if name == root or name.startswith(root + "/")
            ),
            None,
        )
        if match is None:
            continue
        forbidden, detail = match
        try:
            source = (REPOSITORY_ROOT / name).read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        for imported, line in _imported_modules(name, tree):
            if imported == forbidden or imported.startswith(forbidden + "."):
                findings.append(
                    {
                        "rule": "import-direction",
                        "path": name,
                        "line": line,
                        "detail": detail,
                    }
                )
    return findings


def _observation_large_modules(files: list[str], limit: int = 100_000) -> list[dict]:
    """A very large module is worth a reviewer's attention, never a failure."""
    observations = []
    for name in files:
        if not _is_shipping(name) or not name.endswith(".py"):
            continue
        try:
            size = (REPOSITORY_ROOT / name).stat().st_size
        except OSError:
            continue
        if size > limit:
            observations.append(
                {
                    "rule": "large-module",
                    "path": name,
                    "detail": f"{size} bytes, above the {limit}-byte reading threshold",
                }
            )
    return observations


RULES = (
    _rule_top_level_roots,
    _rule_python_package_source,
    _rule_no_tests_in_production,
    _rule_no_probes_in_production,
    _rule_nothing_generated_is_tracked,
    _rule_no_proprietary_artifacts,
    _rule_no_local_state_tracked,
    _rule_site_and_sdk_are_separate,
    _rule_no_test_imports_in_production,
    _rule_import_direction,
)


def check(root: Path | None = None) -> dict:
    """Run every rule over the tracked tree and return the report document."""
    base = root or REPOSITORY_ROOT
    if base != REPOSITORY_ROOT:
        raise ValueError("the repository purity check runs against its own checkout")
    files = tracked_files()
    violations: list[dict] = []
    for rule in RULES:
        violations.extend(rule(files))
    violations.sort(key=lambda item: (item["path"], item["rule"], item.get("line", 0)))
    observations = sorted(
        _observation_large_modules(files), key=lambda item: item["path"]
    )
    counts: dict[str, int] = {}
    for item in violations:
        counts[item["rule"]] = counts.get(item["rule"], 0) + 1
    return {
        "schema": SCHEMA,
        "files": len(files),
        "violations": violations,
        "observations": observations,
        "rule_counts": dict(sorted(counts.items())),
    }


def _render(report: dict, stream) -> None:
    print(
        f"repository purity: {report['files']} tracked files, "
        f"{len(report['violations'])} violation(s), "
        f"{len(report['observations'])} observation(s)",
        file=stream,
    )
    for item in report["violations"]:
        where = f"{item['path']}:{item['line']}" if item.get("line") else item["path"]
        print(f"  {where}: {item['rule']}: {item['detail']}", file=stream)
    if report["observations"]:
        print("observations (a reading list, never a failure):", file=stream)
        for item in report["observations"]:
            print(f"  {item['path']}: {item['rule']}: {item['detail']}", file=stream)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="architecture",
        description="Check that every tracked file lives where its kind belongs.",
    )
    parser.add_argument("--json", metavar="PATH", help="write the report document as JSON")
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="report violations but always exit 0",
    )
    arguments = parser.parse_args(argv)

    try:
        report = check()
    except (RuntimeError, ValueError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2

    if arguments.json:
        Path(arguments.json).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    _render(report, sys.stdout)

    if report["violations"] and not arguments.no_fail:
        print(
            "\nA tracked file is in the wrong place. Move it to its home or "
            "extend the rules in tools/quality/architecture.py deliberately.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
