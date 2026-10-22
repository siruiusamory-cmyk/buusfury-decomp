import argparse
import hashlib
import os
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "webfoot"))

import webfoot_lz

ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
COMPRESS = os.path.join(ROOT, "tools", "compress", "compress.exe")
PAYLOADS = os.path.join(ROOT, "assets", "generated")

IMAGES = (
    ("asset_intro", 0x055620, 240, 160, True, None, 0x055620, 0x0561C4),
    ("asset_splash", 0x3BE3D4, 240, 160, True, 20516, 0x3BE3D4, 0x3C33F8),
    ("asset_dialogbox", 0x071758, 160, 64, True, 788, 0x071758, 0x071A6C),
    ("asset_dialogbox_small", 0x071A6C, 160, 64, True, None, 0x071A6C, 0x071C90),
    ("corner_top_left", 0x05622C, 8, 8, False, None, 0x05622C, 0x05626C),
    ("corner_top_right", 0x05626C, 8, 8, False, None, 0x05626C, 0x0562AC),
    ("corner_bottom_left", 0x0562AC, 8, 8, False, None, 0x0562AC, 0x0562EC),
    ("corner_bottom_right", 0x0562EC, 8, 8, False, None, 0x0562EC, 0x05632C),
)


def read_rom(path):
    rom = open(path, "rb").read()
    digest = hashlib.sha256(rom).hexdigest()
    if digest != ROM_SHA256:
        raise SystemExit("%s sha256 %s is not %s" % (path, digest, ROM_SHA256))
    return rom


def grit():
    for candidate in (os.environ.get("GRIT"), shutil.which("grit"),
                      os.path.join(os.environ.get("DEVKITPRO", "C:/devkitPro"),
                                   "tools", "bin", "grit.exe")):
        if candidate and os.path.exists(candidate):
            return candidate
    raise SystemExit("grit not found: set GRIT or DEVKITPRO")


def bmp(width, height, pixels):
    stride = (width + 3) // 4 * 4
    body = b"".join(pixels[y * width:(y + 1) * width] + b"\0" * (stride - width)
                    for y in range(height - 1, -1, -1))
    offset = 54 + 1024
    header = struct.pack("<2sIHHI", b"BM", offset + len(body), 0, 0, offset)
    info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, 8, 0, len(body),
                       0, 0, 256, 256)
    palette = b"".join(bytes((index, index, index, 0)) for index in range(256))
    return header + info + palette + body


def pixels(rom, image):
    _name, offset, width, height, container, _hint, _start, _end = image
    if container:
        decoded = webfoot_lz.unpack(rom, offset, maximum_output=width * height)
        if decoded.declared_size != width * height:
            raise SystemExit("%s declares %d bytes, not %d"
                             % (_name, decoded.declared_size, width * height))
        return decoded.data
    return rom[offset:offset + width * height]


def extract(rom, payloads):
    os.makedirs(payloads, exist_ok=True)
    for image in IMAGES:
        name, _offset, width, height, _container, _hint, _start, _end = image
        path = os.path.join(payloads, name + ".bmp")
        body = bmp(width, height, pixels(rom, image))
        open(path, "wb").write(body)
        print("%-22s %6d B  %dx%d" % (os.path.relpath(path, ROOT), len(body),
                                      width, height))


def encode(bmp_path, build, name, container, hint):
    tool = grit()
    img = os.path.join(build, name + ".img.bin")
    proc = subprocess.run([tool, bmp_path, "-gB8", "-p!", "-ftb", "-gb", "-o",
                           os.path.join(build, name)], capture_output=True)
    if proc.returncode != 0 or not os.path.exists(img):
        raise SystemExit("grit %s exit %d: %s" % (name, proc.returncode,
                                                  proc.stderr.decode("utf-8", "replace")))
    out = img
    if container:
        out = os.path.join(build, name + ".compressed")
        args = [COMPRESS, img, out] + ([str(hint)] if hint else [])
        proc = subprocess.run(args, capture_output=True)
        if proc.returncode != 0 or not os.path.exists(out):
            raise SystemExit("compress %s exit %d: %s" % (name, proc.returncode,
                                                          proc.stderr.decode("utf-8", "replace")))
    return out


def build(rom, payloads, build_dir):
    os.makedirs(build_dir, exist_ok=True)
    for image in IMAGES:
        name, _offset, width, height, container, hint, start, end = image
        want = rom[start:end]
        got = open(encode(os.path.join(payloads, name + ".bmp"), build_dir, name,
                          container, hint), "rb").read()
        if got != want:
            raise SystemExit("%s encodes %d bytes, not the %d retail bytes at %#x"
                             % (name, len(got), len(want), start))
        print("%-22s %6d B  file 0x%06X..0x%06X  %s" % (
            name, len(got), start, end, "grit+compress" if container else "grit"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("extract", "build"))
    parser.add_argument("--rom", required=True)
    parser.add_argument("--payloads", default=PAYLOADS)
    parser.add_argument("--build", default=os.path.join(ROOT, "build"))
    args = parser.parse_args()
    if not os.path.exists(COMPRESS):
        raise SystemExit("no compressor at %s" % COMPRESS)
    rom = read_rom(args.rom)
    if args.mode == "extract":
        extract(rom, args.payloads)
    else:
        build(rom, args.payloads, args.build)
    return 0


if __name__ == "__main__":
    sys.exit(main())
