from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GHIDRA_TOOLS = PROJECT_ROOT / "tools" / "ghidra"
EXPECTED_MD5 = "3a74fce97f1ea2b28c2a50ec3df0acee"
EXPECTED_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)


def _read(name: str) -> str:
    return (GHIDRA_TOOLS / name).read_text(encoding="utf-8")


def test_ghidra_scripts_fail_closed_before_access_or_mutation():
    report = _read("CalibrationReport.java")
    markup = _read("ApplyCalibrationMarkup.java")

    for source in (report, markup):
        assert EXPECTED_MD5 in source
        assert EXPECTED_SHA256 in source
        assert 'EXPECTED_LANGUAGE = "ARM:LE:32:v4t"' in source
        assert "getExecutableMD5()" in source
        assert "getExecutableSHA256()" in source
        assert "requireExpectedProgram();" in source

    assert report.index("requireExpectedProgram();") < report.index("getScriptArgs()")
    assert markup.index("requireExpectedProgram();") < markup.index("startTransaction(")


def test_report_output_is_confined_to_ignored_build_directory():
    report = _read("CalibrationReport.java")
    wrapper = _read("run-calibration.ps1")

    assert '"build/ghidra/reports"' in report
    assert "getCanonicalFile()" in report
    assert "candidate.startsWith(allowed)" in report
    assert "build\\ghidra\\reports" in wrapper
    assert "$absoluteOutputPath.StartsWith(" in wrapper
    assert "OrdinalIgnoreCase" in wrapper


def test_headless_report_wrapper_is_read_only_and_does_not_reanalyze():
    wrapper = _read("run-calibration.ps1")

    assert "-readOnly" in wrapper
    assert "-noanalysis" in wrapper
    assert "ApplyCalibrationMarkup.java" not in wrapper
    assert "CalibrationReport.java" in wrapper


def test_calibration_labels_remain_conservative():
    markup = _read("ApplyCalibrationMarkup.java")

    for label in (
        "point_query_080126D4",
        "factory_08007674",
        "spatial_filter_08007768",
        "spatial_action_080125E8",
        "downstream_080075AC",
    ):
        assert label in markup

    for unsupported in ("collision_trigger", "warp_zone", "dialogue_region"):
        assert unsupported not in markup
