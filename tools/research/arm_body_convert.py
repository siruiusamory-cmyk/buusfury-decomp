from __future__ import annotations

import json
import os
import re
import shutil
import struct
import subprocess
import sys

import arm_bodies
import arm_evidence

DEV = os.path.join(arm_bodies.ROOT, "build", "arm_bodies")
LDM_STM = re.compile(r"^(ldm|stm)(ia|ib|da|db|fd|fa|ed|ea)?"
                     r"(eq|ne|cs|hs|cc|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)$")
LDM_STM_BARE = re.compile(r"^(ldm|stm)$")
LDM_STM_COND = re.compile(r"^(ldm|stm)(eq|ne|cs|hs|cc|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)"
                          r"(ia|ib|da|db|fd|fa|ed|ea)?$")
SHIFTS = ("lsl", "lsls", "lsr", "lsrs", "asr", "asrs", "ror", "rors", "rrx", "rrxs")
CONDITIONS = ("eq", "ne", "cs", "hs", "cc", "lo", "mi", "pl", "vs", "vc", "hi", "ls", "ge", "lt",
              "gt", "le")
PSEUDO = {"push": "stmdb sp!,", "pop": "ldmia sp!,",
          "ldmfd": "ldmia", "stmfd": "stmdb", "ldmia": "ldmia", "stmia": "stmia"}
TOKEN_LINE = re.compile(r"^(\s*INCBIN\s+)(baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)"
                        r"\.extracted)(\s*)$")


def workspace(dev=None):
    dev = DEV if dev is None else dev
    if not os.path.isdir(dev):
        os.makedirs(dev)
    return dev


def first_line(result):
    text = (result.stdout + result.stderr).strip()
    return text.split("\n")[0].strip() if text else "no output, exit %d" % result.returncode


def assemble(text, base, dev=None):
    work = workspace(dev)
    source = os.path.join(work, "one.s")
    object_path = os.path.join(work, "one.o")
    scatter = os.path.join(work, "one.scf")
    axf = os.path.join(work, "one.axf")
    binary = os.path.join(work, "one.bin")
    with open(source, "w", newline="\n") as handle:
        handle.write(text)
    with open(scatter, "w", newline="\n") as handle:
        handle.write("LOAD 0x%08X\n{\n    ARM 0x%08X\n    {\n        one.o (+RO)\n    }\n}\n"
                     % (base, base))
    result = subprocess.run(["armasm", source, "-o", object_path], capture_output=True, text=True)
    refusals = []
    for line in (result.stdout + result.stderr).split("\n"):
        found = re.search(r"line (\d+): Error: (\S+: [^\n]*)", line)
        if found:
            refusals.append((int(found.group(1)), found.group(2).strip()))
    if result.returncode != 0:
        if not refusals:
            raise SystemExit("armasm failed and named no line, so no body can be judged: %s"
                             % first_line(result))
        return None, refusals
    for tool, step in (("armlink", ["armlink", object_path, "-scatter", scatter, "-o", axf]),
                       ("fromelf", ["fromelf", axf, "-bin", "-o", binary])):
        got = subprocess.run(step, capture_output=True, text=True)
        if got.returncode != 0:
            refusals.append((0, "%s: %s" % (tool, first_line(got))))
            return None, refusals
    with open(binary, "rb") as handle:
        return handle.read(), refusals


def operands_of(text):
    text = re.sub(r"#(-0x[0-9a-fA-F]+)", lambda match: "#%d" % -int(match.group(1), 0), text)
    if text.count("#") >= 2:
        text = re.sub(r", #(\d+)$", lambda match: ", %s" % match.group(1), text)
    return text


