"""TOOLKIT-013: the read-only `webfoot event` surface over the Buu corpus."""
from pathlib import Path
import hashlib
import json
import pytest
from tools.webfoot.cli import main

SHA = '940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e'
FIRST = 'buus_fury_usa_rev0_01c1707f:static40:00:slot04'


@pytest.fixture
def rom():
    path = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
    if not path.exists():
        pytest.skip('canonical ROM not configured locally')
    before = path.read_bytes()
    assert hashlib.sha256(before).hexdigest() == SHA
    yield str(path)
    assert path.read_bytes() == before


def _run(capsys, *argv):
    assert main(list(argv)) == 0
    return json.loads(capsys.readouterr().out)


def test_event_summary_reports_the_measured_corpus(rom, capsys):
    # No --family, so the first declared family is used and static40 remains the
    # default surface. TOOLKIT-014 proved no owner for it, hence 0 attachments.
    assert _run(capsys, 'event', 'summary', rom) == {
        'profile_id': 'buus_fury_usa_rev0_01c1707f',
        'family': 'static40',
        'opcode_set': 'stack_be16_buu_v1',
        'entries': 120,
        'blocks': 120,
        'instructions': 328,
        'extent_bytes': 548,
        'uncovered_bytes': 0,
        'attachments': 0,
    }


def test_event_list_is_deterministic_and_address_free(rom, capsys):
    listed = _run(capsys, 'event', 'list', rom)
    assert len(listed) == 120
    assert listed == sorted(listed)
    assert listed[0] == FIRST
    assert _run(capsys, 'event', 'list', rom) == listed
    # Identities are authoring names, so no ROM address may leak into them.
    assert not any('0x' in identity or '720340' in identity for identity in listed)


def test_event_show_names_structure_without_asserting_meaning(rom, capsys):
    shown = _run(capsys, 'event', 'show', rom, FIRST)
    assert shown['identity'] == FIRST
    names = [i['name'] for i in shown['instructions']]
    assert names[-1] == 'terminate'
    # Structural names only: nothing here may read as a gameplay verb.
    assert not {'say', 'give_item', 'warp', 'set_flag'} & set(names)


def test_event_validate_round_trip_passes(rom, capsys):
    assert _run(capsys, 'event', 'validate-round-trip', rom) == {
        'round_trip': True, 'bytes': 548}


def test_event_refuses_a_profile_without_a_verified_corpus(capsys):
    path = Path('roms/Dragon Ball Z - The Legacy of Goku (USA).gba')
    if not path.exists():
        pytest.skip('LOG1 ROM not configured locally')
    assert main(['event', 'summary', str(path)]) == 2
    assert 'does not declare scripts' in capsys.readouterr().err


def test_event_reports_an_unknown_identity(rom, capsys):
    assert main(['event', 'show', rom, 'nope']) == 2
    assert 'unknown event identity' in capsys.readouterr().err


def test_no_event_authoring_command_exists(rom):
    """Free capacity is zero, so growth is absent by construction, not refused."""
    from tools.webfoot.cli import build_parser
    parser = build_parser()
    event = next(a for a in parser._subparsers._group_actions[0].choices.items()
                 if a[0] == 'event')[1]
    commands = set(event._subparsers._group_actions[0].choices)
    # TOOLKIT-014 added family selection and owner queries. All are read-only:
    # nothing here writes, grows or relocates a stream.
    assert commands == {'summary', 'list', 'show', 'validate-round-trip',
                        'families', 'attachments', 'for-owner', 'owners-of'}
