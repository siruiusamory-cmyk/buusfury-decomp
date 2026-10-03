"""What the two randomizer *releases* must and must not contain.

The products are two frozen executables, and a frozen build contains exactly what
its entry point can reach. Nothing in the ordinary test suite can see that: a
function-local or a string-named import is invisible to a source scan, and it was
exactly that kind of import which put the whole command surface - the CLI, the
atlas, the map editors, the workbench session - inside both executables until
EXE-PACKAGE-HYGIENE-001 moved the ROM catalog loader out of ``cli.py``.

These are the two rules that keep that from coming back: one measured on the real
import graph, one measured against the product's own identity.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

#: Packages a randomizer release must never carry. Named individually rather than
#: matched by a prefix so that adding to this list is a decision: ``tools.webfoot``
#: itself obviously has to be reachable.
COMMAND_SURFACE = (
    "tools.webfoot.cli",
    "tools.webfoot.commands",
    "tools.webfoot.atlas",
    "tools.webfoot.atlas_build",
    "tools.webfoot.atlas_producers",
    "tools.webfoot.workbench",
    "tools.webfoot.build",
    "tools.webfoot.graphics",
    "tools.webfoot.graphics_authoring",
    "tools.webfoot.dialogue",
    "tools.webfoot.compressed_dialogue",
    "tools.webfoot.text",
    "tools.webfoot.handles",
    "tools.webfoot.relocation",
    "tools.webfoot.map_paint",
    "tools.webfoot.map_resize",
    "tools.webfoot.map_chunk",
    "tools.webfoot.map_layout_write",
    "tools.webfoot.tileset_compositor",
)

#: The entry points both spec templates freeze, and the identity each one reports.
PRODUCTS = (
    ("enemyrand", "Enemy-Randomizer"),
    ("warprand", "Buu-Fury-Warp-Randomizer"),
)

_VERSION_STRING = re.compile(r'StringStruct\("(\w+)",\s*"((?:[^"\\]|\\.)*)"\)')


def _reachable_command_surface() -> list[str]:
    """Import both product services in a subprocess and report what came with them.

    A subprocess rather than an in-process import, because the question is what a
    *fresh* interpreter reaches: this test process has already imported the test
    suite, pytest and whatever else, and none of that is in the executable.
    """
    script = "\n".join(
        [
            "import sys",
            "import tools.webfoot.enemyrand.service",
            "import tools.webfoot.warprand.service",
            f"surface = {COMMAND_SURFACE!r}",
            "reached = sorted(",
            "    name for name in sys.modules",
            "    if any(name == part or name.startswith(part + '.') for part in surface)",
            ")",
            "print(chr(10).join(reached))",
        ]
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, (
        "the product services could not be imported at all, so this check proved "
        f"nothing:\n{completed.stderr}"
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def test_a_product_release_reaches_no_part_of_the_command_surface():
    reached = _reachable_command_surface()

    assert reached == [], (
        "a randomizer release would bundle the command surface it never runs: "
        f"{reached}. Reach the shared code through its own module (for the ROM "
        "catalog that is tools.webfoot.catalog) rather than through tools.webfoot.cli."
    )


@pytest.mark.parametrize("package,build_name", PRODUCTS, ids=[p[0] for p in PRODUCTS])
def test_the_version_resource_names_the_product_it_is_built_into(package: str, build_name: str):
    """The Windows metadata must be the product's own identity, not a copy.

    Read by parsing rather than by evaluating the file: the expression in it is
    PyInstaller's, and a build-time dependency on PyInstaller would make this
    test skip in the portable gate, which is where it is worth the most.
    """
    service = REPO_ROOT / "tools" / "webfoot" / package / "service.py"
    source = service.read_text(encoding="utf-8")

    def constant(name: str) -> str:
        match = re.search(rf'^{name} = "([^"]*)"$', source, flags=re.MULTILINE)
        assert match is not None, f"{service.name} does not define {name}"
        return match.group(1)

    resource = REPO_ROOT / f"{build_name}.version.txt"
    fields = dict(_VERSION_STRING.findall(resource.read_text(encoding="utf-8")))

    assert fields["ProductName"] == constant("TOOL_NAME"), (
        f"{resource.name} names a different product than {service.name} reports"
    )
    version = constant("TOOL_VERSION")
    expected = ".".join([*version.split("."), "0"]) if version.count(".") == 2 else version
    assert fields["FileVersion"] == expected
    assert fields["ProductVersion"] == expected
    assert fields["OriginalFilename"] == f"{build_name}.exe"
    assert fields["InternalName"] == build_name


@pytest.mark.parametrize("package,build_name", PRODUCTS, ids=[p[0] for p in PRODUCTS])
def test_the_spec_freezes_the_identity_the_product_reports(package: str, build_name: str):
    spec = (REPO_ROOT / f"{build_name}.spec.in").read_text(encoding="utf-8")
    assert f"version='{build_name}.version.txt'" in spec
    assert "icon='scripts/randomizer.ico'" in spec
    assert (REPO_ROOT / "scripts" / "randomizer.ico").is_file()