def shift_spelling(mnemonic, operands):
    lowered = mnemonic.lower()
    stems = ("lsl", "lsr", "asr", "ror", "rrx")
    condition = ""
    for candidate in sorted(CONDITIONS, key=len, reverse=True):
        if lowered.endswith(candidate) and lowered[: -len(candidate)].rstrip("s") in stems:
            condition, lowered = candidate.upper(), lowered[: -len(candidate)]
            break
    sets_flags = lowered.endswith("s") and lowered[:-1] in stems
    stem = lowered[:-1] if sets_flags else lowered
    if stem not in stems:
        return None
    parts = [part.strip() for part in operands.split(",")]
    if stem == "rrx":
        if len(parts) != 2:
            return None
        shift = "RRX"
    else:
        if len(parts) != 3:
            return None
        shift = "%s %s" % (stem.upper(), parts[2])
    head = "MOVS" if (sets_flags or lowered.endswith("s")) else "MOV"
    return "\t%-8s %s, %s, %s" % (head + condition, parts[0], parts[1], shift)


def flag_order(mnemonic):
    lowered = mnemonic.lower()
    for condition in CONDITIONS:
        if lowered.endswith("s" + condition):
            return lowered[: -len(condition) - 1].upper() + condition.upper() + "S"
    return mnemonic.upper()


def spell(mnemonic, operands):
    lowered = mnemonic.lower()
    operands = operands_of(operands)
    shifted = shift_spelling(mnemonic, operands)
    if shifted is not None:
        return shifted
    if lowered in SHIFTS:
        return None
    if lowered in ("push", "pop"):
        return "\t" + "%-8s %s" % (PSEUDO[lowered].split()[0].upper(),
                                   PSEUDO[lowered].split()[1] + " " + operands)
    if LDM_STM_BARE.match(lowered):
        return "\t%-8s %s" % (lowered.upper() + "IA", operands)
    found = LDM_STM.match(lowered) or LDM_STM_COND.match(lowered)
    if found:
        base, rest_a, rest_b = found.group(1), found.group(2), found.group(3)
        parts = [part for part in (rest_a, rest_b) if part]
        condition = next((part for part in parts if part in
                          ("eq", "ne", "cs", "hs", "cc", "lo", "mi", "pl", "vs", "vc", "hi",
                           "ls", "ge", "lt", "gt", "le")), "")
        mode = next((part for part in parts if part not in
                     ("eq", "ne", "cs", "hs", "cc", "lo", "mi", "pl", "vs", "vc", "hi", "ls",
                      "ge", "lt", "gt", "le")), "")
        condition = {"hs": "cs", "lo": "cc"}.get(condition, condition)
        head = base + condition.upper() + mode.upper()
        return "\t" + "%-8s %s" % (head, operands)
    return "\t" + "%-8s %s" % (flag_order(mnemonic), operands)


def branch_targets(start, end, instructions):
    inside = set()
    for offset, _size, mnemonic, operands, _raw in instructions:
        if not mnemonic.startswith("b"):
            continue
        found = re.search(r"#(0x[0-9a-f]+|\d+)", operands)
        if not found:
            continue
        target = int(found.group(1), 0)
        if arm_bodies.ROM_BASE + start <= target < arm_bodies.ROM_BASE + end:
            inside.add(target)
    return inside


BRANCH = re.compile(r"#(0x[0-9a-fA-F]+|\d+)$")
TERMINAL = ("b", "bx")
RETURNS_VIA_PC = re.compile(r"\bpc\b")


def enters_next(mnemonic, operands):
    lowered = mnemonic.lower()
    for condition in CONDITIONS:
        if lowered.endswith(condition):
            return True
    if lowered in TERMINAL:
        return False
    if lowered.startswith(("pop", "ldm")) and RETURNS_VIA_PC.search(operands):
        return False
    return True


def address_word(value):
    return (0x08000000 <= value < 0x0A000000 or 0x02000000 <= value < 0x02040000
            or 0x03000000 <= value < 0x03008000 or 0x07000000 <= value < 0x08000000)


