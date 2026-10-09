"""Launch-site coverage: a new mGBA launcher cannot arrive unnoticed.

This is the repository's enforcement that replaced the textual source scan that
used to live in ``tests/unit/test_mgba_identity_gate.py``, which read
``tools/runtime/*.py`` with two regular expressions. That predicate could not
see a launcher written anywhere else in the repository, could not resolve an import
alias, and could not tell where a gate sits inside a function.

Discovery here is syntactic, not textual:

- every tracked ``.py`` file is parsed with ``ast``, and every call whose
  resolved dotted name is one of the launch spellings below is a discovered
  site, with import aliases resolved (``import subprocess as sp`` is seen, and
  ``service.run`` is not mistaken for ``subprocess.run``);
- every tracked ``.ps1`` file that references mGBA and starts a process is a
  discovered site, with the executable it starts read from ``-FilePath``.

Each discovered site must then satisfy the repository policy:

- it is registered in ``tools.runtime.mgba_identity.LAUNCH_SITES`` (imported,
  never duplicated here), and an mGBA-target launch inside an already-registered
  file must additionally sit under a function the registry's anchor names; or
- it is listed in ``NON_MGBA_SITES``, an explicit table keyed by
  ``(path, anchor, launched target)`` with a written reason. A bare path, a
  wildcard and a directory prefix are all rejected shapes; and
- independently of that table, a site whose launched target mentions mGBA is
  never exempt. That trigger is what stops the table from becoming the new hole.

Registration is not the whole requirement: the mechanism it must prove is read
from the site's ``proof`` field (Amendment 1), never from the taxonomy string,
and it must be placed so it actually covers a launch. A gate moved inside a
conditional, into a helper function, or into another module fails.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Iterable, Mapping, Sequence

import pytest

import tools.runtime.mgba_identity as identity

ROOT = Path(__file__).resolve().parents[2]

#: Every spelling that puts a process on this machine.
LAUNCH_CALLS = frozenset(
    {
        "subprocess.Popen",
        "subprocess.run",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "os.system",
        "os.popen",
        "os.startfile",
        "asyncio.create_subprocess_exec",
        "asyncio.create_subprocess_shell",
    }
)

#: Which mechanism proves identity for each frozen proof kind. Keyed off the
#: proof, never off the taxonomy string: the PowerShell Lua vehicle and the
#: patched SDL build are both `instrumented-required` and need different gates.
GATE_FOR_PROOF: Mapping[str, str] = {
    identity.EXECUTABLE_DIGEST: "require_mgba_build",
    identity.INSTRUMENTED_MANIFEST: "verify_instrumented_mgba",
}
GATE_NAMES = frozenset(GATE_FOR_PROOF.values())

MGBA = "mgba"
POWERSHELL_VERSION_TOKENS = ("VersionInfo.FileVersion", "--version")
POWERSHELL_DIGEST_TOKENS = ("Get-FileHash", "MGBSha256")
PYTHON_VERSION_TOKEN = "--version"
POWERSHELL_START = re.compile(
    r"Start-Process|\[System\.Diagnostics\.Process\]::Start", re.IGNORECASE
)
#: PowerShell's call operator also creates a process, and a launcher written
#: with `& $exe` is invisible to the two cmdlets above. `tools/mgba_probe/build.ps1`
#: starts the instrumented build this way.
POWERSHELL_CALL = re.compile(r"&\s+([^\s;|&]+)")
POWERSHELL_FILE_PATH = re.compile(r"-FilePath\s+([^\s`]+)", re.IGNORECASE)

#: Process starts in this repository that cannot start mGBA, keyed by
#: ``(path, anchor, launched target)``. The key is the whole point: an exemption
#: covers one call site, never a file, so a launcher added into an exempt file
#: is still reported. Every entry carries the reason it is not an mGBA launch.
#:
#: This table is a maintenance cost by design. A new ``subprocess.run`` in any
#: tracked file - a test shelling out to git included - must be classified here
#: with a reason, or `test_the_current_tree_has_no_unregistered_launch_site`
#: fails. That is what makes the exemption explicit rather than implicit.
NON_MGBA_SITES: Mapping[tuple[str, str, str], str] = {
    ("tools/runtime/stage_text_handle_001.ps1", "&", "powershell"):
        "delegates to the tracked toolkit session launcher; it starts no emulator",
    ("tools/runtime/stage_toolkit034_trial.ps1", "&", "powershell"):
        "delegates to the tracked toolkit session launcher; it starts no emulator",
    ("tests/integration/test_logx_connector_rom.py",
     "test_documented_module_invocation_emits_the_canonical_report",
     "sys.executable"):
        "runs this interpreter on a logx probe module; it starts no emulator",
    ("tests/integration/test_logx_connector_rom.py",
     "test_the_probe_refuses_a_non_canonical_file",
     "sys.executable"):
        "runs this interpreter on a logx probe module; it starts no emulator",
    ("tests/integration/test_logx_layer_rom.py",
     "test_documented_module_invocation_emits_the_canonical_report",
     "sys.executable"):
        "runs this interpreter on a logx probe module; it starts no emulator",
    ("tests/integration/test_logx_layer_rom.py",
     "test_the_probe_refuses_a_non_canonical_file",
     "sys.executable"):
        "runs this interpreter on a logx probe module; it starts no emulator",
    ("tests/integration/test_logx_map_record_rom.py",
     "test_documented_module_invocation_emits_the_canonical_report",
     "sys.executable"):
        "runs this interpreter on a logx probe module; it starts no emulator",
    ("tests/integration/test_logx_map_render_rom.py",
     "test_documented_module_invocation_emits_the_canonical_report",
     "sys.executable"):
        "runs this interpreter on a logx probe module; it starts no emulator",
    ("tests/integration/test_logx_tile_rom.py",
     "test_documented_module_invocation_emits_the_canonical_report",
     "sys.executable"):
        "runs this interpreter on a logx probe module; it starts no emulator",
    ("tests/integration/test_logx_tile_rom.py",
     "test_the_probe_refuses_a_non_canonical_file",
     "sys.executable"):
        "runs this interpreter on a logx probe module; it starts no emulator",
    ("tests/integration/test_warp_randomizer_rom.py",
     "test_the_manifest_is_the_same_in_a_fresh_interpreter",
     "sys.executable"):
        "reruns this interpreter to compare a manifest; it starts no emulator",
    ("tests/unit/test_architecture.py",
     "test_the_removed_engine_prototype_stays_out_of_the_product_repository",
     "'git'"):
        "asks git what the repository tracks; it starts no emulator",
    ("tests/unit/test_dragonbyte_foundation.py",
     "_run_module",
     "sys.executable"):
        "runs this interpreter on the application module to read its version "
        "flag; it starts no emulator",
    ("tests/unit/test_dragonbyte_foundation.py",
     "test_the_package_imports_and_the_qt_free_modules_stay_headless",
     "sys.executable"):
        "runs this interpreter to prove the headless modules import with no "
        "window toolkit loaded; it starts no emulator",
    ("tests/unit/test_dragonbyte_foundation.py",
     "test_the_application_starts_and_stays_alive_offscreen",
     "sys.executable"):
        "runs this interpreter on the application under the offscreen platform "
        "to prove start-up does not crash; it starts no emulator",
    ("tests/unit/test_mgba_instrumented_identity.py",
     "_emulator_processes",
     "'ps'"):
        "reads the POSIX process list to assert no emulator appeared",
    ("tests/unit/test_mgba_instrumented_identity.py",
     "_emulator_processes",
     "'tasklist'"):
        "reads the Windows process list to assert no emulator appeared",
    ("tests/unit/test_mgba_instrumented_identity.py",
     "test_the_superseded_revision_is_the_tracked_patches_own_history",
     "'git'"):
        "reads an older revision of the tracked patch with git; it starts no "
        "emulator",
    ("tests/unit/test_mgba_launch_coverage.py",
     "_tracked",
     "'git'"):
        "lists this repository's tracked files for the predicate itself; it "
        "starts no emulator",
    ("tests/unit/test_project_safety.py",
     "_ignored_ancestor",
     "'git'"):
        "asks git whether a path is ignored; it starts no emulator",
    ("tests/unit/test_project_safety.py",
     "test_a_checkout_that_excludes_its_own_state_cannot_stage_it",
     "'git'"):
        "stages and inspects tracked state with git; it starts no emulator",
    ("tests/unit/test_project_safety.py",
     "test_built_wheel_uses_packaged_profile_catalog",
     "sys.executable"):
        "runs this interpreter against a built wheel; it starts no emulator",
    ("tests/unit/test_project_safety.py",
     "test_local_environment_secrets_are_git_ignored",
     "'git'"):
        "asks git which local state is ignored; it starts no emulator",
    ("tests/unit/test_project_safety.py",
     "test_no_local_state_is_tracked",
     "'git'"):
        "asks git what the repository tracks; it starts no emulator",
    ("tests/unit/test_project_safety.py",
     "test_no_rom_or_proprietary_directory_is_tracked",
     "'git'"):
        "asks git what the repository tracks; it starts no emulator",
    ("tests/unit/test_project_safety.py",
     "test_no_tracked_text_embeds_proprietary_artifacts",
     "'git'"):
        "lists tracked text with git for a content scan; it starts no emulator",
    ("tests/unit/test_project_safety.py",
     "test_proprietary_and_generated_paths_are_git_ignored",
     "'git'"):
        "asks git which generated paths are ignored; it starts no emulator",
    ("tests/unit/test_readability.py",
     "test_every_configured_exception_path_matches_a_tracked_file",
     "'git'"):
        "lists tracked files with git to check the exception table; it starts "
        "no emulator",
    ("tests/unit/test_runtime_evidence_report.py",
     "_emulator_processes",
     "'ps'"):
        "reads the POSIX process list to assert no emulator appeared",
    ("tests/unit/test_runtime_evidence_report.py",
     "_emulator_processes",
     "'tasklist'"):
        "reads the Windows process list to assert no emulator appeared",
    ("tests/unit/test_runtime_evidence_report.py",
     "test_the_module_entry_point_prints_the_report",
     "sys.executable"):
        "runs the offline inspector as a module; that module starts nothing",
    ("tools/quality/architecture.py",
     "_git",
     "'git'"):
        "reports the repository's architecture with git; it starts no emulator",
    ("tests/unit/test_release_identity.py",
     "test_a_checkout_reports_its_own_commit_and_tree_state",
     "'git'"):
        "reads the repository's own head and status to check the identity a "
        "checkout reports against them; it starts no emulator",
    ("tests/unit/test_release_identity.py",
     "test_the_generated_record_is_ignored_by_git",
     "'git'"):
        "asks git whether the generated build record is ignored; it starts no "
        "emulator",
    ("tools/quality/public_surface.py",
     "changed_text_files",
     "'git'"):
        "lists changed text with git for the public-surface check; it starts no "
        "emulator",
    ("tools/quality/public_surface.py",
     "tracked_text_files",
     "'git'"):
        "lists tracked text with git for the public-surface check; it starts no "
        "emulator",
    ("tools/quality/readability.py",
     "_git",
     "'git'"):
        "lists tracked files with git for the readability scan; it starts no "
        "emulator",
    ("tools/runtime/evidence_bundle.py",
     "_git",
     "'git'"):
        "measures the repository revision for a bundle; it starts no emulator",
    ("tools/runtime/inject_mgba_lua.ps1",
     "Start-Process",
     "'powershell.exe'"):
        "starts a helper shell that clicks the Scripting window's Run button in "
        "an already-running mGBA; it starts no emulator itself",
    ("tests/unit/test_mgba_state_load_routing.py",
     "_tracked_powershell",
     "'git'"):
        "lists the tracked PowerShell tree for the single-injection-authority "
        "check; it starts no emulator",
    ("tools/webfoot/release_identity.py",
     "_git",
     "'git'"):
        "reads repository state to name the build a package was cut from; it "
        "starts no emulator",
}


@dataclass(frozen=True, slots=True)
class Found:
    """One discovered process start."""

    path: str
    line: int
    anchor: str
    target: str
    name: str
    nested: bool = False

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.path, self.anchor, self.target)

    def describe(self) -> str:
        return (
            f"{self.path}:{self.line} {self.name} launches {self.target} "
            f"(anchor {self.anchor})"
        )


@dataclass(frozen=True, slots=True)
class FileScan:
    """What one Python module contains, as parsed."""

    relative: str
    text: str
    launches: tuple[Found, ...]
    gates: tuple[Found, ...]
    functions: frozenset[str]


def _aliases(tree: ast.AST) -> dict[str, str]:
    """What each imported name resolves to, including ``as`` aliases."""
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return aliases


def _dotted(node: ast.AST, aliases: Mapping[str, str]) -> str:
    """The dotted name a call expression resolves to, or "" if it has none."""
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value, aliases)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _target(call: ast.Call) -> str:
    """The executable a call starts: argv[0], exactly as written."""
    if not call.args:
        return "-"
    first = call.args[0]
    if isinstance(first, (ast.List, ast.Tuple)) and first.elts:
        first = first.elts[0]
    return ast.unparse(first)


class _Walk(ast.NodeVisitor):
    """Launch calls, gate calls and function definitions in one module."""

    def __init__(self, relative: str, aliases: Mapping[str, str]) -> None:
        self.relative = relative
        self.aliases = aliases
        self.functions: set[str] = set()
        self.launches: list[Found] = []
        self.gates: list[Found] = []
        self._stack: list[tuple[str, bool]] = []

    def _descend(self, node: ast.AST, label: str, nested: bool) -> None:
        self._stack.append((label, nested))
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        self._stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions.add(node.name)
        self._descend(node, node.name, False)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_If(self, node: ast.If) -> None:
        self._descend(node, "if", True)

    visit_For = visit_While = visit_Try = visit_With = visit_If

    def visit_Call(self, node: ast.Call) -> None:
        name = _dotted(node.func, self.aliases)
        leaf = name.rsplit(".", 1)[-1]
        functions = [label for label, nested in self._stack if not nested]
        anchor = functions[-1] if functions else "<module>"
        nested = any(flag for _, flag in self._stack)
        if name in LAUNCH_CALLS:
            self.launches.append(
                Found(self.relative, node.lineno, anchor, _target(node), name, nested)
            )
        if leaf in GATE_NAMES:
            self.gates.append(
                Found(self.relative, node.lineno, anchor, "-", leaf, nested)
            )
        self.generic_visit(node)


def scan_python(root: Path, relative: str) -> FileScan:
    """Parse one Python file and record what the predicate needs from it."""
    text = (Path(root) / relative).read_text(encoding="utf-8")
    tree = ast.parse(text)
    walk = _Walk(relative, _aliases(tree))
    walk.visit(tree)
    return FileScan(
        relative,
        text,
        tuple(walk.launches),
        tuple(walk.gates),
        frozenset(walk.functions),
    )


def python_launch_sites(root: Path, files: Iterable[str]) -> tuple[Found, ...]:
    """Every launch call site in the given Python files."""
    return tuple(
        found
        for relative in files
        if relative.endswith(".py")
        for found in scan_python(root, relative).launches
    )


def powershell_launch_sites(root: Path, files: Iterable[str]) -> tuple[Found, ...]:
    """Every process start in a PowerShell file that also references mGBA."""
    found: list[Found] = []
    for relative in files:
        path = Path(root) / relative
        if path.suffix != ".ps1" or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if MGBA not in text.lower():
            continue
        for match in POWERSHELL_START.finditer(text):
            window = text[match.end() : match.end() + 400]
            target = POWERSHELL_FILE_PATH.search(window)
            found.append(
                Found(
                    path=relative,
                    line=text.count("\n", 0, match.start()) + 1,
                    anchor=match.group(0),
                    target=target.group(1) if target else "-",
                    name=match.group(0),
                )
            )
        for match in POWERSHELL_CALL.finditer(text):
            found.append(
                Found(
                    path=relative,
                    line=text.count("\n", 0, match.start()) + 1,
                    anchor="&",
                    target=match.group(1),
                    name="&",
                )
            )
    return tuple(found)


def _gate_covers(scan: FileScan, gate: str, anchor: str) -> bool:
    """Whether the gate is placed so it covers a launch in this file.

    Three shapes are rejected, each proved by a mutation test below:

    - the gate is called inside a conditional, so a path can reach a launch
      without it;
    - the gate lives in a helper function, so nothing ties it to a launch;
    - the gate is named only in another module, so this file is not gated at all.

    A call to the gate in the same function as a launch, before it and not
    nested inside anything, is the accepted shape. The one definition shape
    accepted is the registered site whose anchor names the gate function itself,
    which is how `tools/mgba_probe/runtime.py` carries the instrumented policy.
    """
    if anchor == gate and gate in scan.functions:
        return True
    for gate_call in scan.gates:
        if gate_call.name != gate or gate_call.nested:
            continue
        for launch in scan.launches:
            if launch.anchor == gate_call.anchor and gate_call.line < launch.line:
                return True
    return False


def _ungated(
    root: Path, scans: Mapping[str, FileScan], sites: Sequence[identity.LaunchSite]
) -> list[str]:
    """Registered sites whose proof mechanism is missing or not placed."""
    failures: list[str] = []
    for site in sites:
        path = Path(root) / site.path
        if site.path.endswith(".py"):
            scan = scans.get(site.path) or scan_python(root, site.path)
            if site.proof in GATE_FOR_PROOF:
                gate = GATE_FOR_PROOF[site.proof]
                if not scan.launches:
                    continue
                if not _gate_covers(scan, gate, site.anchor):
                    failures.append(
                        f"{site.path} ({site.anchor}): proof {site.proof} requires "
                        f"{gate}() directly in the function that launches"
                    )
            elif site.proof == identity.FILE_VERSION:
                if PYTHON_VERSION_TOKEN not in scan.text:
                    failures.append(
                        f"{site.path} ({site.anchor}): proof {site.proof} requires "
                        f"{PYTHON_VERSION_TOKEN!r} in the file"
                    )
            elif site.proof == identity.NO_PROOF:
                if not site.rationale.strip():
                    failures.append(f"{site.path} ({site.anchor}): no rationale")
            else:
                failures.append(f"{site.path}: unsupported proof {site.proof}")
        elif site.path.endswith(".ps1"):
            if not path.is_file():
                failures.append(f"{site.path}: registered but missing")
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if site.proof == identity.EXECUTABLE_DIGEST:
                missing = [
                    token for token in POWERSHELL_DIGEST_TOKENS if token not in text
                ]
                if missing:
                    failures.append(
                        f"{site.path} ({site.anchor}): proof {site.proof} requires "
                        f"{', '.join(POWERSHELL_DIGEST_TOKENS)} in the script "
                        f"(missing {', '.join(missing)})"
                    )
            elif site.proof == identity.FILE_VERSION:
                if not any(token in text for token in POWERSHELL_VERSION_TOKENS):
                    failures.append(
                        f"{site.path} ({site.anchor}): proof {site.proof} requires "
                        f"one of {', '.join(POWERSHELL_VERSION_TOKENS)} in the script"
                    )
            elif site.proof == identity.NO_PROOF:
                if not site.rationale.strip():
                    failures.append(f"{site.path} ({site.anchor}): no rationale")
            else:
                failures.append(
                    f"{site.path}: no PowerShell check for proof {site.proof}"
                )
    return failures


def _anchor_tokens(anchor: str) -> frozenset[str]:
    """The identifiers a registry anchor names, for matching against a function."""
    return frozenset(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", anchor))


def audit(
    root: Path,
    python_files: Sequence[str],
    powershell_files: Sequence[str],
    *,
    sites: Sequence[identity.LaunchSite] | None = None,
    exemptions: Mapping[tuple[str, str, str], str] | None = None,
) -> dict[str, list[str]]:
    """Discover every process start and report the ones that escape the policy."""
    registry = tuple(identity.LAUNCH_SITES if sites is None else sites)
    table = NON_MGBA_SITES if exemptions is None else exemptions
    registered = {site.path for site in registry}
    anchors: dict[str, set[str]] = {}
    for site in registry:
        if site.path.endswith(".py"):
            anchors.setdefault(site.path, set()).update(_anchor_tokens(site.anchor))

    needed = list(
        dict.fromkeys(
            [relative for relative in python_files if relative.endswith(".py")]
            + [site.path for site in registry if site.path.endswith(".py")]
        )
    )
    scans = {relative: scan_python(root, relative) for relative in needed}
    discovered = [found for scan in scans.values() for found in scan.launches]
    discovered.extend(powershell_launch_sites(root, powershell_files))

    unregistered: list[str] = []
    for found in discovered:
        if found.path in registered:
            if (
                MGBA in found.target.lower()
                and found.path.endswith(".py")
                and found.anchor not in anchors.get(found.path, set())
            ):
                unregistered.append(
                    f"{found.describe()} - an mGBA launch inside a registered "
                    "file must sit under an anchor the registry names"
                )
            continue
        if MGBA in found.target.lower():
            unregistered.append(
                f"{found.describe()} - a site whose launched target is mGBA is "
                "never exempt"
            )
            continue
        if found.key in table:
            continue
        unregistered.append(found.describe())

    return {
        "unregistered": sorted(unregistered),
        "ungated": sorted(_ungated(root, scans, registry)),
        "exempting_registered": sorted({key[0] for key in table} & registered),
    }


def _tracked(pattern: str) -> list[str]:
    """The repository's tracked files matching one pattern."""
    listing = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", pattern],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [line for line in listing.splitlines() if line.strip()]


