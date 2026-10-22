from __future__ import annotations

import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, os.path.join(ROOT, "tools", "gate")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import residual_index  # noqa: E402

RESEARCH = os.path.join(ROOT, "docs", "research")
DOC_OUT = os.path.join(RESEARCH, "OTHERS_FOUND_TRIAGE.md")
GROUP_BYTES = 4096
KINDS = (
    ("code", "a decoded pc-literal load whose word is an address in the row"),
    ("data", "the MapEntry `+0x30` field site a carrier comment records, handed to the opcode interpreter"),
    ("runtime", "a read of the row observed at run time"),
)
STEPS = (
    ("extent", "an extent an existing tool derives now"),
    ("reader", "a new reader, named by the code address that supplies its index or its end"),
    ("null", "a measured null"),
    ("blocked", "a reader no automated run reached, so the census states no index"),
)
DISPOSITIONS = {
    "code:0x08038B98": {
        "step": "null",
        "instrument": "`tools/research/endrom_readers.py`: the pc-literal channel and the play read log",
        "sample_doc": "docs/research/ENDROM_LAYOUTS.md",
        "sample": "the base only: at `0x08038B9A` `0068` `ldr r0,[r0]` it reads one word of the object, "
                  "not of the row",
        "moves": 0,
        "assumption": "",
    },
    "code:0x0801B2F6": {
        "step": "blocked",
        "instrument": "`docs/research/ENDROM_INDEX_CENSUS.md`: the read watch over the row's "
                      "35,408 B in 102 map runs",
        "sample_doc": "docs/research/ENDROM_INDEX_CENSUS.md",
        "sample": "no automated run read a byte of the row",
        "moves": 0,
        "assumption": "",
    },
    "runtime": {
        "step": "null",
        "instrument": "the read log the play sitting produced, one line per (row, pc)",
        "sample_doc": "docs/research/R02_NULL_CENSUS.md",
        "sample": "read at run time from 3 site(s); no field, no count and no extent measured "
                  "inside the row",
        "moves": 0,
        "assumption": "",
    },
    "code:0x08036A62": {
        "step": "null",
        "instrument": "`docs/research/ENDROM_LAYOUTS.md`: the reader's offsets inside the row",
        "sample_doc": "docs/research/ENDROM_LAYOUTS.md",
        "sample": "a width x height copy, plus one word of the row read as `ldr r1,[r1,#4]`",
        "moves": 0,
        "assumption": "",
    },
    "code:0x0801FFFC": {
        "step": "null",
        "instrument": "`docs/research/ENDROM_LAYOUTS.md`: the reader's offsets inside the row",
        "sample_doc": "docs/research/ENDROM_LAYOUTS.md",
        "sample": "the same piece copy, one or two pieces",
        "moves": 0,
        "assumption": "",
    },
    "code:0x0802472C": {
        "step": "null",
        "instrument": "`docs/research/ENDROM_INDEX_CENSUS.md`: the read watch over the row's "
                      "16,112 B in 102 map runs",
        "sample_doc": "docs/research/ENDROM_INDEX_CENSUS.md",
        "sample": "the watch reached index 2 of the 268 whole",
        "moves": 0,
        "assumption": "",
    },
    "code:0x0800B57E": {
        "step": "null",
        "instrument": "`docs/research/ENDROM_BOUND_CENSUS.md`: the copy's source literal and the "
                      "copy body",
        "sample_doc": "docs/research/ENDROM_BOUND_CENSUS.md",
        "sample": "the copy at `0x0800B586` `f03d` `fdd7` `bl 0x08049138` takes `0x0800B57E` `a04a`",
        "moves": 0,
        "assumption": "",
    },
    "data:0x08008CEE": {
        "step": "null",
        "instrument": "`tools/research/opcode_stream.py`: the opcode table proven from the "
                      "interpreter at `0x08004038`",
        "sample_doc": "docs/research/OPCODE_STREAM_CENSUS.md",
        "sample": "carry a stream that ends on `0x11` at the stop column",
        "moves": 0,
        "assumption": "",
    },
    "code:0x0802C7CA": {
        "step": "null",
        "instrument": "`docs/research/ENDROM_LAYOUTS.md`: the reader's offsets inside the row",
        "sample_doc": "docs/research/ENDROM_LAYOUTS.md",
        "sample": "one 12-byte piece and its copy",
        "moves": 0,
        "assumption": "",
    },
    "code:0x08036FC2": {
        "step": "null",
        "instrument": "`tools/research/endrom_readers.py`: the pc-literal channel",
        "sample_doc": "docs/research/ENDROM_NULL_CENSUS.md",
        "sample": "00036FC2 ldr [pc] 0x037238 = 0x0875F808; 9 naming word(s)",
        "moves": 0,
        "assumption": "",
    },
    "code:0x0802A840": {
        "step": "null",
        "instrument": "`docs/research/ENDROM_LAYOUTS.md`: the reader's offsets inside the row",
        "sample_doc": "docs/research/ENDROM_LAYOUTS.md",
        "sample": "`ldr r0,[r0]` on the base, then a call with the word",
        "moves": 0,
        "assumption": "",
    },
    "code:0x0801D5F8": {
        "step": "null",
        "instrument": "`tools/research/endrom_readers.py`: the pc-literal channel",
        "sample_doc": "docs/research/ENDROM_NULL_CENSUS.md",
        "sample": "0001D5F8 ldr [pc] 0x01D958 = 0x0871E9D8; 12 naming word(s)",
        "moves": 0,
        "assumption": "",
    },
    "code:0x0802211A": {
        "step": "null",
        "instrument": "`tools/research/endrom_readers.py`: the pc-literal channel",
        "sample_doc": "docs/research/ENDROM_NULL_CENSUS.md",
        "sample": "0002211A ldr [pc] 0x0222DC = 0x0872A6F8; 15 naming word(s)",
        "moves": 0,
        "assumption": "",
    },
    "code:0x08019B0A": {
        "step": "null",
        "instrument": "`docs/research/ENDROM_LAYOUTS.md`: the reader's offsets inside the row",
        "sample_doc": "docs/research/ENDROM_LAYOUTS.md",
        "sample": "the object's base word and one more",
        "moves": 0,
        "assumption": "",
    },
    "code:0x0803C31E": {
        "step": "blocked",
        "instrument": "`docs/research/ENDROM_INDEX_CENSUS.md`: the read watch over the row's "
                      "4,468 B in 102 map runs",
        "sample_doc": "docs/research/ENDROM_INDEX_CENSUS.md",
        "sample": "no automated run read a byte of the row",
        "moves": 0,
        "assumption": "",
    },
    "code:0x08037C74": {
        "step": "null",
        "instrument": "`tools/research/endrom_readers.py`: the pc-literal channel",
        "sample_doc": "docs/research/ENDROM_NULL_CENSUS.md",
        "sample": "00037C74 ldr [pc] 0x037D48 = 0x0876BA78; 21 naming word(s)",
        "moves": 0,
        "assumption": "",
    },
    "code:0x080293E8": {
        "step": "null",
        "instrument": "`tools/research/endrom_readers.py`: the pc-literal channel",
        "sample_doc": "docs/research/ENDROM_NULL_CENSUS.md",
        "sample": "000293E8 ldr [pc] 0x0295C4 = 0x0874F08C; 8 naming word(s)",
        "moves": 0,
        "assumption": "",
    },
}