def pc_loaded(start, end, instructions):
    out = set()
    for offset, _size, mnemonic, operands, _word in instructions:
        if mnemonic not in ("ldr", "ldrbt", "ldrt", "ldrh", "ldrb"):
            continue
        found = re.search(r"\[pc, #(0x[0-9a-f]+|\d+)\]", operands)
        if found:
            out.add((offset + 8 + int(found.group(1), 0)) & ~3)
    return out


def unreachable(start, end, instructions, labels):
    targets = {target - arm_bodies.ROM_BASE
               for target in branch_targets(start, end, instructions) | set(labels)}
    reached, fall = set(), True
    for index, (offset, _size, mnemonic, operands, _word) in enumerate(instructions):
        if index == 0 or fall or offset in targets:
            reached.add(offset)
        fall = enters_next(mnemonic, operands)
    out = {offset: "no branch or fall-through reaches this word"
           for offset, _size, _m, _o, _w in instructions if offset not in reached}
    loaded = pc_loaded(start, end, instructions)
    words = {offset: struct.unpack_from("<I", word)[0]
             for offset, size, _m, _o, word in instructions if size == 4}
    for offset, value in words.items():
        if offset in out or not address_word(value):
            continue
        previous, following = words.get(offset - 4), words.get(offset + 4)
        in_run = (previous is not None and address_word(previous)) or \
            (following is not None and address_word(following))
        if in_run or offset in loaded:
            out[offset] = ("address word 0x%08X: pool data this body carries, not an instruction"
                           % value)
    return out


def label_table():
    table = {}
    for name in sorted(os.listdir(os.path.join(arm_bodies.ROOT, "asm"))):
        if not name.endswith(".s"):
            continue
        for line in open(os.path.join(arm_bodies.ROOT, "asm", name), errors="replace"):
            found = re.match(r"^\s*\|([A-Za-z_][A-Za-z0-9_]*)\|\s*$", line)
            if found:
                digits = re.fullmatch(r"(?:sub|loc|unk|gap|dat|arm)_([0-9A-Fa-f]{8})",
                                      found.group(1))
                if digits:
                    table.setdefault(int(digits.group(1), 16), "|%s|" % found.group(1))
    return table


def branch_text(mnemonic, operands, address, start, end, labels, table, arm_spans=()):
    found = BRANCH.search(operands)
    if not found:
        return None
    target = int(found.group(1), 0)
    if arm_bodies.ROM_BASE + start <= target < arm_bodies.ROM_BASE + end:
        return "\t%-8s |arm_%08X|" % (mnemonic.upper(), target)
    if not any(low <= target < high for low, high in arm_spans):
        return None
    return "\t%-8s |arm_%08X|" % (mnemonic.upper(), target)


def spell_target(mnemonic, operands, address, start, end, labels, table, arm_spans=()):
    if mnemonic.startswith("b") and mnemonic not in ("bic", "blx", "bkpt") and \
            BRANCH.search(operands):
        return branch_text(mnemonic, operands, address, start, end, labels, table, arm_spans)
    return spell(mnemonic, operands)


def body_lines(start, end, instructions, pool, labels, raw=None, table=None, gaps=(), bypass=(),
               arm_spans=()):
    table = table or {}
    raw = raw or {}
    bypass = set(bypass)
    lines, where = [], []
    for offset, _size, mnemonic, operands, raw_word in instructions:
        address = arm_bodies.ROM_BASE + offset
        if address in labels or offset in raw:
            lines.append("|arm_%08X|" % address)
            where.append(None)
        text = spell_target(mnemonic, operands, address, start, end, labels, table, arm_spans)
        if offset in raw:
            lines.append("\tDCD     0x%08X\t; %s %s%s" %
                         (struct.unpack_from("<I", raw_word)[0], mnemonic, operands,
                          " | " + raw[offset] if raw[offset] else ""))
        elif offset in bypass and text is not None:
            lines.append("\tDCD     0x%08X\t; probe placeholder for: %s" %
                         (struct.unpack_from("<I", raw_word)[0], text.strip()))
        elif text is None:
            lines.append("\tDCD     0x%08X\t; %s %s | no assembler spelling" %
                         (struct.unpack_from("<I", raw_word)[0], mnemonic, operands))
        else:
            lines.append(text)
        where.append(offset)
    for low, high in gaps:
        offset = low
        while offset < high:
            if high - offset >= 4:
                lines.append("|arm_%08X|" % (arm_bodies.ROM_BASE + offset))
                where.append(None)
                reason = ("pool word the body loads" if offset in pool
                          else "data the body does not load")
                lines.append("\tDCD     0x%08X\t; %s" %
                             (struct.unpack_from("<I", arm_bodies.ROM, offset)[0], reason))
                where.append(offset)
                offset += 4
            else:
                lines.append("\tDCB     0x%02X" % arm_bodies.ROM[offset])
                where.append(offset)
                offset += 1
    return lines, where