@pytest.fixture(scope="module")
def current_tree() -> dict[str, list[str]]:
    """The whole-tree audit, computed once and shared by the three tree tests.

    Module scope is the point: the audit parses every tracked Python file, and
    running it once per assertion costs the CI job tens of seconds for a result
    that cannot change inside one run. The synthetic mutation tests below never
    touch this fixture - each audits its own temporary tree.
    """
    return audit(ROOT, _tracked("*.py"), _tracked("*.ps1"))

def _write_module(root: Path, relative: str, source: str) -> None:
    path = Path(root) / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def _synthetic_site(path: str) -> identity.LaunchSite:
    return identity.LaunchSite(
        path,
        "run_probe",
        identity.PACKAGED_REQUIRED,
        identity.EXECUTABLE_DIGEST,
        "synthetic site for the coverage mutation test",
    )


NEW_LAUNCHER = '''"""A launcher written after the registry was last extended."""
import subprocess


def run_probe(mgba_path):
    return subprocess.Popen([str(mgba_path), "--gdb"], cwd=".")
'''

ALIASED_LAUNCHER = '''"""The same launcher, spelled through an import alias."""
import subprocess as sp


def run_probe(mgba_path):
    return sp.run([str(mgba_path), "rom.gba"], cwd=".")
'''

