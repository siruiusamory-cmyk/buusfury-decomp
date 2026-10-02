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


def _ignored_ancestor(probe: str) -> str | None:
    """The shallowest path component of ``probe`` git reports as ignored.

    Only consulted when git refuses to answer about ``probe`` itself, which it
    does when the path traverses a symlink or directory junction ("pathspec is
    beyond a symbolic link"). Git will not stage anything under an ignored
    directory, so an ignored ancestor is the same guarantee for this probe.
    """
    parts = Path(probe).parts
    for index in range(1, len(parts)):
        ancestor = Path(*parts[:index]).as_posix()
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", "--", ancestor],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return ancestor
    return None


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
            capture_output=True,
            text=True,
        )
        if result.returncode == 128 and "beyond a symbolic link" in result.stderr:
            # A local convenience link in the path - the `roms` directory
            # junction several ROM-gated families expect - makes git refuse
            # the pathspec rather than answer it. The probe is still decidable
            # one level up, and it is decidable strictly: the enclosing path
            # must itself be ignored, or its contents could be staged.
            ancestor = _ignored_ancestor(probe)
            assert ancestor is not None, (
                f"{probe} cannot be checked ({result.stderr.strip()}) and no "
                "ancestor of it is ignored either: a link in this path is not "
                "covered by any ignore rule, so what it points at could be "
                "staged. Prefer a real ignored directory over a link."
            )
            continue
        assert result.returncode == 0, f"path is not ignored: {probe}"


def test_local_environment_secrets_are_git_ignored():
    """A local .env must never be stageable, and its template must stay trackable.

    A live API key was found in an untracked `.env` in a stale checkout. The
    key itself was preserved outside the repository; this contract is what keeps
    the next one from being committed by an unthinking `git add -A`.

    Every probe passes ``--no-index``. Without it, ``git check-ignore`` consults
    the index and reports a *tracked* path as not ignored even when a pattern
    matches it, so the template assertion below would quietly stop testing the
    patterns the moment a template was committed - exactly the change it exists
    to catch. ``--no-index`` makes the answer depend on the ignore rules alone.
    """
    ignored = [
        ".env",
        ".env.local",
        ".env.production.local",
        ".env.development.local",
        ".env.example.local",
        "tools/.env",
        "src/data/.env.local",
    ]
    trackable = [
        ".env.example",
        ".env.sample",
        ".env.template",
        "docs/.env.example",
    ]

    for probe in ignored:
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-v", "--", probe],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"local secret file is not ignored: {probe}"
        # Pin the source: an ambient excludes file must not be able to satisfy
        # this contract if the repository patterns are ever deleted.
        assert ".gitignore:" in result.stdout, (
            f"{probe} is ignored by something other than a repository rule: "
            f"{result.stdout.strip()}"
        )

    for probe in trackable:
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--quiet", "--", probe],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1, (
            f"{probe} is ignored, so a documentation template could not be "
            "committed; the local-secret patterns are too broad"
        )


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


def test_local_state_is_not_stageable():
    """The local working state a tool keeps in the checkout must stay untracked.

    These paths are ignored from `.git/info/exclude` rather than the tracked
    `.gitignore`, so that a contributor's tooling choices are not published as
    part of the project. The contract is the same either way: a stray
    `git add -A` must not pick them up, and no tracked path may be one of them.
    """
    probes = [
        "<local-state-name>",
        "<local-state-prefix>/example.md",
        "<local-state-name>",
        "<local-state-prefix>/state.json",
        "<local-state-prefix>/settings.json",
        "<local-state-prefix>/goals/example.json",
        "<local-state-name>",
    ]

    for probe in probes:
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--quiet", "--", probe],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"local state is stageable: {probe}"

    tracked = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    offenders = [
        name
        for name in tracked
        if name in {"<local-state-name>", "<local-state-name>", "<local-state-name>"}
        or name.startswith(("<local-state-prefix>/", "<local-state-prefix>/", "<local-state-prefix>/", "<local-state-prefix>/"))
    ]
    assert offenders == [], f"local state is tracked: {offenders}"


def test_pytest_does_not_retain_passing_run_artifacts():
    """Build/extract tests write whole ROMs and thousands of PNGs into tmp_path.

    pytest's defaults keep three basetemp roots, so a run under a fresh TEMP
    never collects the previous one: thousands of orphaned ROMs and over a
    million PNGs reached 17 GB before this was set. Retaining only failed runs
    keeps what diagnosis needs and nothing else.
    """
    config = Path("pyproject.toml").read_text(encoding="utf-8")

    assert 'tmp_path_retention_policy = "failed"' in config
    assert "tmp_path_retention_count" in config


def test_no_tracked_text_embeds_proprietary_artifacts():
    """No tracked text may name a private ROM, save state or dump.

    The named files are local research inputs. A document that cites one as a
    required input turns an instruction to a reader into an instruction to
    obtain proprietary data, so the ban is on the filename anywhere in tracked
    text, not only in a workflow document.

    This file necessarily contains the names it forbids, so it is the only
    exclusion. That is asserted rather than assumed: a detector that quietly
    stops scanning a file is worse than no detector.
    """
    forbidden = ("higher-plane-original.ss1", "higher-plane-original.sav", "BEGIN ROM")
    self_path = "tests/unit/test_project_safety.py"
    offenders = []
    excluded = 0
    listing = subprocess.run(
        ["git", "ls-files", "-z"], check=True, capture_output=True, text=True
    ).stdout.split("\0")
    for name in listing:
        if not name or Path(name).suffix.lower() in {".png", ".gba", ".sav", ".ss1"}:
            continue
        if name == self_path:
            excluded += 1
            continue
        try:
            text = Path(name).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for marker in forbidden:
            if marker in text:
                offenders.append(f"{name}: {marker}")

    assert excluded == 1, "the detector must be the only file skipped"
    assert offenders == [], "tracked text names proprietary inputs:\n" + "\n".join(offenders)