def body_text(lines):
    return "\tAREA |arm|, CODE, READONLY\n\tCODE32\n" + "\n".join(lines) + "\n\tEND\n"


def build_body(row, arm_spans=(), arm_targets=()):
    start, end = row[3], row[4]
    instructions, gaps = arm_bodies.arm_decode(start, end)
    pool = arm_bodies.pool_words(start, end, gaps)
    labels = branch_targets(start, end, instructions) | \
        set(arm_bodies.ROM_BASE + offset for offset in pool) | \
        {target for target in arm_targets
         if arm_bodies.ROM_BASE + start <= target < arm_bodies.ROM_BASE + end}
    want = arm_bodies.ROM[start:end]
    table = label_table()
    raw = unreachable(start, end, instructions, labels)
    labels = {address for address in labels if address - arm_bodies.ROM_BASE not in raw}
    for offset, _size, mnemonic, operands, _word in instructions:
        if not (mnemonic.startswith("b") and mnemonic not in ("bic", "blx", "bkpt")):
            continue
        target = BRANCH.search(operands)
        if target is None:
            continue
        address = int(target.group(1), 0)
        inside = arm_bodies.ROM_BASE + start <= address < arm_bodies.ROM_BASE + end
        if inside:
            continue
        if not any(low <= address < high for low, high in arm_spans):
            raw.setdefault(offset, "armlink L6239E: target 0x%08X is Thumb and these areas do "
                                   "not interwork" % address)
    bypass = {offset for offset, _s, mnemonic, operands, _w in instructions
              if mnemonic.startswith("b") and mnemonic not in ("bic", "blx", "bkpt")
              and offset not in raw
              and spell_target(mnemonic, operands, arm_bodies.ROM_BASE + offset, start, end,
                               labels, table, arm_spans) is not None}
    probe_raw = dict(raw)
    for offset in bypass:
        probe_raw.setdefault(offset, "")
    lines, where = body_lines(start, end, instructions, pool, labels, probe_raw, table, gaps,
                              bypass, arm_spans)
    got, refusals = assemble(body_text(lines), arm_bodies.ROM_BASE + start)
    for _attempt in range(8):
        if got == want:
            break
        changed = False
        for number, message in refusals:
            offset = where[number - 3] if 0 <= number - 3 < len(where) else None
            if offset is not None and offset not in raw:
                raw[offset] = "armasm %s" % message
                changed = True
        if got is not None:
            for offset, size, _mnemonic, _operands, _word in instructions:
                if offset in probe_raw:
                    continue
                piece = got[offset - start:offset - start + size]
                if piece != arm_bodies.ROM[offset:offset + size]:
                    raw[offset] = "the assembler does not reproduce this word"
                    changed = True
        if not changed:
            break
        probe_raw = dict(raw)
        for offset in bypass:
            probe_raw.setdefault(offset, "")
        lines, where = body_lines(start, end, instructions, pool, labels, probe_raw, table, gaps,
                                  bypass, arm_spans)
        got, refusals = assemble(body_text(lines), arm_bodies.ROM_BASE + start)
    if got != want:
        return None, 0, "the body does not reassemble byte-exact"
    lines, _where = body_lines(start, end, instructions, pool, labels, raw, table, gaps, (),
                               arm_spans)
    return lines, len(raw), "%d raw word(s)" % len(raw) if raw else ""