DIRECT_GATE = '''"""The gate is a first statement of the function that launches."""
import subprocess

from tools.runtime.mgba_identity import PACKAGED_0_10_5, require_mgba_build


def run_probe(mgba_path):
    mgba_path = require_mgba_build(mgba_path, PACKAGED_0_10_5)
    return subprocess.Popen([str(mgba_path), "--gdb"], cwd=".")
'''

NESTED_GATE = '''"""The gate sits inside a conditional, so a path can skip it."""
import subprocess

from tools.runtime.mgba_identity import PACKAGED_0_10_5, require_mgba_build


def run_probe(mgba_path, paranoid=True):
    if paranoid:
        mgba_path = require_mgba_build(mgba_path, PACKAGED_0_10_5)
    return subprocess.Popen([str(mgba_path), "--gdb"], cwd=".")
'''

HELPER_GATE = '''"""The gate lives in a helper function, tied to no launch."""
import subprocess

from tools.runtime.mgba_identity import PACKAGED_0_10_5, require_mgba_build


def _check(mgba_path):
    return require_mgba_build(mgba_path, PACKAGED_0_10_5)


def run_probe(mgba_path):
    return subprocess.Popen([str(_check(mgba_path)), "--gdb"], cwd=".")
'''

IMPORTED_GATE = '''"""The gate is reached inside another module, never named here."""
import subprocess

from tools.runtime.gate_helper import verify_identity


def run_probe(mgba_path):
    mgba_path = verify_identity(mgba_path)
    return subprocess.Popen([str(mgba_path), "--gdb"], cwd=".")
'''

