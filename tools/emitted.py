from __future__ import annotations

import os
import re

SLICE = re.compile(r"baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted$")
RUN = re.compile(r"_([0-9a-fA-F]{1,8})_([0-9a-fA-F]{1,8})\.bin$")
GEN = re.compile(r"gen_([0-9a-fA-F]+)\.bin$")
TOKEN = re.compile(r"^\s*INCBIN\s+(\S+)\s*$")
INCLUDE = re.compile(r"^\s*INCLUDE\s+(\S+)\s*$")
LABEL = re.compile(r"^\s*(?:\|unk_([0-9A-Fa-f]+)\||unk_([0-9A-Fa-f]{8}))\s*$")
EXPORT = re.compile(r"^\s*EXPORT\s+\|unk_[0-9A-Fa-f]+\|\s*$")
DATA = re.compile(r"^\s*(DCW|DCB|DCD)\s+(.+?)\s*$")
CITED = re.compile(r"^\s*;\s*(?:cited by\b|\d+ ldr-literal site\(s\) load\b)")
UNCITED = re.compile(r"^\s*;\s*(?:no citation:|no site names\b)")
SPACE = re.compile(r"^\s*SPACE\s+(0[xX][0-9A-Fa-f]+|\d+)\s*$")
DATA_WIDTH = {"DCW": 2, "DCB": 1, "DCD": 4}
RELATIVE = re.compile(r"^\|([A-Za-z_][A-Za-z0-9_]*)\|(\+\d+)?(?:-\s*\|([A-Za-z_][A-Za-z0-9_]*)\|"
                      r"(\+\d+)?)?$")
ADDRESS_IN_NAME = re.compile(r"([0-9A-Fa-f]{8})")


def carrier_comments(root):
    out = {}
    directory = os.path.join(root, "asm")
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".s"):
            continue
        pending = []
        for number, line in enumerate(open(os.path.join(directory, name), errors="replace"), 1):
            token = TOKEN.match(line)
            if token:
                span = SLICE.search(token.group(1))
                if span:
                    out[(int(span.group(1), 16), int(span.group(2), 16))] = list(pending)
                pending = []
                continue
            if line.strip().startswith(";"):
                pending.append((number, line.rstrip()))
                pending = pending[-6:]
            elif line.strip():
                pending = []
    return out


def token_span(token):
    for pattern in (SLICE, RUN):
        found = pattern.search(token)
        if found:
            return int(found.group(1), 16), int(found.group(2), 16)
    return None


def source_text(root, path, seen=None):
    path = os.path.abspath(path)
    seen = set() if seen is None else seen
    if path in seen:
        raise SystemExit("INCLUDE cycle at %s" % path)
    seen.add(path)
    out = []
    for line in open(path, errors="replace").read().split("\n"):
        found = INCLUDE.match(line)
        if not found:
            out.append(line)
            continue
        name = os.path.basename(found.group(1))
        out.append("; INCLUDE %s" % name)
        for candidate in (os.path.join(os.path.dirname(path), name), os.path.join(root, name)):
            if os.path.exists(candidate):
                out.append(source_text(root, candidate, seen))
                break
    return "\n".join(out)


def incbin_tokens(text):
    return list(dict.fromkeys(found.group(1)
                              for found in (TOKEN.match(line) for line in text.split("\n")) if found))


def operand_value(text):
    text = text.strip()
    try:
        return int(text, 16)
    except ValueError:
        pass
    found = RELATIVE.match(text)
    if not found:
        return None
    drawn = []
    for name, offset in ((found.group(1), found.group(2)), (found.group(3), found.group(4))):
        if name is None:
            continue
        digits = ADDRESS_IN_NAME.search(name)
        if not digits:
            return None
        drawn.append(int(digits.group(1), 16) + int(offset[1:] if offset else 0))
    return drawn[0] - drawn[1] if len(drawn) == 2 else drawn[0]


def token_ranges(text):
    tokens = incbin_tokens(text)
    spans = [None] * len(tokens)
    following = None
    for index in range(len(tokens) - 1, -1, -1):
        token = tokens[index]
        found = token_span(token)
        if found is None:
            single = GEN.search(token)
            if single is not None:
                start = int(single.group(1), 16)
                if following is not None and following > start:
                    found = (start, following)
        spans[index] = found
        if found is not None:
            following = found[0]
    return [(token, span) for token, span in zip(tokens, spans) if span is not None]


