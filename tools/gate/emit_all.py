from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import encode_cache

ENCODER = os.path.join(ROOT, "tools", "compress", "compress.exe")

STEPS = (
    ("tilebank_gen",
     (os.path.join(ROOT, "tools", "tilebank", "generate_tilebank.py"), "build",
      "--payloads", os.path.join(ROOT, "assets", "tilebank"),
      "--manifest", os.path.join(ROOT, "tools", "tilebank", "tilebank_manifest.csv"),
      "--out", os.path.join(ROOT, "build", "tilebank_0945c0.bin"))),
    ("mapcontainer_gen",
     (os.path.join(ROOT, "tools", "mapcontainer", "generate_mapcontainer.py"), "build",
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--payloads", os.path.join(ROOT, "assets", "mapcontainer"),
      "--records", os.path.join(ROOT, "assets", "maprecords"),
      "--manifest", os.path.join(ROOT, "tools", "mapcontainer", "mapcontainer_manifest.csv"),
      "--out-dir", os.path.join(ROOT, "build", "mapcontainer"))),
    ("spritecontainer_gen",
     (os.path.join(ROOT, "tools", "mapcontainer", "generate_mapcontainer.py"), "build",
      "--block", "sprite",
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--payloads", os.path.join(ROOT, "assets", "spritecontainer"),
      "--manifest", os.path.join(ROOT, "tools", "spritecontainer", "spritecontainer_manifest.csv"),
      "--out-dir", os.path.join(ROOT, "build", "spritecontainer"))),
    ("animframe_gen",
     (os.path.join(ROOT, "tools", "mapcontainer", "animframe.py"), "build",
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--out-dir", os.path.join(ROOT, "build", "animframe"))),
    ("structured_gen",
     (os.path.join(ROOT, "tools", "structured", "generate_structured.py"), "build",
      "--rom", "baserom.gba", "--payloads", os.path.join("assets", "structured"),
      "--out-dir", os.path.join("build", "structured"))),
    ("endromcontainer_gen",
     (os.path.join(ROOT, "tools", "mapcontainer", "generate_mapcontainer.py"), "build",
      "--block", "endrom",
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--payloads", os.path.join(ROOT, "assets", "endrom"),
      "--records", os.path.join(ROOT, "assets", "endromrecords"),
      "--manifest", os.path.join(ROOT, "tools", "mapcontainer", "endromcontainer_manifest.csv"),
      "--out-dir", os.path.join(ROOT, "build", "endrom"))),
    ("spritedefs_gen",
     (os.path.join(ROOT, "tools", "mapcontainer", "generate_mapcontainer.py"), "build",
      "--block", "spritedefs",
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--payloads", os.path.join(ROOT, "assets", "spritedefs"),
      "--records", os.path.join(ROOT, "assets", "spriterecords"),
      "--manifest", os.path.join(ROOT, "tools", "spritecontainer", "spritecontainer_manifest.csv"),
      "--out-dir", os.path.join(ROOT, "build", "spritedefs"))),
    ("assetdir_gen",
     (os.path.join(ROOT, "tools", "mapcontainer", "generate_mapcontainer.py"), "build",
      "--block", "assetdir",
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--payloads", os.path.join(ROOT, "assets", "assetdir"),
      "--records", os.path.join(ROOT, "assets", "assetdirrecords"),
      "--manifest", os.path.join(ROOT, "tools", "mapcontainer", "endromcontainer_manifest.csv"),
      "--out-dir", os.path.join(ROOT, "build", "assetdir"))),
    ("assetdir3_gen",
     (os.path.join(ROOT, "tools", "mapcontainer", "generate_assetdir3.py"), "build",
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--payloads", os.path.join(ROOT, "assets", "assetdir3"),
      "--out-dir", os.path.join(ROOT, "build", "assetdir3"))),
    ("jcalg1_gen",
     (os.path.join(ROOT, "tools", "research", "generate_jcalg1.py"),
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--payloads", os.path.join(ROOT, "assets", "jcalg1"),
      "--out-dir", os.path.join(ROOT, "build", "jcalg1"))),
    ("endromrecords_gen",
     (os.path.join(ROOT, "tools", "assetrecords", "records_table.py"),
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--out", os.path.join(ROOT, "build", "endromrecords.s"))),
    ("musicrecords_gen",
     (os.path.join(ROOT, "tools", "assetrecords", "records_table.py"),
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--layout", os.path.join(ROOT, "tools", "assetrecords", "musicrecords_layout.json"),
      "--out", os.path.join(ROOT, "build", "musicrecords.s"))),
    ("strings_gen",
     (os.path.join(ROOT, "tools", "text", "strings_table.py"),
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--out", os.path.join(ROOT, "build", "strings.cpp"))),
    ("opcode_stream_gen",
     (os.path.join(ROOT, "tools", "research", "opcode_stream.py"), "build",
      "--rom", os.path.join(ROOT, "baserom.gba"),
      "--out-dir", os.path.join(ROOT, "build", "opcode"))),
)


def run(steps, root):
    environment = dict(os.environ)
    environment[encode_cache.STAMP_ENV] = encode_cache.stamp_of(encode_cache.default_cache_dir())
    running = []
    for name, argv in steps:
        handle = tempfile.TemporaryFile(mode="w+", encoding="utf-8", errors="replace")
        child = subprocess.Popen([sys.executable, *argv], cwd=root, env=environment,
                                 stdout=handle, stderr=subprocess.STDOUT)
        running.append((name, child, handle))
    failed = None
    for name, child, handle in running:
        code = child.wait()
        handle.seek(0)
        tail = deque(maxlen=200)
        printed = 0
        for line in handle:
            printed += 1
            sys.stdout.write(line)
            tail.append(line)
        handle.close()
        sys.stdout.write("%s_exit=%d\n" % (name, code))
        if code != 0:
            os.makedirs(os.path.join(root, "build"), exist_ok=True)
            with open(os.path.join(root, "build", "%s_fail.log" % name), "w",
                      encoding="utf-8") as fail:
                fail.write("".join(tail))
            sys.stdout.write("emit_all: %s printed %d line(s), tail in build\\%s_fail.log\n"
                             % (name, printed, name))
        sys.stdout.flush()
        if code != 0 and failed is None:
            failed = name
    if failed is None:
        encode_cache.publish_stamp(encode_cache.default_cache_dir(), ENCODER)
    return 1 if failed else 0


def main():
    return run(STEPS, ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