EXEMPTABLE_HARNESS = '''"""One non-mGBA process start and one mGBA launch, side by side."""
import subprocess


def _git_status():
    return subprocess.run(["git", "status"], cwd=".")


def run_probe(mgba_path):
    return subprocess.Popen([str(mgba_path), "--gdb"], cwd=".")
'''

SECOND_LAUNCHER = '''"""A registered probe with a second launcher bolted on."""
import subprocess

from tools.runtime.mgba_identity import PACKAGED_0_10_5, require_mgba_build


def run_probe(mgba_path):
    mgba_path = require_mgba_build(mgba_path, PACKAGED_0_10_5)
    return subprocess.Popen([str(mgba_path), "--gdb"], cwd=".")


def run_probe_again(mgba_path):
    return subprocess.Popen([str(mgba_path), "--gdb"], cwd=".")
'''


def test_the_current_tree_has_no_unregistered_launch_site(
    current_tree: dict[str, list[str]]
):
    assert current_tree["unregistered"] == [], (
        "every detected process start must be registered in "
        "tools.runtime.mgba_identity.LAUNCH_SITES or classified in "
        "NON_MGBA_SITES:\n" + "\n".join(current_tree["unregistered"])
    )


def test_every_registered_site_uses_the_gate_its_proof_names(
    current_tree: dict[str, list[str]]
):
    assert current_tree["ungated"] == [], "\n".join(current_tree["ungated"])


