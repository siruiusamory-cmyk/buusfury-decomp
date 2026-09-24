"""CQA-12: a normal build publishes its provenance document beside its image.

The allocation-critical slice of CQA-12 is one behaviour and one default:

    a build writes its manifest BESIDE the output image, unless a caller
    explicitly redirects it or explicitly disables it.

These tests are portable on purpose. The behaviour they pin is the *default*, and
a default that only a ROM-gated integration test exercises is a default CI cannot
see. The ROM-gated proof that a real build actually creates the file lives in
`tests/integration/test_project_build_rom.py`.
"""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

import pytest

from tools.webfoot.authored_image import AUTHORED_MANIFEST_SUFFIX, manifest_path_for
from tools.webfoot.build import (
    MANIFEST_BESIDE_OUTPUT,
    manifest_path_for_build,
)
from tools.webfoot.cli import build_parser


OUTPUT = Path("out/derivative.gba")

#: The sibling the authored-image transaction already publishes. Deriving it from
#: that module rather than restating the suffix keeps the two writers from
#: disagreeing about where a derivative's provenance lives.
OUTER_SIBLING = manifest_path_for(OUTPUT)


def test_the_default_writes_the_manifest_beside_the_output():
    resolved = manifest_path_for_build(MANIFEST_BESIDE_OUTPUT, OUTPUT)
    assert resolved == OUTER_SIBLING
    assert resolved.name == "derivative.gba" + AUTHORED_MANIFEST_SUFFIX


def test_disabling_and_redirecting_are_both_explicit():
    assert manifest_path_for_build(None, OUTPUT) is None
    elsewhere = Path("reports/derivative.json")
    assert manifest_path_for_build(elsewhere, OUTPUT) == elsewhere
    assert manifest_path_for_build("reports/derivative.json", OUTPUT) == elsewhere


def test_the_default_does_not_depend_on_the_output_directory_existing():
    """Resolution is pure path arithmetic; nothing is created or probed."""
    resolved = manifest_path_for_build(MANIFEST_BESIDE_OUTPUT, Path("nowhere/x.gba"))
    assert resolved.parent == Path("nowhere")
    assert not resolved.exists()


def _build_args(extra):
    return build_parser().parse_args(
        ["build", "proj", "--rom", "roms/x.gba", "--output", "out/x.gba", *extra])


def test_the_cli_defaults_to_publishing_and_can_only_opt_out_explicitly():
    default = _build_args([])
    assert default.manifest is MANIFEST_BESIDE_OUTPUT
    assert default.no_manifest is False

    disabled = _build_args(["--no-manifest"])
    assert disabled.no_manifest is True
    assert disabled.manifest is MANIFEST_BESIDE_OUTPUT   # unused, and not a path

    redirected = _build_args(["--manifest", "reports/m.json"])
    assert redirected.manifest == Path("reports/m.json")
    assert redirected.no_manifest is False


def test_the_cli_refuses_to_redirect_and_disable_at_once():
    with pytest.raises(SystemExit):
        _build_args(["--manifest", "reports/m.json", "--no-manifest"])


def test_the_manifest_pattern_is_ignored_and_stays_narrow():
    """`.gitignore` must cover the generated manifest WITHOUT ignoring all JSON.

    `*.gba` does not match `foo.gba.dragonbyte.json`, so without this pattern a
    derivative saved outside an ignored build directory commits the provenance
    document - which carries ROM-derived content - while ignoring the ROM.
    """
    patterns = [
        line.strip() for line in Path(".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert AUTHORED_MANIFEST_SUFFIX in " ".join(patterns)

    def ignored(name: str) -> bool:
        return any(fnmatch(name, pattern) for pattern in patterns)

    assert ignored("derivative.gba" + AUTHORED_MANIFEST_SUFFIX)
    assert ignored("Some ROM (U).gba" + AUTHORED_MANIFEST_SUFFIX)
    # Narrow: an unrelated manifest-shaped JSON is still tracked, and the pattern
    # needs the `<image>.` prefix rather than matching a bare `dragonbyte.json`.
    assert not ignored("package.json")
    assert not ignored("roms.yaml")
    assert not ignored("provenance.json")
    assert not ignored(AUTHORED_MANIFEST_SUFFIX.lstrip("."))
