"""The machine-readable launch-site registry in `tools.runtime.mgba_identity`.

`docs/skills/mgba-runtime.md` section 2 requires the emulator to be identified
from the binary itself, never from its path. Every repository-controlled way an
mGBA process can start is named in one registry, so an audit, and the coverage
predicate that succeeds the old source scan, read structured fields instead of
grepping prose for them.

Each site carries two of them. `classification` is the frozen taxonomy string -
what the site requires - and `proof` is the mechanism that actually proves
identity there. The two are not the same question: two different binaries live
inside `instrumented-required`, one proved by a build manifest and one by
`VersionInfo.FileVersion`. An enforcement predicate must key the expected gate
off `proof`.

These tests pin that consistency, the registry's own integrity, and the recorded
exceptions: the places where an arbitrary user-chosen emulator is the intended
behaviour, which no later identity gate may quietly take away.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

#: An identity gate in either language (the Python policy module, or the
#: `VersionInfo.FileVersion` comparison the PowerShell launchers use). A
#: `user-selected-permitted` site must contain none of them: adding one there
#: reverses a recorded product decision rather than tightening a hole.
IDENTITY_GATE_TOKENS = (
    "require_mgba_build",
    "verify_instrumented_mgba",
    "PACKAGED_0_10_5",
    "$RequiredMGBVersion",
    "$MGBVersion",
    "VersionInfo.FileVersion",
)

WORKBENCH = "tools/webfoot/workbench/launcher.py"

#: The one packaged site with no launch of its own: it hands its executable to
#: `rom008_query_probe.run_probe`, whose gate is therefore its gate.
DELEGATED_ANCHOR = "run_probe imported from rom008_query_probe"

#: Identity that no site may claim: the frozen proofs, and the classes under
#: which proving nothing is legal.
NO_PROOF_CLASSES = ("user-selected-permitted", "non-runtime-test-only",
                    "obsolete-unreachable")


def _registry():
    """Imported late so the tests below fail as assertions on the baseline
    rather than collapsing this module at collection time."""
    import tools.runtime.mgba_identity as module
    return module


def _sites():
    sites = _registry().LAUNCH_SITES
    assert len(sites) == 32, (
        f"the launch-site registry has {len(sites)} entries; the inventory found "
        "32 repository-controlled mGBA launch sites, the thirty-first being "
        "tools/mgba_probe/build.ps1, which starts the instrumented build it has "
        "just produced through PowerShell's call operator, and the thirty-second "
        "being tools/runtime/mgba_session.ps1, which is the single launch every "
        "session launcher now delegates to")
    return sites


def test_every_site_carries_a_frozen_classification_and_a_frozen_proof_kind():
    module = _registry()
    frozen = set(module.LAUNCH_CLASSIFICATIONS)
    assert len(frozen) == 5, sorted(frozen)
    proofs = set(module.PROOF_KINDS)
    assert len(proofs) == 4, sorted(proofs)
    assert {site.classification for site in _sites()} <= frozen
    assert {site.proof for site in _sites()} <= proofs


def test_every_site_is_a_real_file_with_a_rationale_and_a_unique_anchor():
    seen: set[tuple[str, str]] = set()
    for site in _sites():
        assert (ROOT / site.path).is_file(), f"{site.path} is not in the tree"
        assert site.anchor.strip(), f"{site.path} has no identifying anchor"
        assert site.rationale.strip(), f"{site.path} has no written rationale"
        key = (site.path, site.anchor)
        assert key not in seen, f"duplicate registry entry: {key}"
        seen.add(key)


def test_the_proof_kind_is_consistent_with_the_classification():
    """The taxonomy says what is required; `proof` says which gate proves it.

    A predicate that inferred the gate from the class name alone would demand
    `verify_instrumented_mgba` from the 0.11 dev Qt PowerShell launchers, and
    false-fail them.
    """
    module = _registry()
    for site in _sites():
        key = (site.path, site.anchor)
        if site.classification == module.PACKAGED_REQUIRED:
            assert site.proof == module.EXECUTABLE_DIGEST, (
                f"{key} is {site.classification} proved by {site.proof}; the "
                "packaged build is identified by executable bytes, never by a "
                "version string a wrong binary can also report")
        elif site.classification == module.INSTRUMENTED_REQUIRED:
            assert site.proof in (module.INSTRUMENTED_MANIFEST, module.FILE_VERSION), key
        elif site.classification == module.USER_SELECTED_PERMITTED:
            assert site.proof == module.NO_PROOF, key
        if site.proof == module.NO_PROOF:
            assert site.rationale.strip(), f"{key} proves nothing and says nothing"
            assert site.classification in NO_PROOF_CLASSES, (
                f"{key} proves no identity under {site.classification}, which "
                "requires one")


def test_every_registered_packaged_site_actually_has_the_byte_gate():
    """The registry says the packaged sites prove identity by digest. Measured.

    A registry that claims a gate a file does not carry is worse than no
    registry: the enforcement predicate would trust it and pass a site that
    accepts any binary reporting the right version.
    """
    module = _registry()
    digest = module.PACKAGED_0_10_5.sha256
    for site in _sites():
        if site.classification != module.PACKAGED_REQUIRED:
            continue
        source = (ROOT / site.path).read_text(encoding="utf-8")
        if site.anchor == DELEGATED_ANCHOR:
            assert "from tools.runtime.rom008_query_probe import" in source, site.path
            continue
        if site.path.endswith(".py"):
            assert "require_mgba_build(" in source, (
                f"{site.path} is packaged-required but never calls the packaged "
                "identity gate")
        else:
            assert digest in source.upper(), (
                f"{site.path} does not pin the packaged executable digest {digest}")
            assert "Get-FileHash" in source, (
                f"{site.path} pins a digest it never computes")


def test_a_non_runtime_test_only_site_is_under_tests():
    for site in _sites():
        if site.classification == _registry().NON_RUNTIME_TEST_ONLY:
            assert site.path.startswith("tests/"), (
                f"{site.path} is classified non-runtime-test-only but is not a "
                "test, so nothing else keeps it off a production path")


def test_the_workbench_user_selected_launch_is_a_recorded_exception():
    """The product decision: a user-chosen mGBA runs, whatever its version.

    It fails in both directions. If the registry loses the entry, or the
    launcher grows an identity gate that would reject the user's own install,
    this test says so.
    """
    selected = _registry().USER_SELECTED_PERMITTED
    exceptions = {site.path: site for site in _sites()
                  if site.classification == selected}
    assert WORKBENCH in exceptions, (
        "the Workbench launch must stay registered as user-selected-permitted: "
        "a version is display-only and never gates launch")
    for path, site in exceptions.items():
        source = (ROOT / path).read_text(encoding="utf-8")
        found = [token for token in IDENTITY_GATE_TOKENS if token in source]
        assert not found, (
            f"{path} is registered {site.classification}, but now contains "
            f"{found}; that forces an identity gate onto a recorded exception")
