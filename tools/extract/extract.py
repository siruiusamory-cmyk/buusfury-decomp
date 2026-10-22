import argparse
import hashlib
import os

ROM_SIZE = 0x800000
SITES = (
    ("bg.pal", 0x05632C, 0x05652C),
    ("sprite.pal", 0x05652C, 0x05672C),
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", required=True)
    ap.add_argument("--sha1-file", required=True)
    ap.add_argument("--build", required=True)
    a = ap.parse_args()

    rom = open(a.rom, "rb").read()
    if len(rom) != ROM_SIZE:
        raise SystemExit("%s is %d bytes, not %d" % (a.rom, len(rom), ROM_SIZE))
    want = open(a.sha1_file).read().strip().lower()
    got = hashlib.sha1(rom).hexdigest()
    if got != want:
        raise SystemExit("%s sha1 %s is not the declared %s" % (a.rom, got, want))

    os.makedirs(a.build, exist_ok=True)
    for name, start, end in SITES:
        with open(os.path.join(a.build, name), "wb") as handle:
            handle.write(rom[start:end])
        print("%-34s %6d B  file 0x%06X..0x%06X" % (name, end - start, start, end))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