def others(rows=None):
    rows = residual_index.measure() if rows is None else rows
    return [row for row in rows if row["verdict"] == residual_index.OTHERS]


def kind_of(row):
    return row["references"].split(":")[0]


def groups(rows):
    out = collections.OrderedDict()
    for row in rows:
        out.setdefault(row["references"], []).append(row)
    return out


def big_groups(rows):
    return [(reference, found) for reference, found in groups(rows).items()
            if sum(row["bytes"] for row in found) >= GROUP_BYTES]


def small_groups(rows):
    return [(reference, found) for reference, found in groups(rows).items()
            if sum(row["bytes"] for row in found) < GROUP_BYTES]


def tally(rows, key):
    out = collections.defaultdict(lambda: [0, 0])
    for row in rows:
        out[key(row)][0] += 1
        out[key(row)][1] += row["bytes"]
    return out


def regions_text(found):
    return ", ".join("`%s`" % region for region in sorted({row["region"] for row in found}))


def gate_figures():
    import gate

    return gate.raw_classes()


def doc_text(rows):
    classes = residual_index.totals(residual_index.measure())
    kinds = tally(rows, kind_of)
    regions = tally(rows, lambda row: row["region"])
    total_rows = len(rows)
    total_bytes = sum(row["bytes"] for row in rows)
    referenced, _cited, _runtime, unreferenced = gate_figures()
    big = big_groups(rows)
    small = small_groups(rows)
    lines = []
    add = lines.append
    add("# Others found: the rows a citation names and no extent bounds")
    add("")
    add("Generated by `tools/research/others_found_triage.py` (`python tools/research/others_found_triage.py`).")
    add("One line per group of `docs/research/RAW_REMAINDER.csv` rows in the index's `others found` class,")
    add("grouped by the citation `docs/research/RESIDUAL_LEDGER.csv` carries for the row. `--check`")
    add("re-derives this file, refuses a group of 4 KiB or more with no measured next step, refuses a")
    add("next step for a group under 4 KiB, and asserts the totals against the index and the gate.")
    add("")
    add("**The class is %d rows / %d B; the gate's raw-data total is %d B, so %d B of it is not in"
        % (total_rows, total_bytes, referenced, referenced - total_bytes))
    add("this class.**")
    add("")
    add("## The class, in the index's terms")
    add("")
    add("`docs/research/residual_index.py` calls a row `%s` when the ledger states a citation for it and"
        % residual_index.OTHERS)
    add("no census line states its extent. The three channels are the ones the ledger records:")
    add("")
    for name, states in KINDS:
        add("- `%s`: %s, %d rows / %d B."
            % (name, states, kinds[name][0], kinds[name][1]))
    add("")
    add("The `code` and `runtime` bytes are the gate's own channels: its cited %d B and its"
        % _cited)
    add("runtime-cited %d B. The `data` bytes sit in the gate's unreferenced %d B, because a recorded"
        % (_runtime, unreferenced))
    add("field site is not a code-site citation.")
    add("")
    add("## By citation kind")
    add("")
    add("| citation | rows | bytes | what the channel states |")
    add("|---|---|---|---|")
    for name, states in KINDS:
        add("| `%s` | %d | %d | %s |" % (name, kinds[name][0], kinds[name][1], states))
    add("| **total** | **%d** | **%d** | |" % (total_rows, total_bytes))
    add("")
    add("## By region")
    add("")
    add("| region | code rows | code bytes | data rows | data bytes | runtime rows | runtime bytes | "
        "rows | bytes |")
    add("|---|---|---|---|---|---|---|---|---|")
    held = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for row in rows:
        got = held[row["region"]][kind_of(row)]
        got[0] += 1
        got[1] += row["bytes"]
    for region in sorted(held):
        cells = [region]
        count = size = 0
        for name, _states in KINDS:
            cells.append(str(held[region][name][0]))
            cells.append(str(held[region][name][1]))
            count += held[region][name][0]
            size += held[region][name][1]
        add("| `%s` | %s | %d | %d |" % (cells[0], " | ".join(cells[1:]), count, size))
    add("")
    add("## By the reader or the code address")
    add("")
    add("Every group, bytes first. `code` addresses are the pc of a decoded literal load, `data` is")
    add("the MapEntry field site a carrier comment records, and `runtime` carries no address.")
    add("")
    add("| citation | kind | rows | bytes | region(s) |")
    add("|---|---|---|---|---|")
    ordered = sorted(groups(rows).items(), key=lambda item: (-sum(row["bytes"] for row in item[1]),
                                                             item[0]))
    for reference, found in ordered:
        add("| `%s` | `%s` | %d | %d | %s |"
            % (reference, kind_of(found[0]), len(found), sum(row["bytes"] for row in found),
               regions_text(found)))
    add("")
    add("The %d groups under 4 KiB hold %d rows / %d B, and the %d groups at or above 4 KiB hold"
        % (len(small), sum(len(found) for _reference, found in small),
           sum(sum(row["bytes"] for row in found) for _reference, found in small), len(big)))
    add("%d rows / %d B."
        % (sum(len(found) for _reference, found in big),
           sum(sum(row["bytes"] for row in found) for _reference, found in big)))
    add("")
    add("## The 20 rows with the most bytes")
    add("")
    add("| row | bytes | region | class | citation |")
    add("|---|---|---|---|---|")
    for row in sorted(rows, key=lambda item: -item["bytes"])[:20]:
        add("| `0x%06X..0x%06X` | %d | `%s` | `%s` | `%s` |"
            % (row["start"], row["end"], row["bytes"], row["region"], row["class"],
               row["references"]))
    add("")
    add("## The 20 readers or addresses with the most bytes")
    add("")
    add("| citation | kind | rows | bytes | region(s) |")
    add("|---|---|---|---|---|")
    for reference, found in ordered[:20]:
        add("| `%s` | `%s` | %d | %d | %s |"
            % (reference, kind_of(found[0]), len(found), sum(row["bytes"] for row in found),
               regions_text(found)))
    add("")
    add("## The next step of every group of 4 KiB or more")
    add("")
    add("Each line quotes the measurement its next step rests on. `extent` is an extent an existing")
    add("tool derives now, `reader` is a new reader named by the code address that supplies its index")
    add("or its end, `null` is a measured null that moves no byte, and `blocked` is a reader no")
    add("automated run reached, where the census states no index at all.")
    add("")
    add("| citation | rows | bytes | step | instrument | sample measurement | bytes the step would move |")
    add("|---|---|---|---|---|---|---|")
    for reference, found in sorted(big, key=lambda item: -sum(row["bytes"] for row in item[1])):
        spec = DISPOSITIONS[reference]
        add("| `%s` | %d | %d | `%s` | %s | %s | %d |"
            % (reference, len(found), sum(row["bytes"] for row in found), spec["step"],
               spec["instrument"], spec["sample"].replace("|", "/"), spec["moves"]))
    add("")
    steps = collections.Counter(DISPOSITIONS[reference]["step"] for reference, _found in big)
    add("No group takes the `extent` step: no tool in the tree derives an extent for any of the %d"
        % len(big))
    add("groups above. They hold %d `reader` group(s), %d `null` group(s) and %d `blocked` group(s)."
        % (steps["reader"], steps["null"], steps["blocked"]))
    add("")
    add("## The groups under 4 KiB")
    add("")
    add("The %d groups under 4 KiB hold %d rows / %d B and no group states a next step of its own:"
        % (len(small), sum(len(found) for _reference, found in small),
           sum(sum(row["bytes"] for row in found) for _reference, found in small)))
    add("each is a row whose own census line carries its null, and the four classes of the index hold")
    add("them already. %d B of the class is measured and outside any plan."
        % sum(sum(row["bytes"] for row in found) for _reference, found in small))
    add("")
    add("## The plan in byte order")
    add("")
    add("| bytes | step | citation | instrument | riskiest assumption |")
    add("|---|---|---|---|---|")
    plan = [(spec["moves"], reference, spec)
            for reference, _found in big for spec in (DISPOSITIONS[reference],)
            if spec["step"] == "reader"]
    for size, reference, spec in sorted(plan, reverse=True):
        add("| %d | `%s` | `%s` | %s | %s |"
            % (size, spec["step"], reference, spec["instrument"], spec["assumption"]))
    if not plan:
        add("| - | - | - | - | - |")
    add("")
    blocked = sum(sum(row["bytes"] for row in found) for reference, found in big
                  if DISPOSITIONS[reference]["step"] == "blocked")
    add("The plan holds %d B; the other %d B of the class has a measured null (%d B) or a reader no"
        % (sum(size for size, _reference, _spec in plan),
           total_bytes - sum(size for size, _reference, _spec in plan),
           total_bytes - sum(size for size, _reference, _spec in plan) - blocked))
    add("automated run reached (%d B)." % blocked)
    add("")
    add("## Re-run")
    add("")
    add("    python tools\\research\\others_found_triage.py")
    add("    python tools\\research\\others_found_triage.py --check")
    add("")
    assert total_rows and total_bytes
    assert classes[residual_index.OTHERS] == [total_rows, total_bytes]
    return "\n".join(lines) + "\n"


