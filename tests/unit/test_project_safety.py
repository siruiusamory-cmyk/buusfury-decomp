import json
from importlib import resources
import os
from pathlib import Path
import re
import subprocess
import sys


def test_upstream_lock_has_eight_unique_pins():
    data = json.loads(Path("upstreams.lock").read_text(encoding="utf-8"))
    repositories = data["repositories"]

    assert data["schema_version"] == 1
    assert len(repositories) == 8
    assert len({item["name"] for item in repositories}) == 8
    assert len({item["path"] for item in repositories}) == 8
    assert all(re.fullmatch(r"[0-9a-f]{40}", item["commit"]) for item in repositories)
    assert all(item["url"].startswith("https://github.com/") for item in repositories)
    assert all(item["path"].startswith("extern/") for item in repositories)


def test_packaged_profile_catalog_matches_development_catalog():
    development = Path("config/roms.yaml").read_text(encoding="utf-8")
    packaged = resources.files("tools.webfoot.data").joinpath("roms.yaml")

    assert packaged.read_text(encoding="utf-8") == development


def test_built_wheel_uses_packaged_profile_catalog(tmp_path):
    project_root = Path(__file__).resolve().parents[2]
    wheel_directory = tmp_path / "wheel"
    install_directory = tmp_path / "installed"
    wheel_directory.mkdir()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            ".",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(wheel_directory),
        ],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    )
    wheel = next(wheel_directory.glob("*.whl"))
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--no-index",
            "--no-compile",
            "--target",
            str(install_directory),
            str(wheel),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(install_directory)
    smoke = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                "from tools.webfoot.cli import load_catalog; "
                "import tools.webfoot.cli as cli; "
                "catalog = load_catalog(None); "
                "assert len(catalog.profiles) == 4; "
                "assert Path(cli.__file__).is_relative_to(Path(r'"
                + str(install_directory)
                + "')); "
                "print('WHEEL_SMOKE_OK')"
            ),
        ],
        cwd=tmp_path,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    assert smoke.stdout.strip() == "WHEEL_SMOKE_OK"


def test_proprietary_and_generated_paths_are_git_ignored():
    probes = [
        "roms/safety-probe.gba",
        "extern/safety-probe/file.txt",
        "build/safety-probe/output.gba",
        ".venv/safety-probe.txt",
        "dump/safety-probe.bin",
        "extracted/safety-probe.png",
    ]

    for probe in probes:
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", "--", probe],
            check=False,
        )
        assert result.returncode == 0, f"path is not ignored: {probe}"


def test_no_rom_or_proprietary_directory_is_tracked():
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--",
            "*.gba",
            "roms/**",
            "extern/**",
            "build/**",
            "dump/**",
            "dumps/**",
            "extracted/**",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout == ""
