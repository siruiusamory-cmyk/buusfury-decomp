import importlib
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, os.path.join(ROOT, "tools", "gate"), os.path.join(ROOT, "tools"),
              os.path.join(ROOT, "tools", "mapcontainer")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

CHECKS = ("audiodir", "code_band", "endrom_index_census", "endrom_readers", "pointer_rows",
          "rawlabeled", "raw_remainder", "region_readers", "residual_causes", "residual_index",
          "row_readers", "runtime_read_results", "transcribed_data", "unknown_census")


@pytest.mark.parametrize("name", CHECKS)
def test_the_tracked_output_check_passes(name):
    assert importlib.import_module(name).main(["--check"]) == 0
