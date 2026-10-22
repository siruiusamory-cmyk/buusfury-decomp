from tools.research import bios_block_scan as S


def test_lz77_reads_literals_and_a_back_reference():
    stream = bytes([0x10, 4, 0, 0, 0x40, 0x41, 0x00, 0x00])
    assert S.decode(stream, 0, len(stream)) == ("lz77", 8, b"AAAA")


def test_lz77_refuses_a_back_reference_before_the_output_starts():
    stream = bytes([0x10, 4, 0, 0, 0x40, 0x41, 0x0F, 0xFF])
    assert S.decode(stream, 0, len(stream)) is None


def test_lz77_refuses_a_block_that_would_overrun_the_stated_size():
    stream = bytes([0x10, 4, 0, 0, 0xC0, 0x41, 0x42, 0x43])
    assert S.decode(stream, 0, len(stream)) is None


def test_rle_reads_a_run_and_a_literal_group():
    assert S.decode(bytes([0x30, 5, 0, 0, 0x82, 0x5A]), 0, 6) == ("rle", 6, b"ZZZZZ")
    assert S.decode(bytes([0x30, 3, 0, 0, 0x02, 0x58, 0x59, 0x5A]), 0, 8) == (
        "rle", 8, b"XYZ")


def test_rle_refuses_a_run_that_would_overrun_the_stated_size():
    assert S.decode(bytes([0x30, 4, 0, 0, 0x83, 0x5A]), 0, 6) is None


def huff_stream(root, tree, bits):
    body = bytes([0x28, 2, 0, 0, (len(tree) // 2) - 1]) + bytes(tree)
    word = 0
    for i, bit in enumerate(bits):
        word |= bit << (31 - i)
    return body + word.to_bytes(4, "little")


def test_huffman_returns_the_data_byte_at_the_child_address():
    tree = [0xC0, 0x41, 0x42, 0, 0, 0, 0, 0]
    stream = huff_stream(0xC0, tree, [0, 1])
    assert S.decode(stream, 0, len(stream)) == ("huff8", 17, b"AB")


def test_huffman_follows_the_offset_field_and_not_the_next_byte():
    tree = [0xC1, 0xAA, 0xBB, 0x58, 0x59, 0, 0, 0]
    stream = huff_stream(0xC1, tree, [0, 1])
    assert S.decode(stream, 0, len(stream)) == ("huff8", 17, b"XY")


def test_huffman_refuses_a_node_that_walks_out_of_its_tree():
    tree = [0x02, 0, 0, 0, 0, 0, 0, 0]
    stream = huff_stream(0x02, tree, [1] * 32)
    assert S.decode(stream, 0, len(stream)) is None


def test_diff_can_never_fail_so_it_carries_no_evidence():
    stream = bytes([0x82, 5, 0, 0]) + b"hello"
    assert S.decode(stream, 0, len(stream)) == ("diff8", 9, b"hello")
    assert S.reencodes(stream, 0, 9, "diff8") is False


def test_a_block_that_ends_past_the_limit_is_not_a_hit():
    stream = bytes([0x10, 4, 0, 0, 0x00, 0x41, 0x42, 0x43, 0x44])
    assert S.decode(stream, 0, 8) is None
    assert S.decode(stream, 0, 9) == ("lz77", 9, b"ABCD")


def test_scan_only_tests_four_aligned_offsets():
    odd = bytes([0x00]) + bytes([0x10, 4, 0, 0, 0x00, 0x41, 0x42, 0x43, 0x44])
    assert S.scan(odd, [(0, len(odd))]) == []
    aligned = bytes([0, 0, 0, 0]) + bytes([0x10, 4, 0, 0, 0x00, 0x41, 0x42, 0x43, 0x44])
    assert S.scan(aligned, [(0, len(aligned))]) == [
        {"start": 4, "compressed": 9, "decompressed": 4, "format": "lz77", "span": 0}]


def test_scan_never_crosses_a_span_end():
    stream = bytes([0x10, 4, 0, 0, 0x00, 0x41, 0x42, 0x43, 0x44])
    assert S.scan(stream, [(0, 8), (8, 9)]) == []


def test_fill_runs_are_reported_at_or_above_the_minimum():
    image = bytes([0x00] * 300) + bytes([0x11]) * 200
    runs = S.fill_runs(image, [(0, 500)])
    assert runs == [{"start": 0, "length": 300, "value": 0x00}]


def test_the_greedy_encoders_round_trip_through_their_own_decoders():
    payload = b"AAAABBBBCCCCDDDD" * 40
    for kind, encode in (("lz77", S.lz77_encode), ("rle", S.rle_encode)):
        stream = encode(payload)
        got = S.decode(stream, 0, len(stream))
        assert got is not None and got[2] == payload
        assert S.reencodes(stream, 0, got[1], kind) is True
