import os

import pytest

from tools.assets import generate_assets as G


def test_a_missing_compressor_is_built_from_the_source_tree(tmp_path, monkeypatch):
    built = tmp_path / "compress.exe"
    seen = []

    def build(argv, **_kwargs):
        seen.append(argv)
        built.write_bytes(b"")
        return 0

    monkeypatch.setattr(G, "COMPRESS", str(built))
    monkeypatch.setattr(G.subprocess, "call", build)
    assert G.compressor() == str(built)
    assert seen == [["cmd.exe", "/c", os.path.join(G.ROOT, "tools", "compress", "build.cmd")]]


def test_a_compressor_that_will_not_build_names_the_script(tmp_path, monkeypatch):
    built = tmp_path / "compress.exe"
    monkeypatch.setattr(G, "COMPRESS", str(built))
    monkeypatch.setattr(G.subprocess, "call", lambda argv, **_kwargs: 1)
    with pytest.raises(SystemExit) as refusal:
        G.compressor()
    assert "build.cmd" in str(refusal.value)


def test_a_present_compressor_is_not_built_again(tmp_path, monkeypatch):
    built = tmp_path / "compress.exe"
    built.write_bytes(b"")
    monkeypatch.setattr(G, "COMPRESS", str(built))
    monkeypatch.setattr(G.subprocess, "call", lambda *a, **k: pytest.fail("the build ran"))
    assert G.compressor() == str(built)