def test_no_exemption_names_a_registered_launch_site(
    current_tree: dict[str, list[str]]
):
    assert current_tree["exempting_registered"] == [], (
        "NON_MGBA_SITES exempts a path the registry already governs, which "
        "would make the registry entry unenforced: "
        + ", ".join(current_tree["exempting_registered"])
    )


def test_a_new_launcher_in_a_synthetic_tree_is_reported(tmp_path: Path):
    _write_module(tmp_path, "pkg/rom013_new_probe.py", NEW_LAUNCHER)

    report = audit(
        tmp_path, ["pkg/rom013_new_probe.py"], [], sites=(), exemptions={}
    )

    assert report["unregistered"], (
        "a normal new launcher was not discovered, so a contributor could add "
        "one without any test noticing"
    )
    assert any("pkg/rom013_new_probe.py:6" in item for item in report["unregistered"])
    assert any("subprocess.Popen" in item for item in report["unregistered"])


def test_an_aliased_launcher_is_reported(tmp_path: Path):
    _write_module(tmp_path, "pkg/rom014_probe.py", ALIASED_LAUNCHER)

    report = audit(tmp_path, ["pkg/rom014_probe.py"], [], sites=(), exemptions={})

    assert report["unregistered"], "an aliased launcher escaped the predicate"
    assert any("subprocess.run" in item for item in report["unregistered"])


