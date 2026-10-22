from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import check_links


def write(root, name, text):
    path = os.path.join(root, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def test_a_resolving_link_and_a_labelled_hash_are_clean(tmp_path):
    root = str(tmp_path)
    write(root, "docs/a.md", "# a\n")
    write(root, "README.md", "[a](docs/a.md) sha256 `%s`\n" % ("a" * 64))
    assert check_links.findings(root) == []


def test_a_broken_relative_link_is_a_finding(tmp_path):
    root = str(tmp_path)
    write(root, "README.md", "[a](docs/missing.md)\n")
    found = check_links.findings(root)
    assert any("missing.md" in item for item in found), found


def test_a_case_mismatched_link_is_a_finding(tmp_path):
    root = str(tmp_path)
    write(root, "docs/NAMING.md", "# n\n")
    write(root, "README.md", "[n](docs/naming.md)\n")
    found = check_links.findings(root)
    assert any("naming.md" in item for item in found), found


def test_a_nested_link_resolves_from_the_file_that_holds_it(tmp_path):
    root = str(tmp_path)
    write(root, "docs/DETAILS.md", "# d\n")
    write(root, "docs/README.md", "[d](DETAILS.md)\n")
    assert check_links.findings(root) == []


def test_a_nested_link_taken_from_the_root_is_a_finding(tmp_path):
    root = str(tmp_path)
    write(root, "docs/DETAILS.md", "# d\n")
    write(root, "docs/README.md", "[d](docs/DETAILS.md)\n")
    found = check_links.findings(root)
    assert any("docs/DETAILS.md" in item for item in found), found


def test_a_root_relative_link_resolves_from_the_repository_root(tmp_path):
    root = str(tmp_path)
    write(root, "README.md", "# r\n")
    write(root, "docs/README.md", "[r](/README.md)\n")
    assert check_links.findings(root) == []


def test_a_commit_citation_is_a_finding(tmp_path):
    root = str(tmp_path)
    write(root, "docs/b.md", "merged at master `1234abc` for the census\n")
    found = check_links.findings(root)
    assert any("1234abc" in item for item in found), found


def test_a_citation_after_another_keyword_is_a_finding(tmp_path):
    root = str(tmp_path)
    write(root, "docs/c.md", "The frozen `1234abc` tree was measured\n")
    found = check_links.findings(root)
    assert any("1234abc" in item for item in found), found