def labeled_bytes(text):
    rows, address, data = [], None, bytearray()
    for line in text.split("\n"):
        body = line.split(";", 1)[0].strip()
        label = LABEL.match(body)
        if label:
            if address is not None and data:
                rows.append((address, bytes(data)))
            address, data = int(label.group(1) or label.group(2), 16) - 0x08000000, bytearray()
            continue
        if not body or EXPORT.match(body):
            continue
        found = DATA.match(body)
        if not found:
            space = SPACE.match(body)
            if space is not None and address is not None:
                data += bytes(int(space.group(1), 0))
                continue
            if address is not None and data:
                rows.append((address, bytes(data)))
            address, data = None, bytearray()
            continue
        if address is None:
            continue
        width = DATA_WIDTH[found.group(1)]
        for value in found.group(2).split(","):
            number = operand_value(value)
            if number is None:
                raise SystemExit("a labeled run carries the operand %r, which is neither a number "
                                 "nor the relative label spelling (P-471)" % value.strip())
            data += (number & 0xFFFFFFFF).to_bytes(width, "little")
    if address is not None and data:
        rows.append((address, bytes(data)))
    return rows


def labeled_rows(text):
    rows = []
    for address, data in sorted(labeled_bytes(text)):
        if rows and rows[-1][1] == address:
            rows[-1][1] += len(data)
            rows[-1][2] += data
        else:
            rows.append([address, address + len(data), data])
    return [(low, high, blob) for low, high, blob in rows]


def fragment_symbols(text):
    rows, address, cited = [], None, None
    for line in text.split("\n"):
        body = line.split(";", 1)[0].strip()
        label = LABEL.match(body)
        if label:
            address, cited = int(label.group(1) or label.group(2), 16) - 0x08000000, None
            continue
        if address is None:
            continue
        if CITED.search(line):
            cited = True
            continue
        if UNCITED.search(line):
            cited = False
            continue
        if not body or EXPORT.match(body):
            continue
        token = TOKEN.match(body)
        if token:
            span = token_span(token.group(1))
            if span is not None and span[0] == address and SLICE.search(token.group(1)):
                rows.append((address, span[1], token.group(1), bool(cited)))
        address = None
    return rows


def source_rows(root, rom, text, span=None):
    def wanted(low, high):
        return span is None or (low < span[1] and high > span[0])

    rows, problems = [], []
    for token, token_range in token_ranges(text):
        if not wanted(*token_range):
            continue
        path = os.path.join(root, token.replace("\\", os.sep))
        if not os.path.exists(path):
            problems.append("%s is missing" % token)
            continue
        blob = open(path, "rb").read()
        if blob != rom[token_range[0]:token_range[1]]:
            problems.append("%s is not the retail bytes" % token)
            continue
        rows.append((token_range[0], token_range[1], token, blob))
    for low, high, blob in labeled_rows(text):
        if not wanted(low, high):
            continue
        if blob != rom[low:high]:
            problems.append("the labeled data at 0x%06X is not the retail bytes" % low)
            continue
        rows.append((low, high, None, blob))
    rows.sort()
    return rows, problems


def row_name(row):
    low, high, name, _ = row
    return name if name else "baserom.gba_0x%x_0x%x.extracted" % (low, high)


def tiling_problems(sections, rows, name_of):
    problems = []
    index = 0
    for section in sections:
        wanted = name_of(section)
        at = section.start
        while at < section.end:
            if index == len(rows):
                problems.append("%s stops at 0x%06X of 0x%06X" % (wanted, at, section.end))
                break
            low, high, _, _ = rows[index]
            if low != at:
                problems.append("%s: the source jumps from 0x%06X to 0x%06X" % (wanted, at, low))
                break
            carried = row_name(rows[index])
            foreign = carried.endswith(".bin")
            if carried != wanted and carried != "baserom.gba_0x%x_0x%x.extracted" % (low, high) \
                    and not foreign:
                problems.append("%s is carried by %s, which names neither it nor its own bytes"
                                % (wanted, carried))
                break
            if high > section.end:
                problems.append("%s runs to 0x%06X, past the section's end 0x%06X"
                                % (carried, high, section.end))
                break
            at = high
            index += 1
    for row in rows[index:]:
        problems.append("%s is carried by the source and by no planned section" % row_name(row))
    return problems
