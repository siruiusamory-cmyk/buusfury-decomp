"""Constant-offset Thumb load/store operand scan for the connector reconstruction.

``docs/research-conventions.md`` requires that a negative claim about a field's
consumer states its coverage and does not rest on a resynchronising sweep that
may have stopped early.  ``tools/research/thumb_disasm.py`` covers that with a
disassembly sweep; this module adds the complementary *raw halfword* route:

every Thumb load or store whose address is ``[Rn, #imm]`` with a **positive
constant immediate** is decoded straight from the halfword bit pattern, so an
undecodable neighbouring halfword cannot hide a site and no control-flow
knowledge is needed.  Six encodings are covered:

    16-bit  ``ldr``/``str``    ``[Rn, #imm5 * 4]``    ``0110 L imm5 rn rt``
    16-bit  ``ldrb``/``strb``  ``[Rn, #imm5]``        ``0111 L imm5 rn rt``
    16-bit  ``ldrh``/``strh``  ``[Rn, #imm5 * 2]``    ``1000 L imm5 rn rt``
    32-bit  ``ldr``/``str``    ``[Rn, #imm12]``       ``1111 1000 1101 Rn`` + ``Rt imm12``
    32-bit  ``ldrb``/``strb``  ``[Rn, #imm12]``       ``1111 1000 1001 Rn`` + ``Rt imm12``
    32-bit  ``ldrh``/``strh``  ``[Rn, #imm12]``       ``1111 1000 1011 Rn`` + ``Rt imm12``

The 32-bit forms are the ARM ARM "Load/store single data item" 12-bit-immediate
encodings: ARMv7-M ``LDR (immediate)`` and the sibling ``STR``/``LDRB``/
``STRB``/``LDRH``/``STRH`` forms that share the layout.  Their field
positions, verified exhaustively against Capstone 5.0.7 by
``build/research/thumb32_layout_probe.py``, are::

    first halfword   1111 1000 op(4) Rn
        bits 15:8    fixed ``1111 1000``
        bits 7:4     ``op``: 0x8 strb, 0x9 ldrb, 0xA strh, 0xB ldrh,
                     0xC str, 0xD ldr.  Bit 7 is 1 exactly for the ``+imm12``
                     form, bits 6:5 are the access size (0 byte, 1 halfword,
                     2 word) and bit 4 is ``L``.
        bits 3:0     ``Rn``
    second halfword  bits 15:12 ``Rt``, bits 11:0 the unscaled ``imm12``

There is **no fixed ``1111`` in the second halfword**: all sixteen bits are the
transfer register and the offset, and the offset is not scaled by the access
size.  ``Rn == 13`` is the SP-relative form and ``Rn == 15`` the PC-relative
literal form of the same encoding, so both are reported here with ``rn`` 13/15;
a field-access claim must exclude them (:func:`coverage_note` says so).

Deliberately *not* covered, and therefore not evidence for absence:

* the 32-bit register-offset and ``imm8`` pre/post-indexed family, whose
  first-halfword ``op`` nibble is ``0x0``-``0x7`` (``1111 1000 0op(3) Rn`` +
  ``Rt 1PUW imm8``).  That family is a *different* layout, so it is not covered
  here.  It carries ``[Rn, Rm]``, and its plain-offset / writeback /
  unprivileged members are selected by second-halfword bits 11:8 = 1100
  (negative ``imm8`` offset), 1001 and 1011 (post-indexed), 1101 and 1111
  (pre-indexed), and 1110 (the unprivileged ``ldrt``/``strt``);
* the 32-bit sign-extending loads ``ldrsb``/``ldrsh`` (``1111 1001 ...``,
  first halfword bits 11:8 = ``1001``), which are not one of the six widths;
* the 32-bit preload hints ``pld``/``pldw``, which are the ``ldrb``/``ldrh``
  ``+imm12`` encodings with ``Rt == 15``, and the architecturally UNDEFINED
  ``str``/``strb``/``strh`` with ``Rn == 15`` (a PC-relative store).  Neither is
  reported: the first is not a load into a register and the second cannot
  execute;
* the 16-bit opcode groups ``0101`` (register offset and the sign-extended
  register forms) and ``1001`` (SP-relative ``str``/``ldr``), and the 16-bit
  PC-relative literal group ``01001``;
* every other load/store addressing mode.

Outside this scan, the *positive* constant-immediate load/store encodings that
remain are the 16-bit SP-relative ``str``/``ldr`` group (``1001 0``/``1001 1``),
the 32-bit preload hints ``pld``/``pldw`` and the unprivileged ``ldrt``/``strt``.
A claim about a positive field offset must name them and must also filter
``rn == 13``, because the SP-relative members of the covered 32-bit encoding are
reported here with ``rn = sp``.

The bit-field positions are measured, not assumed: a Thumb instruction is
written MSB-first, so in the little-endian halfword the operand fields sit in
reverse order from the printed syntax.  Measured behaviour on the canonical
image over ``0x08000000..0x08070000``: at every instruction boundary that
Capstone reports, this scan reports a **superset** of Capstone's in-scope
constant-immediate sites - no site is missed and none is misreported - and it
additionally fires at halfword offsets that are *not* instruction boundaries,
which is the expected residue of decoding every halfword position.  A caller
must therefore read this scan as "candidate accesses", then keep the ones at
real boundaries.  ``tests/unit/test_thumb_mem_operands.py`` pins each encoding
against hand-computed halfwords and
``tests/integration/test_logx_connector_rom.py`` re-measures that agreement over
the whole image, because a wrong field position silently produces an empty scan
that looks like evidence of absence - the exact failure mode
``docs/research-conventions.md`` warns about.

Nothing here writes to the ROM image or to any file.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

ROM_BASE = 0x08000000

#: Register names in encoding order.
REGS = (
    "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
    "r8", "r9", "r10", "r11", "r12", "sp", "lr", "pc",
)

#: ``first & 0xFF00`` shared by every 32-bit ``[Rn, #imm12]`` site: bits 15:8
#: carry the fixed ``1111 1000``.  ``1111 1001`` is a *different* family (the
#: sign-extending ``ldrsb``/``ldrsh``), not one of the six covered widths.
_IMM12_HIGH = 0xF800

#: The 32-bit ``op`` nibble (bits 7:4 of the first halfword) -> mnemonic.
#: Bit 7 is 1 exactly for the ``+imm12`` forms, bits 6:5 are the size
#: (0 byte, 1 halfword, 2 word) and bit 4 is ``L``, so the six covered
#: mnemonics are exactly the nibbles 0x8..0xD.  Nibbles 0x0..0x7 are the
#: register-offset / ``imm8`` pre-post-indexed family (a different layout,
#: out of scope) and 0xE/0xF are size 3 and undefined here.
_IMM12_OPCODES = {
    0x8: "strb",
    0x9: "ldrb",
    0xA: "strh",
    0xB: "ldrh",
    0xC: "str",
    0xD: "ldr",
}

#: The byte/halfword loads.  The ``+imm12`` bit pattern of these two with
#: ``Rt == 15`` is the ``pld``/``pldw`` preload hint, not a load into ``pc``.
_IMM12_HINT_ALIASES = frozenset(("ldrb", "ldrh"))

#: The stores.  Their ``+imm12`` bit pattern with ``Rn == 15`` (a PC-relative
#: store) is architecturally UNDEFINED.
_IMM12_UNDEFINED_WITH_PC_BASE = frozenset(("str", "strb", "strh"))


@dataclass(frozen=True, slots=True)
class MemoryOperand:
    """One ``[Rn, #imm]`` site of a load or store."""

    address: int
    mnemonic: str
    rt: int
    rn: int
    immediate: int

    @property
    def rt_name(self) -> str:
        return REGS[self.rt]

    @property
    def rn_name(self) -> str:
        return REGS[self.rn]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.address:#010x}  {self.mnemonic} {self.rt_name}, [{self.rn_name}, #{self.immediate:#x}]"


def decode_memory_operands(data: bytes, address: int) -> tuple[MemoryOperand, ...]:
    """Every constant-offset load/store whose first halfword is at ``address``.

    Returns an empty tuple when the halfword is not one of the six covered
    encodings.  A 32-bit encoding needs four readable bytes but places no
    constraint on the second halfword beyond ``Rt`` and ``imm12`` themselves, so
    a truncated image drops the site rather than guessing.
    """
    offset = address - ROM_BASE
    if offset < 0 or offset + 4 > len(data):
        return ()
    first = data[offset] | (data[offset + 1] << 8)
    second = data[offset + 2] | (data[offset + 3] << 8)
    found: list[MemoryOperand] = []

    # 16-bit immediate-offset forms.  Thumb-1 is written MSB-first and these
    # three encodings are one 4-bit opcode plus a load bit:
    #     0110 L imm5 rn rt   word   (L is bit 11 of the printed form)
    #     0111 L imm5 rn rt   byte
    #     1000 L imm5 rn rt   halfword
    # In the little-endian halfword that is: mnemonic class in the high nibble,
    # the load bit at bit 11, imm5 at 10:6, rn at 5:3 and rt at 2:0.
    #
    # Masking the class with 0xF800 is the trap here: it splits `0110 L` and
    # `0111 L` into the wrong groups and silently drops every word load.  The
    # class nibble is the top four bits, so the mask is 0xF000 and the load bit
    # is called out separately.
    low_byte = (first >> 6) & 0x1F
    if (first & 0xF000) == 0x6000:  # 0110 word
        is_load = (first & 0x0800) != 0
        found.append(
            MemoryOperand(
                address,
                "ldr" if is_load else "str",
                first & 7,
                (first >> 3) & 7,
                low_byte * 4,
            )
        )
    elif (first & 0xF000) == 0x7000:  # 0111 byte
        is_load = (first & 0x0800) != 0
        found.append(
            MemoryOperand(
                address,
                "ldrb" if is_load else "strb",
                first & 7,
                (first >> 3) & 7,
                low_byte,
            )
        )
    elif (first & 0xF000) == 0x8000:  # 1000 halfword
        is_load = (first & 0x0800) != 0
        found.append(
            MemoryOperand(
                address,
                "ldrh" if is_load else "strh",
                first & 7,
                (first >> 3) & 7,
                low_byte * 2,
            )
        )

    # 32-bit `1111 1000 op(4) Rn` + `Rt imm12`.  Bits 15:8 are the fixed
    # `1111 1000`; the op nibble at bits 7:4 selects the mnemonic, with bit 7
    # = 1 for the `+imm12` form, bits 6:5 the size and bit 4 the load bit.
    # Rn is the low nibble of the first halfword and the *whole* second
    # halfword is `Rt` in bits 15:12 plus the unscaled `imm12` in bits 11:0 -
    # there is no `1111` in the second halfword.  (An earlier revision masked
    # the op to bits 8:5 and demanded `second & 0xF000 == 0xF000`, which
    # misread every byte/halfword form and dropped every store.)
    if (first & 0xFF00) == _IMM12_HIGH:
        mnemonic = _IMM12_OPCODES.get((first >> 4) & 0xF)
        if mnemonic is not None:
            rt = (second >> 12) & 0xF
            rn = first & 0xF
            # Two sub-patterns of this encoding are not one of the six
            # instructions and must not be reported as if they were:
            # `ldrb`/`ldrh` with Rt == 15 is the `pld`/`pldw` preload hint, and
            # `str`/`strb`/`strh` with Rn == 15 (a PC-relative store) is
            # architecturally UNDEFINED.  Capstone 5.0.7 agrees: it decodes the
            # first as `pld`/`pldw` and rejects the second.  `ldr` with Rt == 15
            # is a real branch-via-load and stays; Rn == 15 loads stay too (the
            # PC-relative literal alias, reported with rn = pc).
            hinted = rt == 15 and mnemonic in _IMM12_HINT_ALIASES
            undefined = rn == 15 and mnemonic in _IMM12_UNDEFINED_WITH_PC_BASE
            if not hinted and not undefined:
                found.append(
                    MemoryOperand(address, mnemonic, rt, rn, second & 0xFFF)
                )
    return tuple(found)


def iter_memory_operands(
    data: bytes, start: int, end: int
) -> Iterator[MemoryOperand]:
    """Every covered site in ``[start, end)``, scanning every halfword offset."""
    address = start & ~1
    while address + 2 <= end:
        yield from decode_memory_operands(data, address)
        address += 2


def find_field_accesses(
    data: bytes,
    offsets: set[int],
    *,
    start: int = ROM_BASE,
    end: int | None = None,
    mnemonics: set[str] | None = None,
    base_registers: set[int] | None = None,
) -> list[MemoryOperand]:
    """Every covered site whose immediate is in ``offsets``.

    ``mnemonics`` and ``base_registers`` narrow the result; both default to
    "any".  The scan is a raw halfword pass over ``[start, end)``, so the
    caller's coverage statement is exactly that range.
    """
    limit = end if end is not None else ROM_BASE + len(data)
    hits: list[MemoryOperand] = []
    for site in iter_memory_operands(data, start, limit):
        if site.immediate not in offsets:
            continue
        if mnemonics is not None and site.mnemonic not in mnemonics:
            continue
        if base_registers is not None and site.rn not in base_registers:
            continue
        hits.append(site)
    return hits


def coverage_note(start: int, end: int) -> str:
    """The sentence a negative claim from this module must carry."""
    return (
        f"positive constant-immediate load/store scan over {start:#010x}..{end:#010x}; "
        "the 32-bit register-offset and imm8 pre/post-indexed forms, the "
        "sign-extending ldrsb/ldrsh forms, the 16-bit register-offset and "
        "SP-relative groups and every PC-relative literal load are outside this "
        "scan, and because the 32-bit imm12 encoding is shared with the "
        "PC-relative literal (rn 15) and SP-relative (rn 13) forms this scan "
        "does report those two base registers, which a field-access claim must "
        "exclude"
    )
