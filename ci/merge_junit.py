"""Merge the per-shard JUnit reports into one ``report.xml``.

The workflow runs the portable suite as ten parallel jobs, so a run leaves ten
JUnit documents. Merging them into one keeps the totals and the skip census
comparable with the single-process record that ``scripts/local-ci.ps1`` writes:
that gate reads ``testsuites.testsuite`` and sums ``tests``, ``failures``,
``errors`` and ``skipped``, which is the shape preserved here.

Standard library only, and :func:`merge_texts` is the whole implementation, so a
test drives the merge on synthetic documents instead of through the CLI.

Usage::

    python ci/merge_junit.py --output report.xml shards/shard-0/report.xml ...
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

#: The count attributes summed here and by the repository's own JUnit reader.
COUNT_ATTRIBUTES = ("tests", "failures", "errors", "skipped")


class DuplicateNodeError(ValueError):
    """Two input documents report the same node."""


def merge_texts(texts: Sequence[str]) -> str:
    """One ``<testsuites>`` document carrying every input suite, in input order.

    Each input's ``<testsuite>`` elements are the merged root's children, each
    preserved whole with its attributes. Raises :class:`DuplicateNodeError` when
    two inputs report the same ``(classname, name)``, and ``AssertionError`` when
    the document written back out does not carry the totals the inputs did.
    """
    documents = [ElementTree.fromstring(text) for text in texts]
    merged = ElementTree.Element("testsuites")
    seen: dict[tuple[str, str], int] = {}
    for position, document in enumerate(documents):
        for suite in _suites(document):
            merged.append(suite)
            for case in suite.iter("testcase"):
                node = (case.get("classname", ""), case.get("name", ""))
                if seen.setdefault(node, position) != position:
                    raise DuplicateNodeError(
                        f"{node[0]}::{node[1]} appears in two of the input reports"
                    )
    expected = {
        attribute: sum(_sum_of(_suites(document), attribute) for document in documents)
        for attribute in COUNT_ATTRIBUTES
    }
    for attribute, total in expected.items():
        merged.set(attribute, str(total))
    written = ElementTree.tostring(merged, encoding="unicode")
    actual = totals_of(written)
    if actual != expected:
        raise AssertionError(
            f"the merged report says {actual}, its inputs said {expected}"
        )
    return written


def totals_of(text: str) -> dict[str, int]:
    """The four summed counts a reader compares one run by."""
    suites = _suites(ElementTree.fromstring(text))
    return {attribute: _sum_of(suites, attribute) for attribute in COUNT_ATTRIBUTES}


def _suites(document: ElementTree.Element) -> list[ElementTree.Element]:
    """The ``testsuite`` elements of one document, in document order."""
    if document.tag == "testsuite":
        return [document]
    return [child for child in document if child.tag == "testsuite"]


def _sum_of(suites: Iterable[ElementTree.Element], attribute: str) -> int:
    total = 0
    for suite in suites:
        raw = suite.get(attribute)
        if raw is None:
            continue
        try:
            total += int(raw)
        except ValueError:
            raise ValueError(
                f"testsuite {suite.get('name', '?')!r} carries "
                f"{attribute}={raw!r}, which is not a count"
            ) from None
    return total


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("inputs", nargs="+", type=Path)
    arguments = parser.parse_args(argv)

    try:
        merged = merge_texts(
            [path.read_text(encoding="utf-8") for path in arguments.inputs]
        )
    except (ElementTree.ParseError, ValueError, AssertionError) as error:
        print(f"merge_junit: FAIL - {error}", file=sys.stderr)
        return 1

    arguments.output.write_text(merged, encoding="utf-8")
    totals = totals_of(merged)
    print(
        "tests={tests} failures={failures} errors={errors} skipped={skipped}".format(
            **totals
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
