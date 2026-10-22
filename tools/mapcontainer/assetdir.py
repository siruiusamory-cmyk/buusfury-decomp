from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from assetdirectory import Spec, install  # noqa: E402

SPEC = Spec(directory="asset_directory_64", block="asset_directory_block", base=0x3192A8, count=64,
            block_start=0x2B9BB0, block_end=0x3192A5, low_words={0: 54, 1: 10},
            units={8000: 25, 16000: 5}, tied=True)
install(globals(), SPEC)

if __name__ == "__main__":
    image = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gba", "rb").read()
    print("%s measure %s" % (DIRECTORY, assert_contract(image)))
    print("%s verify  round trip %s" % (DIRECTORY, round_trip(image)))