def replacement(row, lines):
    return ["\tCODE32"] + lines + ["\tCODE16"]


def arm_targets_of(rows):
    out = set()
    for _flags, row in rows:
        instructions, _gaps = arm_bodies.arm_decode(row[3], row[4])
        for _offset, _size, mnemonic, operands, _word in instructions:
            if not (mnemonic.startswith("b") and mnemonic not in ("bic", "blx", "bkpt")):
                continue
            found = BRANCH.search(operands)
            if found:
                out.add(int(found.group(1), 0))
    return out


def convert(write=False):
    references = arm_evidence.load() if os.path.exists(arm_evidence.OUT) else None
    rows, without = [], {}
    for flags, row in arm_bodies.enumerated():
        evidence, site = arm_evidence.evidence_for(row, references)
        if evidence in ("veneer", "arm-xref"):
            rows.append((flags, row, evidence, site))
        else:
            without[(row[0], row[3], row[4])] = (evidence, site)
    os.makedirs(DEV, exist_ok=True)
    arm_spans = [(row[3] + arm_bodies.ROM_BASE, row[4] + arm_bodies.ROM_BASE)
                 for _flags, row, _evidence, _site in rows]
    arm_targets = arm_targets_of([(flags, row) for flags, row, _evidence, _site in rows])
    planned, failures, evidence_of = {}, [], {}
    for flags, row, evidence, site in rows:
        lines, raw, _reason = build_body(row, arm_spans, tuple(arm_targets))
        evidence_of[(row[0], row[1])] = (evidence, site)
        if lines is None:
            failures.append(row)
            continue
        planned[(row[0], row[1])] = (row, lines)
        print("  %-4s %-20s:%-6d 0x%06x..0x%06x %5d B %-9s %s"
              % (flags, row[0], row[1], row[3], row[4], row[4] - row[3], evidence, site))
    print("byte-exact: %d of %d with ARM-state evidence" % (len(planned), len(rows)))
    for row in failures:
        print("  REFUSED %s:%d 0x%06x..0x%06x" % (row[0], row[1], row[3], row[4]))
    if not write:
        return planned, failures
    manifest = {"converted": [{"file": row[0], "line": row[1], "start": row[3], "end": row[4],
                               "evidence": evidence_of[(row[0], row[1])][0],
                               "site": evidence_of[(row[0], row[1])][1]}
                              for row, _lines in planned.values()]}
    with open(os.path.join(DEV, "manifest.json"), "w") as handle:
        json.dump(manifest, handle, indent=1)
    touched = 0
    for name in sorted({row[0] for row, _lines in planned.values()}):
        path = os.path.join(arm_bodies.ROOT, "asm", name)
        source = open(path, errors="replace").read().split("\n")
        out = []
        for number, line in enumerate(source, 1):
            found = TOKEN_LINE.match(line)
            entry = planned.get((name, number)) if found else None
            if entry is None:
                out.append(line)
                continue
            out.extend(replacement(entry[0], entry[1]))
            touched += 1
        with open(path, "w", newline="\n") as handle:
            handle.write("\n".join(out))
    print("rewrote %d row(s) in %d file(s)"
          % (touched, len({row[0] for row, _lines in planned.values()})))
    if touched != len(planned):
        raise SystemExit("%d row(s) planned but %d rewritten: the manifest and the source disagree"
                         % (len(planned), touched))
    return planned, failures


def check():
    planned, failures = convert(write=False)
    return 0 if not failures else 1


def main(argv=None):
    write = "--write" in (argv or sys.argv[1:])
    planned, failures = convert(write=write)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