def test_a_new_powershell_mgba_launcher_is_reported(tmp_path: Path):
    _write_module(
        tmp_path,
        "tools/run_newbuild.ps1",
        "# launches the dev mGBA build\n"
        "$exe = 'build/tools/mgba-dev/mGBA.exe'\n"
        "Start-Process -FilePath $exe -ArgumentList $rom\n",
    )

    report = audit(tmp_path, [], ["tools/run_newbuild.ps1"], sites=(), exemptions={})

    assert report["unregistered"], "a new PowerShell launcher escaped the predicate"
    assert any("tools/run_newbuild.ps1:3" in item for item in report["unregistered"])


def test_a_call_operator_launcher_is_reported(tmp_path: Path):
    """The call operator starts a process too, and used to be invisible.

    `tools/mgba_probe/build.ps1` launches the instrumented build it has just
    produced this way, which is how a real mGBA launch escaped the inventory.
    """
    _write_module(
        tmp_path,
        "tools/run_instrumented.ps1",
        "# launches the instrumented mGBA build\n"
        "$exe = 'build/rom012/mgba-probe-sdl/mgba-sdl.exe'\n"
        "& $exe --version\n",
    )

    report = audit(tmp_path, [], ["tools/run_instrumented.ps1"], sites=(), exemptions={})

    assert report["unregistered"], "a call-operator launcher escaped the predicate"
    assert any("tools/run_instrumented.ps1:3" in item for item in report["unregistered"])


