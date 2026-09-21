"""Resynchronising read-only Thumb/ARM disassembly helpers for LOGX-LAYER-001.

Repository rule (``docs/research-conventions.md``, "Static disassembly
discipline"): a naive linear sweep stops at the first undecodable halfword and
silently returns nothing for every later address, so an empty sweep is not
evidence of absence.  This module therefore never reports absence from a linear
sweep.  It offers:

* :func:`linear_thumb` - a resynchronising single-pass sweep that advances two
  bytes past an undecodable halfword instead of stopping and reports how many
  halfwords it could not decode;
* :func:`linear_thumb_wide` / :func:`iter_thumb_wide` - the same sweep, but each
  site is offered a full four-byte window so that two-halfword Thumb
  instructions (``bl``, ``blx``, and the Thumb-2 wide forms) decode instead of
  being counted as undecodable;
* :func:`find_field_extractions` - every ``lsls rd,rs,#a ; lsrs rd,rd,#b`` site
  in a range, reported as ``(right_shift, width)``, which is how this project
  states a negative claim about a mask such as ``0x3FF`` or ``0xF000``;
* :func:`thumb_function` - a control-flow-following decode from a seeded entry;
* :func:`find_thumb_function_entries` - discovers Thumb ``push {.., lr}``
  prologues across a bounded region as candidate boundaries;
* :func:`resolve_thumb_bl` - exact BL/BLX target decoding from raw halfwords;
* :func:`iter_thumb_calls` / :func:`scan_thumb_calls` / \
  :func:`scan_thumb_bl_callers` - the authoritative Thumb caller census,
  enumerated by *decoding* each halfword-aligned site.

Nothing here writes to the ROM image or to any file.

The two sweeps are deliberately different entry points.  ``linear_thumb`` is
the one LOGX-LAYER-001's published undecodable-halfword census was taken with;
it offers Capstone only two bytes at a time, so it cannot decode a two-halfword
instruction and its undecodable count includes every such site.  New work that
needs real coverage uses ``linear_thumb_wide``.  Neither sweep is a caller
census: a sweep follows one decode path, so a site it steps over is invisible.
:func:`iter_thumb_calls` exists because a caller census needs the opposite
property - *every* halfword-aligned site must be considered.

**Caller enumeration, and what was wrong with it (EVIDENCE-RISK-DEBT-001).**
The former ``scan_thumb_bl_callers`` matched raw halfword pairs against the
pattern "first halfword in ``0xF000..0xF7FF``, second halfword masked to
``0xF800`` or ``0xE800``".  Measured against the whole canonical image that
predicate was wrong in two independent ways, and both were reproduced before it
was replaced:

* **It invented sites.** ``BLX`` (T2) reserves bit 0 of its second halfword, so
  a pair with that bit set is not an encoding at all; the pattern accepted it
  anyway.  All **1,552** false positives the old helper reported were exactly
  that: a bit-0-set ``0xE800``-masked pair.
* **It missed real sites.** The masked values admit only the J1=J2=1
  combination of each encoding - one of four - so three quarters of the encoding
  space was unreachable.  It recovered **16,196** of the accepted **29,509**
  sites, a recall of **54.9%**, missing 9,779 ``BL`` and 3,534 ``BLX`` sites.
  The visible effect on one target is not uniform: a branch whose displacement is
  smaller than 4 MiB in magnitude has J1=J2=1 in either direction, so a census of
  callers to a nearby function can come out numerically unchanged.  Measured over
  the accepted sites, every site with |displacement| < 2^22 has both bits set and
  none at or above it does, which is where that boundary comes from.  Either way it
  is luck, not correctness, and it is not something a caller may rely on.
* **It mis-computed ``BLX`` targets.** :func:`resolve_thumb_bl` added the
  immediate to ``address + 4`` for both encodings, but ``BLX`` rounds that PC
  *down* to a word boundary first.  On the canonical image 2,568 of the 5,283
  ``BLX`` sites resolved two bytes high - a wrong address, not merely a missing
  one, and a wrong target cannot be detected by comparing counts.

The accepted census is "every halfword-aligned site in the image whose
four-byte window decodes as a four-byte ``bl`` or ``blx``": 24,226 ``BL`` and
5,283 ``BLX``, 29,509 in total, reproduced exactly by
:func:`iter_thumb_calls`.  The census is a *static site* count, not a
control-flow-reachable caller set: it cannot tell code from data, so a
halfword pair in a data region that happens to be a valid encoding is still a
site.  That is a limit of the accepted definition, not of the enumeration.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

try:  # pragma: no cover - dependency presence is environment-specific
    import capstone
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"capstone is required for this probe: {exc}") from exc

ROM_BASE = 0x08000000

_THUMB = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
_THUMB.detail = False
_ARM = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
_ARM.detail = False


@dataclass(frozen=True, slots=True)
class Instruction:
    address: int
    size: int
    mnemonic: str
    operands: str

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.address:08x}  {self.mnemonic:<8} {self.operands}".rstrip()


@dataclass(slots=True)
class SweepResult:
    """Accumulated result of a resynchronising linear sweep."""

    instructions: list[Instruction] = field(default_factory=list)
    undecodable_halfwords: list[int] = field(default_factory=list)
    start: int = 0
    end: int = 0

    @property
    def coverage_bytes(self) -> int:
        return self.end - self.start


def iter_thumb(data: bytes, start: int, end: int) -> Iterator[Instruction | int]:
    """Yield each decodable Thumb instruction, or the address (an ``int``) of an
    undecodable halfword, in one pass over ``[start, end)``.

    This is the only sweep primitive: correctness (resynchronisation) and speed
    (a single pass) both matter for the caller's absence claims.
    """
    address = start & ~1
    while address + 2 <= end:
        offset = address - ROM_BASE
        if offset < 0 or offset + 2 > len(data):
            break
        item = next(_THUMB.disasm(data[offset : offset + 2], address, 2), None)
        if item is None:
            yield address
            address += 2
            continue
        yield Instruction(item.address, item.size, item.mnemonic, item.op_str)
        address += item.size


def linear_thumb(data: bytes, start: int, end: int) -> SweepResult:
    """Materialised resynchronising Thumb sweep over ``[start, end)``."""
    result = SweepResult(start=start, end=end)
    for item in iter_thumb(data, start, end):
        if isinstance(item, int):
            result.undecodable_halfwords.append(item)
        else:
            result.instructions.append(item)
    return result


def decode_thumb_at(data: bytes, address: int) -> Instruction | None:
    """Decode one Thumb instruction at ``address`` using a four-byte window.

    Returns ``None`` when no instruction decodes.  The wider window is what
    makes two-halfword instructions visible; :func:`iter_thumb` cannot see them
    because it hands Capstone two bytes.
    """
    offset = address - ROM_BASE
    if offset < 0 or offset + 2 > len(data):
        return None
    window = data[offset : offset + 4]
    item = next(_THUMB.disasm(window, address, 1), None)
    if item is None:
        return None
    if item.size > len(window):
        return None
    return Instruction(item.address, item.size, item.mnemonic, item.op_str)


def iter_thumb_wide(data: bytes, start: int, end: int) -> Iterator[Instruction | int]:
    """Like :func:`iter_thumb`, but decodes two-halfword Thumb instructions.

    Each site is offered four bytes, so ``bl``/``blx`` and Thumb-2 wide forms
    decode and advance by their real size.  A site that still does not decode
    yields its address (an ``int``) and the sweep advances two bytes.
    """
    address = start & ~1
    while address + 2 <= end:
        item = decode_thumb_at(data, address)
        if item is None:
            yield address
            address += 2
            continue
        yield item
        address += item.size


def linear_thumb_wide(data: bytes, start: int, end: int) -> SweepResult:
    """Materialised wide-window Thumb sweep over ``[start, end)``."""
    result = SweepResult(start=start, end=end)
    for item in iter_thumb_wide(data, start, end):
        if isinstance(item, int):
            result.undecodable_halfwords.append(item)
        else:
            result.instructions.append(item)
    return result


@dataclass(frozen=True, slots=True)
class FieldExtraction:
    """One ``lsls rd,rs,#a ; lsrs rd,rd,#b`` site, as a mask/field operation.

    The pair computes ``(value << a) >> b``.  With ``b == a`` that is the plain
    mask idiom ``value & ((1 << (32 - a)) - 1)``, reported as
    ``right_shift == 0``; with ``b > a`` it keeps ``width`` bits of ``value``
    starting at bit ``right_shift``.  ``b < a`` shifts left and is not a mask,
    so it is not reported.
    """

    address: int
    right_shift: int
    width: int

    @property
    def mask(self) -> int:
        return (1 << self.width) - 1


def _shift_halfword(high: int, low: int) -> tuple[int, int, int, int] | None:
    """``(opcode, rd, rs, imm)`` for a Thumb format-1 shift, else ``None``.

    ``imm`` is left as the encoded 5-bit field, so ``imm == 0`` on ``lsrs`` is
    the architecturally different "shift by 32" form and is rejected there.
    """
    halfword = high | (low << 8)
    if (halfword & 0xE000) != 0x0000:
        return None
    opcode = (halfword >> 11) & 3
    if opcode == 3:
        return None
    imm = (halfword >> 6) & 0x1F
    rs = (halfword >> 3) & 7
    rd = halfword & 7
    if opcode in (1, 2) and imm == 0:
        return None
    return opcode, rd, rs, imm


def find_field_extractions(
    data: bytes, start: int = ROM_BASE, end: int | None = None
) -> list[FieldExtraction]:
    """Every adjacent ``lsls``/``lsrs`` mask-or-field pair in ``[start, end)``.

    A raw halfword scan, not a disassembly sweep: it cannot stop at an
    undecodable halfword, so a count of zero for a given ``(right_shift,
    width)`` is coverage evidence rather than a sweep artifact.  The caller must
    still state the range scanned.

    Both forms are reported, and both matter for a negative claim about a mask:

    * ``lsls rd,rs,#a`` followed by ``lsrs rd,rd,#a`` - the plain mask idiom
      ``value & ((1 << (32 - a)) - 1)``, reported as ``(0, 32 - a)``.  A scan
      that only accepted a strictly larger second shift would silently never
      produce ``right_shift == 0`` and would make "no site masks the low ten
      bits" vacuously true, so the two shifts are compared with ``>=``;
    * ``lsls rd,rs,#a`` followed by ``lsrs rd,rd,#b`` with ``b > a`` - a field
      extraction of ``32 - b`` bits starting at bit ``b - a``.
    """
    limit = end if end is not None else ROM_BASE + len(data)
    found: list[FieldExtraction] = []
    previous: tuple[int, int, int, int, int] | None = None
    address = start & ~1
    while address + 2 <= limit:
        offset = address - ROM_BASE
        if offset < 0 or offset + 2 > len(data):
            break
        decoded = _shift_halfword(data[offset], data[offset + 1])
        if decoded is not None and previous is not None:
            prev_address, prev_opcode, prev_rd, prev_rs, prev_imm = previous
            opcode, rd, rs, imm = decoded
            if (
                prev_opcode == 0  # lsls
                and opcode == 1  # lsrs
                and rd == prev_rd
                and rs == prev_rd
                and imm >= prev_imm
            ):
                found.append(
                    FieldExtraction(
                        address=prev_address,
                        right_shift=imm - prev_imm,
                        width=32 - imm,
                    )
                )
        previous = (address, *decoded) if decoded is not None else None
        address += 2
    return found


def linear_arm(data: bytes, start: int, end: int) -> SweepResult:
    """Resynchronising linear ARM sweep over ``[start, end)``."""
    result = SweepResult(start=start, end=end)
    address = start & ~3
    while address + 4 <= end:
        offset = address - ROM_BASE
        if offset < 0 or offset + 4 > len(data):
            break
        decoded = next(_ARM.disasm(data[offset : offset + 4], address, 4), None)
        if decoded is None:
            result.undecodable_halfwords.append(address)
            address += 4
            continue
        result.instructions.append(
            Instruction(decoded.address, decoded.size, decoded.mnemonic, decoded.op_str)
        )
        address += decoded.size
    return result


#: Second halfwords that can complete a Thumb ``BL``/``BLX``.  ``BL`` (T1) is
#: ``11 J1 1 J2 imm11`` and ``BLX`` (T2) is ``11 J1 0 J2 imm10H 0``, so the
#: masked value is one of these eight and nothing else.  This is a *necessary*
#: condition used to skip the ~99% of halfwords that cannot begin a call; the
#: decision is still made by decoding, because ``BLX`` additionally reserves
#: bit 0 and only a decoder can say what the four bytes really are.
THUMB_CALL_SECOND_HALFWORDS = (
    0xC000, 0xC800, 0xD000, 0xD800,
    0xE000, 0xE800, 0xF000, 0xF800,
)

#: The mnemonics a decoder reports for those two encodings.
THUMB_CALL_MNEMONICS = ("bl", "blx")


@dataclass(frozen=True, slots=True)
class ThumbCallSite:
    """One decoded Thumb ``BL``/``BLX`` site.

    ``kind`` is the architectural encoding - ``"bl"`` to Thumb code or
    ``"blx"`` to ARM code - because a caller census that cannot tell them apart
    cannot be checked against either.  ``target`` is the absolute destination
    with the Thumb state bit as the instruction sets it: ``BL`` targets have
    bit 0 clear by construction (its immediate is even and ``PC`` is
    halfword-aligned), and ``BLX`` targets are word-aligned.
    """

    address: int
    kind: str
    target: int

    @property
    def cleared_target(self) -> int:
        """``target`` with the Thumb state bit cleared.

        A raw Thumb code pointer carries the state bit; a call *target* does not.
        Callers that compare a call target against a stored Thumb pointer mask it
        with ``& ~1``, which this property states once instead of at each call
        site.  Masking is harmless for ``BLX``, whose target is word-aligned.
        """
        return self.target & ~1


def _thumb_call_halves(high: int, low: int) -> bool:
    """Whether the halfword pair could be a Thumb ``BL``/``BLX`` encoding."""
    if (high & 0xF800) != 0xF000:
        return False
    if (low & 0xF800) not in THUMB_CALL_SECOND_HALFWORDS:
        return False
    # BLX (T2) reserves bit 0 of the second halfword; a pair with it set is not
    # one of the two encodings. Accepting it was the old helper's entire
    # false-positive population.
    return bool(low & 0x1000) or not (low & 0x0001)


def resolve_thumb_bl(address: int, high: int, low: int) -> int:
    """Absolute target of the Thumb ``BL``/``BLX`` halfword pair at ``address``.

    Both encodings carry the same 25-bit immediate; they differ in the program
    counter it is added to, and the encoding says which applies:

    * ``BL``  (T1, second halfword bit 12 set)   -> ``target = PC + imm32``;
    * ``BLX`` (T2, second halfword bit 12 clear) -> ``target = Align(PC, 4) + imm32``.

    ``PC`` is ``address + 4``.  The alignment is load-bearing rather than
    cosmetic: a ``BLX`` at an address that is not word-aligned has its PC
    rounded *down* first, so a resolver that always used ``address + 4``
    reported those targets two bytes high.  On the canonical image that was
    2,568 of the 5,283 ``BLX`` sites, and 0 of the 24,226 ``BL`` sites - BL
    resolution was, and remains, exact.

    Raises ``ValueError`` for a halfword pair that is not one of the two
    encodings, so a caller cannot resolve arbitrary data as a call.  Every
    target this returns agrees with Capstone's own decoded operand on the
    canonical image, which is what the ROM-gated suite pins.
    """
    if not _thumb_call_halves(high, low):
        raise ValueError(
            f"{high:#06x} {low:#06x} is not a Thumb BL/BLX encoding"
        )
    sign = (high >> 10) & 1
    j1 = (low >> 13) & 1
    j2 = (low >> 11) & 1
    i1 = 1 - (j1 ^ sign)
    i2 = 1 - (j2 ^ sign)
    offset = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | ((high & 0x3FF) << 12)
        | ((low & 0x7FF) << 1)
    )
    if offset & 0x01000000:
        offset -= 0x02000000
    pc = address + 4
    if not (low & 0x1000):  # BLX (T2): Align(PC, 4)
        pc &= ~3
    return pc + offset


def iter_thumb_calls(
    data: bytes, start: int = ROM_BASE, end: int | None = None
) -> Iterator[ThumbCallSite]:
    """Every Thumb ``BL``/``BLX`` site in ``[start, end)``, by decoding.

    Considers *every halfword-aligned address* whose first halfword can begin
    one of the two encodings and offers each a four-byte window to Capstone,
    accepting the site only when the decoder returns a four-byte ``bl`` or
    ``blx``.  Nothing is decided from the halfword pair alone.

    The stride is two bytes, never the decoded instruction's size: a sweep that
    advances by ``size`` can step over a real site behind a four-byte window
    that happened to decode as something else, and a caller census must not
    depend on which of two overlapping decodes a library prefers.

    This is a *static site* enumeration.  It cannot distinguish code from data,
    so it reports every valid encoding in the requested range - including one
    that is a coincidence inside a data table.  Callers must state the range
    they scanned, and must not present the result as a reachable-caller set.
    """
    limit = end if end is not None else ROM_BASE + len(data)
    address = start & ~1
    while address + 4 <= limit:
        offset = address - ROM_BASE
        if offset < 0 or offset + 4 > len(data):
            break
        high = data[offset] | (data[offset + 1] << 8)
        low = data[offset + 2] | (data[offset + 3] << 8)
        if _thumb_call_halves(high, low):
            item = next(_THUMB.disasm(data[offset : offset + 4], address, 1), None)
            if (
                item is not None
                and item.size == 4
                and item.mnemonic in THUMB_CALL_MNEMONICS
            ):
                yield ThumbCallSite(
                    address=address,
                    kind=item.mnemonic,
                    target=resolve_thumb_bl(address, high, low),
                )
        address += 2


def scan_thumb_calls(
    data: bytes, *, start: int = ROM_BASE, end: int | None = None
) -> list[ThumbCallSite]:
    """Materialised :func:`iter_thumb_calls` over ``[start, end)``."""
    return list(iter_thumb_calls(data, start, end))


def scan_thumb_bl_callers(
    data: bytes,
    targets: set[int],
    *,
    start: int = ROM_BASE,
    end: int | None = None,
    include_blx: bool = True,
) -> dict[int, list[int]]:
    """Every decoded Thumb call site resolving to a member of ``targets``.

    The authoritative replacement for the raw-pair predicate this function used
    to be: sites come from :func:`iter_thumb_calls`, so a halfword pair that is
    not a real encoding is never reported (the old predicate invented 1,552 of
    them), and neither ``BL`` nor ``BLX`` is missed (the old predicate found
    16,196 of the accepted 29,509 sites, 54.9%).

    ``include_blx`` selects whether ``BLX`` - a call into ARM code - counts.
    Both are call sites and both are on by default; a caller interested only in
    calls that stay in Thumb code asks for ``include_blx=False``.  Use
    :func:`scan_thumb_calls` when the distinction has to be reported rather
    than filtered.

    Targets are compared with the Thumb state bit cleared, so a raw Thumb code
    pointer (``0x0803D967``) and the call target a ``BL`` records
    (``0x0803D966``) are the same key.  Every requested target is present in the
    result, so an empty list means "no caller in the scanned range" rather than
    "not asked about".
    """
    wanted = {target & ~1 for target in targets}
    found: dict[int, list[int]] = {target: [] for target in wanted}
    for site in iter_thumb_calls(data, start, end):
        if site.kind == "blx" and not include_blx:
            continue
        resolved = site.cleared_target
        if resolved in found:
            found[resolved].append(site.address)
    for sites in found.values():
        sites.sort()
    return found


def scan_word_references(
    data: bytes, values: set[int], *, aligned_only: bool = True
) -> dict[int, list[int]]:
    """Every ROM address whose 32-bit little-endian word equals one of ``values``.

    ``str.find`` over a packed needle table, so a full-image scan is cheap while
    remaining exact.  The caller must state the alignment used when reporting a
    negative result.
    """
    step = 4 if aligned_only else 2
    found: dict[int, list[int]] = {value: [] for value in values}
    needles = {value: value.to_bytes(4, "little") for value in values}
    offset = 0
    while offset + 4 <= len(data):
        chunk = data[offset : offset + 4]
        for value, needle in needles.items():
            if chunk == needle:
                found[value].append(offset + ROM_BASE)
        offset += step
    return found


def find_thumb_function_entries(
    data: bytes, start: int, end: int, *, require_lr_push: bool = True
) -> list[int]:
    """Candidate function entries: Thumb ``push`` of a list containing ``lr``."""
    entries: list[int] = []
    for item in iter_thumb(data, start, end):
        if isinstance(item, int):
            continue
        if item.mnemonic == "push" and (not require_lr_push or "lr" in item.operands):
            entries.append(item.address)
    return entries
