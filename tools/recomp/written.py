from __future__ import annotations

import os


def difference(path, text):
    if not os.path.exists(path):
        return "%s does not exist" % path
    with open(path, encoding="ascii", newline="") as handle:
        committed = handle.read()
    if committed == text:
        return None
    for number, (was, now) in enumerate(zip(committed.splitlines(), text.splitlines()), 1):
        if was != now:
            return "%s line %d: %r is not %r" % (path, number, was, now)
    return "%s differs after line %d" % (path, min(len(committed.splitlines()),
                                                   len(text.splitlines())))


def emit(args, text, path, message):
    if args.check:
        found = difference(path, text)
        if found:
            raise SystemExit(found)
        print("CHECK: %s" % message)
        return 0
    if args.write:
        with open(path, "w", encoding="ascii", newline="\n") as handle:
            handle.write(text)
        print("wrote %s (%d B)" % (os.path.basename(path), len(text)))
        return 0
    print("dry run: pass --write or --check")
    return 0
