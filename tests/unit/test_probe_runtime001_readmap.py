"""The PROBE-RUNTIME-001 read-map observer's JSON and state-arming contract.

The observer is Lua and this host has no Lua interpreter wired into the test
environment, so these tests read the tracked file and assert the exact properties
the fix round named: every runtime-controlled string that reaches READMAP.json goes
through one escape, a state path with no AT frame never loads and says so, and no
stale claim about the width column survives in the summary or the JSON note.
"""

from __future__ import annotations

from pathlib import Path

OBSERVER = (
    Path(__file__).resolve().parents[2]
    / "tools"
    / "runtime"
    / "probe_runtime001_readmap.lua"
)


def _source() -> str:
    assert OBSERVER.is_file(), f"{OBSERVER} is missing"
    return OBSERVER.read_text(encoding="utf-8")


def test_the_readmap_observer_escapes_every_runtime_string_it_writes_to_json():
    source = _source()
    assert "local function json_escape(" in source, "the observer has no json_escape"
    # A Windows filename cannot contain a quote, so the quote case is exercised on
    # every load by a self-check that carries both characters the escape must cover.
    assert 'assert(json_escape([[a"b\\c]]) == [[a\\"b\\\\c]]' in source, (
        "the escape is not self-checked against a value with a quote and a backslash"
    )
    for applied in (
        'json_escape(state and state.path or "")',
        'json_escape(state and state.result or "")',
        "json_escape(overall_verdict())",
    ):
        assert applied in source, f"{applied} is not applied in READMAP.json"


def test_the_readmap_observer_refuses_a_state_path_without_an_at_frame():
    source = _source()
    assert 'tonumber(os.getenv("PROBE_RUNTIME_STATE_AT") or "") or 0' not in source, (
        "a missing AT frame still defaults to frame 0, which loads on frame 1"
    )
    assert "STATE_AT ~= nil and frames >= STATE_AT" in source, (
        "the load is not gated on both PROBE_RUNTIME_STATE and PROBE_RUNTIME_STATE_AT"
    )
    assert "STATE REFUSED" in source, "a refused state path is not logged"
    assert "PROBE_RUNTIME_STATE_AT is not set" in source, (
        "the refusal does not name the missing variable"
    )


def test_the_readmap_observer_does_not_claim_the_width_is_unexposed():
    source = _source()
    assert "Width is not exposed" not in source, (
        "the summary writer and the JSON note still carry the pre-fix width claim"
    )


def test_the_readmap_observer_quotes_every_json_string_field():
    source = _source()
    # The pre-fix artifact did not parse: first_pc was interpolated as a bare
    # 0x-token, so json.load refused the whole file at its first span row.
    assert '"first_pc": "%s"' in source, "first_pc is not quoted in the span row"
    assert '"first_pc": %s' not in source, "first_pc is still written unquoted"
