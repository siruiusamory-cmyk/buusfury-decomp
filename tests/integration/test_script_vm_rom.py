from pathlib import Path
import hashlib
from collections import Counter
from dataclasses import replace
import pytest
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.scripts import load_scripts, script_references, reverse_text_consumers
from tools.webfoot.formats.script_vm import assemble
from tools.webfoot.capability import CapabilityError

SHA='6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75'

@pytest.fixture
def rom():
    path=Path('roms/Dragon Ball Z - The Legacy of Goku II (USA).gba')
    if not path.exists(): pytest.skip('canonical ROM not configured locally')
    before=path.read_bytes()
    assert hashlib.sha256(before).hexdigest()==SHA
    yield path
    assert path.read_bytes()==before


def test_exhaustive_supported_corpus_identity(rom):
    c=load_scripts(rom,RomProfileCatalog.load('config/roms.yaml'))
    assert len(c.ir.entries)==86
    assert len(c.ir.blocks)==86
    assert c.instruction_count==323
    assert c.source_offset==0x6d66c0
    assert c.ir.extent==539
    assert not c.ir.opaque
    assert assemble(c.ir)==rom.read_bytes()[0x6d66c0:0x6d68db]
    assert Counter(i.opcode for b in c.ir.blocks for i in b.instructions)=={0:107,1:1,2:107,4:16,5:6,17:86}
    assert c==load_scripts(rom,RomProfileCatalog.load('config/roms.yaml'))
    assert script_references(c.ir)==()
    assert reverse_text_consumers((),260)=={i:() for i in range(260)}


def test_contract_tampering_rejected(rom):
    catalog=RomProfileCatalog.load('config/roms.yaml')
    text=Path('config/roms.yaml').read_text().replace('pool_size: 539','pool_size: 540')
    with pytest.raises(CapabilityError): load_scripts(rom,RomProfileCatalog.loads(text))


def test_executable_dispatch_and_root_contract(rom):
    import struct
    d=rom.read_bytes()
    u=lambda pos:struct.unpack_from('<I',d,pos)[0]
    assert u(0x4c80)==0x086d68dc
    assert u(0x9320)==0x083b5c00
    assert u(0x3b5c00+17*4)==0
    assert u(0x3b5c00+30*4)==0x030026bc
    assert d[0x4ae2:0x4ae6]==bytes.fromhex('2b2ecfdb')
    assert u(0x95ac)==0x080e2840
    assert sum(u(i)==0x080e2840 for i in range(0,len(d),4))==20


def test_opcode_profile_allowlist_enforced(rom,monkeypatch):
    from tools.webfoot.data.script_specs import OPCODE_SETS
    from tools.webfoot.formats.script_vm import ScriptError
    spec=OPCODE_SETS['stack_be7_v1']
    monkeypatch.setitem(OPCODE_SETS,'stack_be7_v1',replace(spec,profiles=()))
    with pytest.raises(ScriptError,match='not verified for this profile'):
        load_scripts(rom,RomProfileCatalog.load('config/roms.yaml'))
