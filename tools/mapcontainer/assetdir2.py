from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from assetdirectory import Spec, install  # noqa: E402

SPEC = Spec(directory="asset_directory_79", block="asset_directory_79_block", base=0x36D18C, count=79,
            block_start=0x3195A8, block_end=0x36D18A, low_words={0: 22, 1: 52, 3: 5},
            units={16000: 35, 11025: 6, 16053: 5}, unit_count=29, length_range=(123, 10046),
            tied=True)
install(globals(), SPEC)

if __name__ == "__main__":
    image = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gba", "rb").read()
    print("%s measure %s" % (DIRECTORY, assert_contract(image)))
    print("%s verify  round trip %s" % (DIRECTORY, round_trip(image)))
