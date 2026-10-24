import pytest

from tools import encode_cache
from tools import testkit
from tools.build import generate_jcalg1 as G


def test_encoded_takes_its_bytes_from_the_payload_and_not_from_the_image():
    image = bytes(range(100)) + bytes([0xAA]) * 8 + bytes(range(100, 120))
    payloads = {100: b"made of the payload"}
    compress = lambda data: b"RE-ENCODED"               # noqa: E731
    extents = [(100, 110, "gen_64_6e.bin")]
    with pytest.raises(G.PromoteError):
        G.encoded(image, payloads, compress, extents)
    image = image[:100] + b"RE-ENCODED" + image[110:]
    assert G.encoded(image, payloads, compress, extents) == [(100, 110, "gen_64_6e.bin",
                                                              b"RE-ENCODED")]


def test_encoded_refuses_a_payload_the_compressor_will_not_take():
    with pytest.raises(G.PromoteError):
        G.encoded(b"\x00" * 32, {0: b"x"}, lambda data: None, [(0, 8, "gen_0_8.bin")])


def test_encoded_keeps_the_runs_apart_where_the_source_names_them_apart():
    image = bytearray(64)
    image[0:4], image[4:8], image[16:20] = b"AAAA", b"BBBB", b"CCCC"
    payloads = {0: b"a", 4: b"b", 16: b"c"}
    sizes = {b"a": b"AAAA", b"b": b"BBBB", b"c": b"CCCC"}
    runs = G.encoded(bytes(image), payloads, lambda data: sizes[data],
                     [(0, 4, "gen_0_4.bin"), (4, 8, "gen_4_8.bin"), (16, 20, "gen_10_14.bin")])
    assert runs == [(0, 4, "gen_0_4.bin", b"AAAA"), (4, 8, "gen_4_8.bin", b"BBBB"),
                    (16, 20, "gen_10_14.bin", b"CCCC")]


def test_encoded_refuses_an_extent_the_store_does_not_tile():
    payloads = {0: b"a"}
    with pytest.raises(G.PromoteError):
        G.encoded(b"AAAA\x00\x00\x00\x00", payloads, lambda data: b"AAAA",
                  [(0, 8, "gen_0_8.bin")])


def test_the_jcalg1_store_directory_is_ignored_by_git():
    import subprocess
    done = subprocess.run(["git", "check-ignore", "assets/jcalg1/payloads.store"],
                          cwd=G.ROOT, capture_output=True)
    assert done.returncode == 0, "assets/jcalg1 must stay out of the repository"


def test_the_generator_store_is_not_the_store_the_emitters_are_measured_through(
        tmp_path, monkeypatch):
    testkit.require(G.COMPRESS, "compress.exe is absent, so the encoder store cannot be opened")
    monkeypatch.setenv(encode_cache.CACHE_ENV, str(tmp_path))
    monkeypatch.delenv(encode_cache.STAMP_ENV, raising=False)
    compress, _stats, close = G.open_encode_store(lambda payload: b"\x02" + payload)
    compress(b"one payload")
    close()
    store = encode_cache.default_cache_dir()
    assert encode_cache.stamp_of(store) == ""
    assert not encode_cache.trusted_store(G.COMPRESS, store)


FRAGMENT = ("\tINCBIN  build\\jcalg1\\gen_10.bin\n"
            "\tINCBIN  baserom.gba_0x14_0x20.extracted\n"
            "\tINCBIN  build\\jcalg1\\gen_20.bin\n"
            "\tINCLUDE rawlabeled_28.s\n")


def test_a_generated_run_ends_where_the_next_token_says_it_starts():
    assert G.run_extents([FRAGMENT]) == [(0x10, 0x14, "gen_10.bin"), (0x20, 0x28, "gen_20.bin")]


def test_a_generated_run_whose_name_carries_its_end_needs_no_following_token():
    assert G.run_extents(["\tINCBIN  build\\jcalg1\\gen_3bd290_3bd2f8.bin\n"]) == [
        (0x3BD290, 0x3BD2F8, "gen_3bd290_3bd2f8.bin")]


def test_a_run_whose_name_does_not_end_past_its_start_is_refused():
    with pytest.raises(G.PromoteError):
        G.run_extents(["\tINCBIN  build\\jcalg1\\gen_20_20.bin\n"])


def test_the_extents_are_the_union_of_every_carrier():
    assert G.run_extents(["\tINCBIN  build\\jcalg1\\gen_3bbe70_3bbefc.bin\n",
                          "\tINCBIN  build\\jcalg1\\gen_3bbefc_3bbf54.bin\n"]) == [
        (0x3BBE70, 0x3BBEFC, "gen_3bbe70_3bbefc.bin"),
        (0x3BBEFC, 0x3BBF54, "gen_3bbefc_3bbf54.bin")]


def test_the_containers_come_from_the_runs_the_source_names(monkeypatch):
    hits = {0x10: {"start": 0x10, "compressed": 4, "decompressed": 3, "byte_exact": True},
            0x20: {"start": 0x20, "compressed": 5, "decompressed": 2, "byte_exact": True},
            0x25: {"start": 0x25, "compressed": 3, "decompressed": 4, "byte_exact": True}}
    stored = {0x18: b"abc", 0x28: b"vw", 0x2D: b"wxyz"}
    monkeypatch.setattr(G.B, "jcalg1_container",
                        lambda image, off, limit, compress=None: hits.get(off))
    monkeypatch.setattr(G.jcalg1, "decompress", lambda image, start, limit: (stored[start], 0))
    assert G.source_payloads(bytes(64), [FRAGMENT], lambda data: data) == {
        0x10: b"abc", 0x20: b"vw", 0x25: b"wxyz"}


def test_a_container_that_does_not_re_encode_is_refused(monkeypatch):
    hits = {0x10: {"start": 0x10, "compressed": 2, "decompressed": 3, "byte_exact": False}}
    monkeypatch.setattr(G.B, "jcalg1_container",
                        lambda image, off, limit, compress=None: hits.get(off))
    with pytest.raises(G.PromoteError):
        G.source_payloads(bytes(64), [FRAGMENT], lambda data: data)


def test_a_run_the_containers_do_not_tile_is_refused(monkeypatch):
    hits = {0x10: {"start": 0x10, "compressed": 2, "decompressed": 3, "byte_exact": True}}
    monkeypatch.setattr(G.B, "jcalg1_container",
                        lambda image, off, limit, compress=None: hits.get(off))
    monkeypatch.setattr(G.jcalg1, "decompress", lambda image, start, limit: (b"abc", 0))
    with pytest.raises(G.PromoteError):
        G.source_payloads(bytes(64), [FRAGMENT], lambda data: data)


def test_a_section_token_the_run_reader_does_not_recognise_is_refused():
    with pytest.raises(G.PromoteError):
        G.run_extents(["\tINCBIN  build\\jcalg1\\run_10.bin\n"
                       "\tINCBIN  baserom.gba_0x14_0x20.extracted\n"])


def test_a_source_with_no_generated_run_is_refused_instead_of_stored():
    with pytest.raises(G.PromoteError):
        G.source_payloads(bytes(32), ["\tINCBIN  baserom.gba_0x0_0x20.extracted\n"], lambda d: d)
