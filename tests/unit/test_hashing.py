from tools.webfoot.hashing import hash_file


def test_known_hashes_for_123456789(tmp_path):
    source = tmp_path / "known.bin"
    source.write_bytes(b"123456789")

    result = hash_file(source, chunk_size=2)

    assert result.crc32 == "cbf43926"
    assert result.md5 == "25f9e794323b453885f5181f1b624d0b"
    assert result.sha1 == "f7c3bc1d808e04732adf679965ccc34ca7ae3441"
    assert result.sha256 == "15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225"


def test_known_hashes_for_empty_file(tmp_path):
    source = tmp_path / "empty.bin"
    source.write_bytes(b"")

    result = hash_file(source)

    assert result.crc32 == "00000000"
    assert result.md5 == "d41d8cd98f00b204e9800998ecf8427e"
    assert result.sha1 == "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    assert result.sha256 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_chunk_size_must_be_positive(tmp_path):
    source = tmp_path / "data.bin"
    source.write_bytes(b"x")

    try:
        hash_file(source, chunk_size=0)
    except ValueError as exc:
        assert "positive" in str(exc)
    else:
        raise AssertionError("hash_file accepted a zero chunk size")
