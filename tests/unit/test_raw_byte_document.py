"""The SDK reads the raw byte document the application authors. LOG1-RAW-WRITE-BUILD-001.

Three questions live here and nowhere else.

**Is the document read the same way by both readers?** The document shape is the
application's to declare (`tools/dragonbyte/rawbytes.py`), and the shipping
package may not import it (`tools/quality/architecture.py`, rule
`import-direction`), so the SDK's reader is a second spelling of one shape. The
first test writes a document with the application's own writer and asserts the two
readers agree byte for byte, which is what a divergence has to break.

**Does an unreadable document fail closed?** A build that reads an authored raw
write as "this project authors none" emits the canonical bytes and reports
success, which is the defect class this ticket exists to close. Every malformed
shape here therefore raises rather than returning an empty document.

**Is the document a value a caller cannot write through?** A build reads the
document to decide what the emitted image contains, so a frozen document holding a
mutable mapping would let a caller inject a write no authored document holds.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.dragonbyte import rawbytes as app_rawbytes
from tools.webfoot.project import (
    RAW_BYTES_FILE,
    RawByteDocumentError,
    RawByteEdits,
    raw_byte_changes,
    read_raw_bytes,
)

_TWO_WRITES = {
    "0x00040083": "aabb",
    "0x00040010": "0f",
}


def _write(directory: Path, text: str) -> Path:
    path = Path(directory) / RAW_BYTES_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- one shape, two readers ---------------------------------------------------


def test_the_application_writer_round_trips_through_both_readers(tmp_path):
    """The application writes the document; both readers read the same edits."""
    application = app_rawbytes.RawEdits(
        bytes_by_offset={0x40010: b"\x0f", 0x40083: b"\xaa\xbb"}
    )
    app_rawbytes.write_raw_document(tmp_path, application)

    sdk = read_raw_bytes(tmp_path)
    reread = app_rawbytes.read_raw_document(
        Path(tmp_path) / app_rawbytes.RAW_DOCUMENT
    )

    assert sdk.bytes_by_offset == reread.bytes_by_offset == application.bytes_by_offset
    # The path both readers agree on is the same path, so a build cannot be looking
    # at a different file than the application saved.
    assert RAW_BYTES_FILE == app_rawbytes.RAW_DOCUMENT


def test_a_document_without_the_bytes_table_authors_nothing(tmp_path):
    _write(tmp_path, "[something_else]\nx = 1\n")

    assert read_raw_bytes(tmp_path) == RawByteEdits()


def test_a_missing_document_authors_nothing(tmp_path):
    assert read_raw_bytes(tmp_path) == RawByteEdits()


def test_an_empty_bytes_table_is_refused(tmp_path):
    """An empty table claims an intent that does not exist; the writer deletes it."""
    _write(tmp_path, "[bytes]\n")

    with pytest.raises(RawByteDocumentError, match="non-empty table"):
        read_raw_bytes(tmp_path)


def test_a_key_that_is_not_a_file_offset_is_refused(tmp_path):
    _write(tmp_path, '[bytes]\nnot_an_offset = "aa"\n')

    with pytest.raises(RawByteDocumentError, match="not a file offset"):
        read_raw_bytes(tmp_path)


def test_a_value_that_is_not_hex_is_refused(tmp_path):
    _write(tmp_path, '[bytes]\n"0x40010" = "zz"\n')

    with pytest.raises(RawByteDocumentError, match="is not hex"):
        read_raw_bytes(tmp_path)


def test_unparseable_toml_is_refused_rather_than_read_as_empty(tmp_path):
    """The fail-open shape: bad text must not mean 'authors no raw bytes'."""
    _write(tmp_path, '[bytes]\n"0x40010" = \n')

    with pytest.raises(RawByteDocumentError, match="invalid TOML"):
        read_raw_bytes(tmp_path)


# --- what the document mints --------------------------------------------------


def _document(tmp_path, table: str) -> RawByteEdits:
    _write(tmp_path, "[bytes]\n" + table)
    return read_raw_bytes(tmp_path)


def test_a_change_names_the_image_address_owner_and_reads_the_base_bytes(tmp_path):
    image = bytearray(0x1000)
    image[0x20:0x22] = b"\x11\x22"
    edits = _document(tmp_path, '"0x00000020" = "aabb"\n')

    (change,) = raw_byte_changes(edits, bytes(image))

    assert change.offset == 0x20
    assert change.old == b"\x11\x22"
    assert change.new == b"\xaa\xbb"
    assert change.owner == "raw:0x08000020"


def test_a_write_equal_to_the_base_mints_no_change(tmp_path):
    """An authored write that changes nothing is not an edit and is not reported."""
    image = bytearray(0x1000)
    image[0x20:0x21] = b"\x11"
    edits = _document(tmp_path, '"0x00000020" = "11"\n')

    assert raw_byte_changes(edits, bytes(image)) == []


@pytest.mark.parametrize(
    ("offset", "value"),
    (("0x00000FFF", "aabb"), ("0x00002000", "aa")),
)
def test_a_write_outside_the_image_is_refused(tmp_path, offset, value):
    edits = _document(tmp_path, f'"{offset}" = "{value}"\n')

    with pytest.raises(RawByteDocumentError, match="inside the 4096-byte canonical"):
        raw_byte_changes(edits, bytes(0x1000))


# --- the document is a value, not a handle ------------------------------------


def test_a_caller_cannot_write_through_the_document(tmp_path):
    """A frozen document that hands out a writable mapping is not frozen.

    An injected entry is a raw write no authored document holds, and the build
    would apply it: the document is the only thing that says what to write.
    """
    edits = _document(tmp_path, '"0x00000020" = "aabb"\n')

    with pytest.raises(TypeError):
        edits.bytes_by_offset[0x40] = b"\x99"  # type: ignore[index]

    assert edits.bytes_by_offset == {0x20: b"\xaa\xbb"}
    assert raw_byte_changes(edits, bytes(0x1000))[0].offset == 0x20


def test_the_document_holds_a_copy_of_the_mapping_it_was_built_from():
    """The read-only view wraps a copy, so the caller's own mapping cannot reach it."""
    source = {0x20: b"\xaa"}
    edits = RawByteEdits(source)

    source[0x20] = b"\x11"

    assert edits.bytes_by_offset == {0x20: b"\xaa"}
