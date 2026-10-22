import argparse
import os
import shutil
import tempfile
import time

SAMPLE = os.path.join(tempfile.gettempdir(), "evict-sample")


def touch_memory(gib):
    blocks, pattern = [], bytes(range(256)) * 4096
    try:
        for _ in range(gib * 1024):
            blocks.append(bytearray(pattern))
    except MemoryError:
        pass
    held = len(blocks)
    del blocks
    return held


def copy_sample(source):
    shutil.rmtree(SAMPLE, ignore_errors=True)
    os.makedirs(SAMPLE)
    for name in os.listdir(source):
        shutil.copyfile(os.path.join(source, name), os.path.join(SAMPLE, name))
    return len(os.listdir(SAMPLE))


def read_sample():
    started = time.perf_counter()
    total = 0
    for name in os.listdir(SAMPLE):
        with open(os.path.join(SAMPLE, name), "rb") as handle:
            total += len(handle.read())
    return total, time.perf_counter() - started


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gib", type=int, default=12, help="memory to demand-touch, in GiB")
    ap.add_argument("--check", metavar="DIR", help="sample population to prove the eviction on")
    a = ap.parse_args()

    if a.check:
        files = copy_sample(a.check)
        read_sample()
        size, warm = read_sample()
        held = touch_memory(a.gib)
        cold = read_sample()[1]
        print("sample %d files %d B  warm %.3fs  cold %.3fs  ratio %.2fx  held %d MiB"
              % (files, size, warm, cold, cold / warm if warm else 0.0, held))
        if cold <= warm:
            print("REFUSE the eviction did nothing: the sample did not slow down")
            return 1
        return 0

    print("held %d MiB" % touch_memory(a.gib))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