def test_a_keyed_exemption_clears_only_its_own_call_site(tmp_path: Path):
    _write_module(
        tmp_path,
        "tools/window_click.ps1",
        "# drives a running mGBA by UI Automation\n"
        "Start-Process -FilePath 'powershell.exe' -ArgumentList $helper\n",
    )
    table = {
        ("tools/window_click.ps1", "Start-Process", "'powershell.exe'"):
            "starts a helper shell that clicks a Qt button; it never starts an "
            "emulator"
    }

    report = audit(
        tmp_path, [], ["tools/window_click.ps1"], sites=(), exemptions=table
    )

    assert report["unregistered"] == []


def test_an_exemption_cannot_cover_a_site_that_launches_mgba(tmp_path: Path):
    """The second trigger: an exemption table is never a hiding place."""
    _write_module(tmp_path, "pkg/harness.py", EXEMPTABLE_HARNESS)
    table = {
        ("pkg/harness.py", "_git_status", "'git'"): "runs git, never an emulator",
        ("pkg/harness.py", "run_probe", "str(mgba_path)"):
            "pretends the emulator launch is acceptable",
    }

    report = audit(tmp_path, ["pkg/harness.py"], [], sites=(), exemptions=table)

    assert len(report["unregistered"]) == 1, report["unregistered"]
    assert "run_probe" in report["unregistered"][0]
    assert "never exempt" in report["unregistered"][0]


