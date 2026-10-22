import re
import subprocess
import time

import gate

BOUNDARY = re.compile(r"^(=== .* ===|[A-Za-z_]+_exit=\d+|DONE)$")


def main():
    gate.purge_outputs()
    started = time.perf_counter()
    previous = started
    process = subprocess.Popen(["cmd.exe", "/c", gate.BUILD], cwd=gate.ROOT,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, bufsize=1)
    for line in process.stdout:
        line = line.rstrip("\r\n")
        now = time.perf_counter()
        if BOUNDARY.match(line):
            print("%7.2fs %6.2fs  %s" % (now - started, now - previous, line))
            previous = now
        else:
            print("                  %s" % line)
    code = process.wait()
    print("total %.2fs exit=%d" % (time.perf_counter() - started, code))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
