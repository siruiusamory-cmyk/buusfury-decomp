from __future__ import annotations

import contextlib
import io
import os
import re
import sys
import tempfile
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import emit_all
import encode_cache


def step(name, body, *args):
    return (name, ("-c", textwrap.dedent(body), *args))


def in_scratch(call):
    root = tempfile.mkdtemp(prefix="emit-all-test-")
    previous = os.environ.get(encode_cache.CACHE_ENV)
    os.environ[encode_cache.CACHE_ENV] = os.path.join(root, "encode-cache")
    try:
        return call(root)
    finally:
        if previous is None:
            os.environ.pop(encode_cache.CACHE_ENV, None)
        else:
            os.environ[encode_cache.CACHE_ENV] = previous


def captured(steps, root):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = emit_all.run(steps, root)
    return code, out.getvalue()


def with_encoder(root):
    cache = os.environ[encode_cache.CACHE_ENV]
    os.makedirs(cache)
    with open(os.path.join(cache, encode_cache.EXE_STAMP), "w") as handle:
        handle.write("a stamp\n")
    encoder = os.path.join(root, "encoder.exe")
    with open(encoder, "wb") as handle:
        handle.write(b"the encoder")
    previous = emit_all.ENCODER
    emit_all.ENCODER = encoder
    return cache, encoder, previous


def test_the_batch_overlaps_and_prints_each_block_at_its_turn():

    def check(root):
        slow = step("slow_gen", """
            import os, sys, time
            open(os.path.join(sys.argv[1], "slow-start"), "w").write("")
            time.sleep(1.2)
            print("fast started while slow ran"
                  if os.path.exists(os.path.join(sys.argv[1], "fast-start"))
                  else "fast started after slow ended")
        """, root)
        fast = step("fast_gen", """
            import os, sys
            open(os.path.join(sys.argv[1], "fast-start"), "w").write("")
            print("fast block")
        """, root)
        return captured((slow, fast), root)

    code, printed = in_scratch(check)
    assert code == 0
    assert printed.splitlines() == ["fast started while slow ran", "slow_gen_exit=0",
                                   "fast block", "fast_gen_exit=0"]


def test_a_failing_step_reports_its_own_code_and_the_batch_fails():
    def check(root):
        assert root
        return captured((step("good_gen", "print('block')"),
                         step("bad_gen", "raise SystemExit(3)"),
                         step("later_gen", "print('later')")), root)

    code, printed = in_scratch(check)
    assert code == 1
    assert printed.splitlines() == ["block", "good_gen_exit=0", "bad_gen_exit=3",
                                   "emit_all: bad_gen printed 0 line(s), tail in "
                                   "build\\bad_gen_fail.log",
                                   "later", "later_gen_exit=0"]


def test_the_batch_reads_the_stamp_once_and_publishes_it_once_itself():

    def check(root):
        cache, encoder, previous = with_encoder(root)
        try:
            code, printed = captured(
                (step("stamp_gen", "import os; print(os.environ.get('%s', 'MISSING'))"
                      % encode_cache.STAMP_ENV),), root)
        finally:
            emit_all.ENCODER = previous
        return code, printed, cache, encoder

    code, printed, cache, encoder = in_scratch(check)
    assert code == 0
    assert printed.splitlines() == ["a stamp", "stamp_gen_exit=0"]
    assert encode_cache.stamp_of(cache) == encode_cache.digest_file(encoder)


def test_a_failed_batch_leaves_the_store_stamp_to_the_next_pass():

    def check(root):
        cache, encoder, previous = with_encoder(root)
        try:
            code, printed = captured((step("good_gen", "print('block')"),
                                      step("bad_gen", "raise SystemExit(3)")), root)
        finally:
            emit_all.ENCODER = previous
        return code, printed, encode_cache.stamp_of(cache)

    code, printed, stamp = in_scratch(check)
    assert code == 1
    assert printed.splitlines() == ["block", "good_gen_exit=0", "bad_gen_exit=3",
                                   "emit_all: bad_gen printed 0 line(s), tail in "
                                   "build\\bad_gen_fail.log"]
    assert stamp == "a stamp"


def test_a_failing_step_leaves_its_captured_output_in_a_fail_log():

    def check(root):
        code, printed = captured(
            (step("noisy_gen", "print('first line')\nprint('second line')\nraise SystemExit(2)"),
             step("silent_gen", "raise SystemExit(4)")), root)
        return code, printed, root

    code, printed, root = in_scratch(check)
    assert code == 1
    with open(os.path.join(root, "build", "noisy_gen_fail.log"), encoding="utf-8") as handle:
        noisy = handle.read()
    with open(os.path.join(root, "build", "silent_gen_fail.log"), encoding="utf-8") as handle:
        silent = handle.read()
    assert noisy.splitlines() == ["first line", "second line"]
    assert silent == ""
    markers = [line for line in printed.splitlines() if line.startswith("emit_all: ")]
    assert markers == ["emit_all: noisy_gen printed 2 line(s), tail in build\\noisy_gen_fail.log",
                       "emit_all: silent_gen printed 0 line(s), tail in build\\silent_gen_fail.log"]
    assert not any(re.search(r"(\w+)_exit=(\d+)", line) for line in markers)


def test_a_verbose_failing_step_keeps_exactly_the_last_two_hundred_lines():

    class NoReadlines:

        def __init__(self, handle):
            self._handle = handle

        def __getattr__(self, name):
            return getattr(self._handle, name)

        def __iter__(self):
            return iter(self._handle)

        def readlines(self, *args):
            raise AssertionError("the whole child log was read into memory")

    def check(root):
        real = emit_all.tempfile.TemporaryFile
        emit_all.tempfile.TemporaryFile = lambda *a, **k: NoReadlines(real(*a, **k))
        try:
            code, printed = captured(
                (step("verbose_gen", """
                    for number in range(1, 251):
                        print('line %d' % number)
                    raise SystemExit(2)
                    """),), root)
        finally:
            emit_all.tempfile.TemporaryFile = real
        return code, printed, root

    code, printed, root = in_scratch(check)
    assert code == 1
    with open(os.path.join(root, "build", "verbose_gen_fail.log"), encoding="utf-8") as handle:
        kept = handle.read().splitlines()
    assert kept == ["line %d" % number for number in range(51, 251)]
    assert ("emit_all: verbose_gen printed 250 line(s), tail in build\\verbose_gen_fail.log"
            in printed.splitlines())


if __name__ == "__main__":
    test_the_batch_overlaps_and_prints_each_block_at_its_turn()
    test_a_failing_step_reports_its_own_code_and_the_batch_fails()
    test_the_batch_reads_the_stamp_once_and_publishes_it_once_itself()
    test_a_failed_batch_leaves_the_store_stamp_to_the_next_pass()
    test_a_failing_step_leaves_its_captured_output_in_a_fail_log()
    test_a_verbose_failing_step_keeps_exactly_the_last_two_hundred_lines()
    print("PASS test_emit_all")