def test_an_exemption_for_another_anchor_does_not_apply(tmp_path: Path):
    _write_module(tmp_path, "pkg/harness.py", EXEMPTABLE_HARNESS)
    table = {
        ("pkg/harness.py", "another_function", "'git'"):
            "keyed to a call site that is not this one"
    }

    report = audit(tmp_path, ["pkg/harness.py"], [], sites=(), exemptions=table)

    assert any("_git_status" in item for item in report["unregistered"])


def test_a_second_mgba_launcher_in_a_registered_file_is_reported(tmp_path: Path):
    """File-level registration is not a hiding place either."""
    _write_module(tmp_path, "pkg/registered_probe.py", SECOND_LAUNCHER)

    report = audit(
        tmp_path,
        ["pkg/registered_probe.py"],
        [],
        sites=[_synthetic_site("pkg/registered_probe.py")],
        exemptions={},
    )

    assert len(report["unregistered"]) == 1, report["unregistered"]
    assert "run_probe_again" in report["unregistered"][0]
    assert "anchor the registry names" in report["unregistered"][0]


def test_a_directly_placed_gate_satisfies_the_predicate(tmp_path: Path):
    _write_module(tmp_path, "pkg/probe.py", DIRECT_GATE)

    report = audit(
        tmp_path,
        ["pkg/probe.py"],
        [],
        sites=[_synthetic_site("pkg/probe.py")],
        exemptions={},
    )

    assert report["ungated"] == []


def test_a_gate_inside_a_conditional_does_not_satisfy_the_predicate(tmp_path: Path):
    _write_module(tmp_path, "pkg/probe.py", NESTED_GATE)

    report = audit(
        tmp_path,
        ["pkg/probe.py"],
        [],
        sites=[_synthetic_site("pkg/probe.py")],
        exemptions={},
    )

    assert report["ungated"], "a gate inside an if-suite counted as the gate"
    assert "pkg/probe.py" in report["ungated"][0]


def test_a_gate_in_a_helper_function_does_not_satisfy_the_predicate(tmp_path: Path):
    _write_module(tmp_path, "pkg/probe.py", HELPER_GATE)

    report = audit(
        tmp_path,
        ["pkg/probe.py"],
        [],
        sites=[_synthetic_site("pkg/probe.py")],
        exemptions={},
    )

    assert report["ungated"], "a gate in a helper function counted as the gate"
    assert "pkg/probe.py" in report["ungated"][0]


def test_a_gate_in_another_module_does_not_satisfy_the_predicate(tmp_path: Path):
    _write_module(tmp_path, "pkg/probe.py", IMPORTED_GATE)

    report = audit(
        tmp_path,
        ["pkg/probe.py"],
        [],
        sites=[_synthetic_site("pkg/probe.py")],
        exemptions={},
    )

    assert report["ungated"], "a gate named only in another module counted"
    assert "pkg/probe.py" in report["ungated"][0]