def check(rows=None):
    rows = others() if rows is None else rows
    total_rows = len(rows)
    total_bytes = sum(row["bytes"] for row in rows)
    index_rows, index_bytes = residual_index.totals(residual_index.measure())[residual_index.OTHERS]
    if (total_rows, total_bytes) != (index_rows, index_bytes):
        raise SystemExit("the triage holds %d rows / %d B, not the index's %d / %d"
                         % (total_rows, total_bytes, index_rows, index_bytes))
    big = big_groups(rows)
    references = {reference for reference, _found in big}
    missing = sorted(references - set(DISPOSITIONS))
    if missing:
        raise SystemExit("%d group(s) of 4 KiB or more state no next step: %s"
                         % (len(missing), ", ".join(missing[:6])))
    stale = sorted(set(DISPOSITIONS) - references)
    if stale:
        raise SystemExit("%d next step(s) are for a group not at or above 4 KiB: %s"
                         % (len(stale), ", ".join(stale[:6])))
    for reference, found in big:
        spec = DISPOSITIONS[reference]
        size = sum(row["bytes"] for row in found)
        if spec["step"] not in dict(STEPS):
            raise SystemExit("%s states step %r, which is not one of the four" % (reference,
                                                                                 spec["step"]))
        if not 0 <= spec["moves"] <= size:
            raise SystemExit("%s would move %d B of its %d B" % (reference, spec["moves"], size))
        path = os.path.join(ROOT, spec["sample_doc"])
        with open(path, encoding="utf-8") as handle:
            if spec["sample"] not in handle.read():
                raise SystemExit("%s quotes a measurement %s no longer holds: %r"
                                 % (reference, spec["sample_doc"], spec["sample"]))
        if spec["step"] in ("null", "blocked") and spec["moves"]:
            raise SystemExit("%s is a %s and still states bytes" % (reference, spec["step"]))
        if spec["step"] == "reader" and not spec["assumption"]:
            raise SystemExit("%s states no assumption for its step" % reference)
    kinds = tally(rows, kind_of)
    _referenced, cited, runtime, unreferenced = gate_figures()
    if kinds["code"][1] != cited:
        raise SystemExit("the code groups hold %d B, not the gate's cited %d B"
                         % (kinds["code"][1], cited))
    if kinds["runtime"][1] != runtime:
        raise SystemExit("the runtime group holds %d B, not the gate's runtime-cited %d B"
                         % (kinds["runtime"][1], runtime))
    if kinds["data"][1] > unreferenced:
        raise SystemExit("the data groups hold %d B of the gate's unreferenced %d B"
                         % (kinds["data"][1], unreferenced))
    return total_rows, total_bytes


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    rows = others()
    total_rows, total_bytes = check(rows)
    text = doc_text(rows)
    kinds = tally(rows, kind_of)
    for name, _states in KINDS:
        print("%-8s %4d row(s) %8d B" % (name, kinds[name][0], kinds[name][1]))
    print("others found %d row(s) %d B  groups %d  at or above 4 KiB %d  plan %d B"
          % (total_rows, total_bytes, len(groups(rows)), len(big_groups(rows)),
             sum(DISPOSITIONS[reference]["moves"] for reference, _found in big_groups(rows))))
    if args.check:
        with open(DOC_OUT, encoding="utf-8") as handle:
            if handle.read() != text:
                raise SystemExit("%s is not the table this triage derives"
                                 % os.path.relpath(DOC_OUT, ROOT))
        print("CHECK: the triage matches the index and the gate")
        return 0
    with open(DOC_OUT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("wrote %s (%d B)" % (os.path.relpath(DOC_OUT, ROOT), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
