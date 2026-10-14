"""Deterministic readability and residue advisories over the public source tree.

Run it as ``python -m tools.quality.readability``. It reports observations and
never a score: a single aggregate number invites editing the number rather than
the file. Two layers instead:

* **Hard findings** are residue that must not ship in a public repository: an
  absolute path from one machine, vocabulary pasted out of a development
  process, an implementation left behind a comment marker.
* **Advisories** are a reading list. They never change the exit code, and the
  summary says so on its last line.

Property that matters more than any single signal: this module reads text and
nothing else. It never imports, compiles or executes the code it looks at, so a
scan cannot change the tree it is measuring or run code from an untrusted
branch.

Two further properties are load-bearing:

* **Determinism.** Findings are sorted by ``(path, line, signal)``, the JSON
  document is emitted with sorted keys and no clock, and a file's content is the
  only input. Two runs over unchanged input are byte-identical.
* **No silent skipping.** Every scanned file comes from ``git ls-files``, and
  the paths this module deliberately never scans are listed in
  :data:`SELF_EXCLUSION` with a reason each. A detector that quietly stops
  looking at a file is worse than no detector, so the tests pin the size of that
  list and the number of files a real scan reaches.
"""

from __future__ import annotations

import argparse
import ast
import base64
import fnmatch
import json
import re
import shutil
import statistics
import subprocess
import sys
from collections.abc import Collection, Iterable, Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PurePosixPath

SCHEMA_VERSION = 1

#: Repository root, resolved from this file rather than the working directory so
#: that a scan of the installed package measures the same tree as a scan run
#: from the repository root.
REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_EXCEPTIONS_PATH = "config/readability_exceptions.json"

#: Matched text is truncated to this many characters in reports. Long enough to
#: recognise the line, short enough that one line cannot dominate the output.
EXCERPT_LIMIT = 120


# --- scope -----------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ScanRoot:
    """One directory the scan covers, with the reason it is in or out.

    ``path`` is repository-relative; ``""`` means the repository root itself and
    is only used with ``direct_files_only``.
    """

    path: str
    reason: str
    direct_files_only: bool = False


#: Where the scan looks. Source files are the product and its instruments, so
#: every tree that ships a source file is named here explicitly; a tree that is
#: omitted from both this list and OUT_OF_SCOPE is a bug, not a decision.
SCAN_ROOTS: tuple[ScanRoot, ...] = (
    ScanRoot(
        "tools",
        "The shipping toolkit, the research tooling and the runtime probes: the "
        "product and the instruments that measure it.",
    ),
    ScanRoot(
        "tests",
        "Public source as well. A test states expected behaviour and is read by "
        "contributors, so it carries the same residue risk as the code.",
    ),
    ScanRoot(
        "scripts",
        "Contributor and CI entry points, run from a checkout on any machine.",
    ),
    ScanRoot(
        "src",
        "Source of the public status site that ships alongside the toolkit.",
    ),
    ScanRoot(
        "public",
        "Static assets for the status site. No source file today; kept so one is "
        "covered on the day it appears.",
    ),
    ScanRoot(
        "",
        "Repository-root build and deploy configuration that is source "
        "(astro.config.mjs). The language filter keeps package manifests, "
        "lockfiles and the shell shim out.",
        direct_files_only=True,
    ),
)

#: Trees deliberately outside the scan, each for the stated reason. Written down
#: so that "not scanned" is a decision that can be reviewed, not an omission.
OUT_OF_SCOPE: tuple[ScanRoot, ...] = (
    ScanRoot("docs", "Narrative, evidence records and tickets: prose about the project."),
    ScanRoot("config", "Data read by the toolkit at run time, not executable source."),
    ScanRoot("build", "Generated build output; ignored by git and never shipped."),
    ScanRoot("dist", "Packaged output, generated."),
    ScanRoot("node_modules", "Third-party dependencies, not this project's source."),
    ScanRoot(".venv", "Local virtual environment."),
    ScanRoot(".git", "Repository internals."),
    ScanRoot("extern", "Checked-out upstream repositories: other projects' source."),
    ScanRoot("roms", "Commercial ROM images and saves; never committed."),
    ScanRoot("extracted", "Extracted game data; ignored by git."),
)

#: Directory names that are never entered even if a tracked path names them.
SKIP_DIRECTORY_NAMES: frozenset[str] = frozenset(
    {
        "build",
        "dist",
        "node_modules",
        ".venv",
        ".git",
        "__pycache__",
        ".astro",
        ".pytest_cache",
        ".hypothesis",
        "extern",
        "roms",
        "extracted",
        "dump",
        "dumps",
        "stock",
        "exports",
        "scratchpad",
    }
)


@dataclass(frozen=True, slots=True)
class Exclusion:
    """A path the scan never reads, and why it must be allowed not to."""

    path: str
    reason: str


#: Files whose own text cannot be scanned. Exactly the files that must name what
#: the scan forbids; the tests pin this length so a later edit cannot widen the
#: blind spot without a failing test.
SELF_EXCLUSION: tuple[Exclusion, ...] = (
    Exclusion(
        "tools/quality/readability.py",
        "Carries the encoded term table and the matcher built from it. A detector "
        "cannot grade its own vocabulary.",
    ),
    Exclusion(
        "tests/unit/test_readability.py",
        "Its positive controls embed the exact shapes the scan forbids, so "
        "including it would make every new control a whole-tree failure.",
    ),
)


# --- languages -------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Language:
    """Comment and string syntax, and how block structure is measured.

    ``indent_nesting`` selects the depth model: languages whose blocks are
    delimited by keywords and indentation are measured by indentation (with
    bracket continuations skipped), and brace languages are measured by brace
    depth. Counting leading spaces in a brace language would measure formatting
    rather than structure, which is why the two models exist.
    """

    name: str
    line_comment: str
    block_comment: tuple[str, str] | None
    string_delimiters: tuple[str, ...]
    indent_nesting: bool


PYTHON = Language("python", "#", None, ('"""', "'''", '"', "'"), True)
TYPESCRIPT = Language("typescript", "//", ("/*", "*/"), ('"', "'", "`"), False)
POWERSHELL = Language("powershell", "#", ("<#", "#>"), ('"', "'"), False)
LUA = Language("lua", "--", ("--[[", "]]"), ('"', "'"), True)

LANGUAGE_BY_SUFFIX: dict[str, Language] = {
    ".py": PYTHON,
    ".ts": TYPESCRIPT,
    ".tsx": TYPESCRIPT,
    ".js": TYPESCRIPT,
    ".mjs": TYPESCRIPT,
    ".cjs": TYPESCRIPT,
    ".ps1": POWERSHELL,
    ".psm1": POWERSHELL,
    ".lua": LUA,
}


def language_for(rel_path: str) -> Language | None:
    """The scanner's view of *rel_path*, or None when the suffix is not covered."""
    return LANGUAGE_BY_SUFFIX.get(PurePosixPath(rel_path).suffix.lower())


# --- signals ---------------------------------------------------------------

HARD = "hard"
ADVISORY = "advisory"


@dataclass(frozen=True, slots=True)
class Signal:
    id: str
    severity: str
    description: str


#: Declaration order is the report order for the human summary. The first six
#: carry the ticket's four hard classes (the proprietary class is split into its
#: three shapes so an exception can name one of them precisely); everything
#: after them is a reading list.
SIGNALS: tuple[Signal, ...] = (
    Signal(
        "process_narration",
        HARD,
        "Vocabulary from a development process rather than from the program.",
    ),
    Signal(
        "commented_out_code",
        HARD,
        "A run of implementation left behind a comment marker.",
    ),
    Signal(
        "debug_residue",
        HARD,
        "A marker naming a debug aid, a local path, or its own removal.",
    ),
    Signal(
        "proprietary_user_path",
        HARD,
        "An absolute path into one machine's user profile.",
    ),
    Signal(
        "proprietary_rom_filename",
        HARD,
        "A ROM, save or state filename naming a commercial game.",
    ),
    Signal(
        "credential_shaped",
        HARD,
        "A quoted value shaped like a credential.",
    ),
    Signal(
        "comment_share",
        HARD,
        "Comment and docstring lines above the ceiling the conventions set.",
    ),
    Signal(
        "oversized_comment_block",
        ADVISORY,
        "One comment run longer than the documented ceiling.",
    ),
    Signal(
        "excessive_prose",
        ADVISORY,
        "A file whose lines are mostly comment.",
    ),
    Signal(
        "todo_debt",
        ADVISORY,
        "An unresolved TODO or FIXME that is not already a hard finding.",
    ),
    Signal(
        "placeholder_identifier",
        ADVISORY,
        "A generated, placeholder or decompiler-shaped name.",
    ),
    Signal(
        "deep_nesting",
        ADVISORY,
        "Structure deeper than the documented ceiling.",
    ),
    Signal(
        "giant_function",
        ADVISORY,
        "One definition longer than the documented ceiling.",
    ),
    Signal(
        "duplicated_address_arithmetic",
        ADVISORY,
        "Inline address arithmetic repeated instead of named.",
    ),
    Signal(
        "repeated_magic_value",
        ADVISORY,
        "The same numeric literal above the documented repetition ceiling.",
    ),
    Signal(
        "stale_temporary",
        ADVISORY,
        "Temporary wording in a comment with no provisional marker.",
    ),
)

SIGNAL_BY_ID: dict[str, Signal] = {signal.id: signal for signal in SIGNALS}


# --- thresholds ------------------------------------------------------------
#
# Every figure below was chosen by reading this tree through this module's own
# scanner. Each is a judgement call, so each hard limit states the measurement
# that produced it, and only the residue classes are hard.

#: Longest comment run on the tree is 104 lines (a runtime probe's file header).
#: 40 flags 13 runs, all of them runtime/research probe headers; nothing in the
#: shipping toolkit reaches it.
COMMENT_BLOCK_MAX_LINES = 40

#: A ratio over a short file is noise, so the prose signal needs a floor. The
#: highest file-level comment ratio on the tree is 0.45, so this fires only on a
#: file that really is mostly prose. Nothing on the tree reaches it today.
FILE_PROSE_MIN_LINES = 80
FILE_PROSE_RATIO = 0.60

#: Three consecutive code-shaped comment lines. Two would fire on a single
#: commented example pair; four would miss a commented-out statement plus its
#: guard.
CODEFLAG_MIN_RUN = 3

#: Structural depth. Measured per language (brace depth, or indentation with
#: bracket continuations skipped). The tree's deepest code line is at depth 9
#: (two lines in one runtime probe's nested debugger loop); 8 leaves the rest of
#: the tree alone and is a judgement call, hence advisory.
NESTING_MAX_DEPTH = 8

#: One definition longer than this. Measured against this tree through the
#: module's own scanner, a few dozen definitions exceed it, headed by a very
#: long constructor and a data builder; a limit of 120 flagged far more and read
#: as noise, which is why this one is higher. The exact figures move as the tree
#: changes, so they are not restated here.
FUNCTION_MAX_LINES = 200

#: Two hex literals combined directly, e.g. ``0x08000000 + 0x1234``. The ticket
#: asks for exactly that shape, so both operands must be hex and adjacent; a hex
#: literal next to a named constant is not counted.
ADDRESS_ARITHMETIC_MIN_OPERANDS = 2

#: A numeric literal repeated more than this many times in one file. Strings are
#: excluded, so a repeated fixture value inside quotes is not counted, and a
#: zero-valued literal is skipped as a sentinel. 10 flags 21 files whose
#: repeated literal really is doing a table's work; 8 flagged 28 and started
#: listing ordinary fixture sizes.
MAGIC_VALUE_MIN_COUNT = 10

#: Short literals repeat for arithmetic reasons (``3``, ``16``, ``32``); a magic
#: value worth naming has at least this many digits, or is written in hex.
MAGIC_VALUE_MIN_DIGITS = 4

#: C1's bar, adopted by the owner on 2026-10-14: under 10% per file and at or
#: below 3% as the median across the files, measured on the lines a change adds.
#: The excess already inside a file is the census this gate does not own.
COMMENT_SHARE_MAX_PERCENT = 10.0
COMMENT_SHARE_MEDIAN_MAX_PERCENT = 3.0

COMMENT_SHARE_OUT_OF_SCOPE: tuple[str, ...] = ("tools/dragonbyte",)

#: Emitted in the JSON document so a stored report can be read against the
#: thresholds that produced it.
THRESHOLDS: dict[str, int | float] = {
    "comment_block_max_lines": COMMENT_BLOCK_MAX_LINES,
    "comment_share_max_percent": COMMENT_SHARE_MAX_PERCENT,
    "comment_share_median_max_percent": COMMENT_SHARE_MEDIAN_MAX_PERCENT,
    "file_prose_min_lines": FILE_PROSE_MIN_LINES,
    "file_prose_ratio": FILE_PROSE_RATIO,
    "codeflag_min_run": CODEFLAG_MIN_RUN,
    "nesting_max_depth": NESTING_MAX_DEPTH,
    "function_max_lines": FUNCTION_MAX_LINES,
    "address_arithmetic_min_operands": ADDRESS_ARITHMETIC_MIN_OPERANDS,
    "magic_value_min_count": MAGIC_VALUE_MIN_COUNT,
    "magic_value_min_digits": MAGIC_VALUE_MIN_DIGITS,
}


# --- encoded term table ----------------------------------------------------
#
# The repository must not carry the strings its own gate forbids, so the table
# is stored as base64 of a JSON array and decoded here. Each entry is
# ``[key, sample, pattern, flags, guard]``:
#
# * ``key`` groups entries by shape ("provider-name", "workflow-phrase"), which
#   is how a test selects one without naming it.
# * ``sample`` is a string the entry's pattern matches. Tests build their
#   fixtures from it, so no test file has to spell a forbidden term.
# * ``needle`` is a lower-case substring present in every match, used as a cheap
#   filter before the pattern runs. Searching all 196,000 lines with the whole
#   table cost 18 seconds; requiring one short literal first costs two.
# * ``flags`` is a letter set, ``i`` for case-insensitive.
# * ``guard`` optionally names a sense whose presence nearby makes the match an
#   ordinary technical use rather than development-process wording.

_ENCODED_TERMS = "".join([
    "W1sicHJvdmlkZXItbmFtZSIsImFudGhyb3BpYyIsIlxcYmFudGhyb3BpY1xcYiIsImkiLCIi",
    "LCJhbnRocm9waWMiXSxbInByb3ZpZGVyLW5hbWUiLCJvcGVuYWkiLCJcXGJvcGVuYWlcXGIi",
    "LCJpIiwiIiwib3BlbmFpIl0sWyJwcm9kdWN0LW5hbWUiLCJjaGF0Z3B0IiwiXFxiY2hhdGdw",
    "dFxcYiIsImkiLCIiLCJjaGF0Z3B0Il0sWyJwcm9kdWN0LW5hbWUiLCJjb3BpbG90IiwiXFxi",
    "Y29waWxvdFxcYiIsImkiLCIiLCJjb3BpbG90Il0sWyJwcm9kdWN0LW5hbWUiLCJnZW1pbmki",
    "LCJcXGJnZW1pbmlcXGIiLCJpIiwiIiwiZ2VtaW5pIl0sWyJwcm9kdWN0LW5hbWUiLCJjbGF1",
    "ZGUiLCJcXGJjbGF1ZGVcXGIiLCJpIiwiIiwiY2xhdWRlIl0sWyJwcm92aWRlci1uYW1lIiwi",
    "ZGVlcHNlZWsiLCJcXGJkZWVwc2Vla1xcYiIsImkiLCIiLCJkZWVwc2VlayJdLFsicHJvdmlk",
    "ZXItbmFtZSIsIm1pc3RyYWwiLCJcXGJtaXN0cmFsXFxiIiwiaSIsIiIsIm1pc3RyYWwiXSxb",
    "InByb2R1Y3QtbmFtZSIsImdyb2siLCJcXGJncm9rXFxiIiwiaSIsIiIsImdyb2siXSxbInBy",
    "b2R1Y3QtbmFtZSIsImNvZGV4IiwiXFxiY29kZXhcXGIiLCJpIiwiIiwiY29kZXgiXSxbInBy",
    "b2R1Y3QtbmFtZSIsImdwdCIsIlxcYmdwdHM/XFxiIiwiaSIsIiIsImdwdCJdLFsibW9kZWwt",
    "d29yZCIsImxhbmd1YWdlIG1vZGVsIiwiXFxibGFuZ3VhZ2VcXHMrbW9kZWxzP1xcYiIsImki",
    "LCIiLCJsYW5ndWFnZSJdLFsibW9kZWwtd29yZCIsImxsbSIsIlxcYmxsbXM/XFxiIiwiaSIs",
    "IiIsImxsbSJdLFsid29ya2Zsb3ctd29yZCIsInN1YmFnZW50IiwiXFxic3ViWy1cXHNdP2Fn",
    "ZW50cz9cXGIiLCJpIiwiIiwiYWdlbnQiXSxbIndvcmtmbG93LXdvcmQiLCJvcmNoZXN0cmF0",
    "aW9uIiwiXFxib3JjaGVzdHJhdGlvblxcYiIsImkiLCJidWlsZC1waXBlbGluZSIsIm9yY2hl",
    "c3RyYXRpb24iXSxbIndvcmtmbG93LXdvcmQiLCJvcmNoZXN0cmF0b3IiLCJcXGJvcmNoZXN0",
    "cmF0b3JzP1xcYiIsImkiLCJidWlsZC1waXBlbGluZSIsIm9yY2hlc3RyYXRvciJdLFsid29y",
    "a2Zsb3ctcGhyYXNlIiwidGhlIGFnZW50IiwiXFxidGhlIGFnZW50cz9cXGIiLCJpIiwiIiwi",
    "YWdlbnQiXSxbIndvcmtmbG93LXBocmFzZSIsImFuIGFnZW50IiwiXFxiYW4gYWdlbnRzP1xc",
    "YiIsImkiLCIiLCJhZ2VudCJdLFsid29ya2Zsb3ctd29yZCIsImFnZW50aWMiLCJcXGJhZ2Vu",
    "dGljXFxiIiwiaSIsIiIsImFnZW50aWMiXSxbIndvcmtmbG93LXBocmFzZSIsIm11bHRpIGFn",
    "ZW50IiwiXFxibXVsdGlbLVxcc10/YWdlbnRzP1xcYiIsImkiLCIiLCJhZ2VudCJdLFsid29y",
    "a2Zsb3ctcGhyYXNlIiwicHJvbXB0IGVuZ2luZWVyaW5nIiwiXFxicHJvbXB0W1xcc18tXWVu",
    "Z2luZWVyaW5nXFxiIiwiaSIsIiIsInByb21wdCJdLFsid29ya2Zsb3ctcGhyYXNlIiwic2Vz",
    "c2lvbiBzdGF0ZSIsIlxcYnNlc3Npb25bXFxzXy1dc3RhdGVcXGIiLCJpIiwiZ3VpLXNlc3Np",
    "b24iLCJzZXNzaW9uIl0sWyJhYmJyZXZpYXRpb24iLCJBSSIsIig/PCFbQS1aYS16MC05X10p",
    "QUkoPzpzfCdzKT8oPyFbQS1aYS16MC05X10pIiwiIiwiIiwiYWkiXV0="
])

#: A hit on a table entry carrying a guard is read as an ordinary technical use
#: when the guard matches the wording around the hit, not just the hit's own
#: line: these words are documented in paragraphs, and the paragraph is the
#: sense. Two guards, both demanded by the ticket's own examples:
#:
#: * ``build-pipeline`` - the word as software that joins stages (a build, a
#:   probe run, a deploy), which is how this repository uses it throughout.
#: * ``gui-session`` - state belonging to the desktop session object, which the
#:   workbench names on almost every line that mentions it.
#:
#: The window is three lines either side. Chosen against the tree: one line is
#: too narrow (the sense is named in the line before or after the hit in every
#: real case here) and five starts to swallow unrelated paragraphs.
_SENSE_WINDOW = 3

_SENSE_GUARDS: dict[str, re.Pattern[str]] = {
    "build-pipeline": re.compile(
        r"(?i)\b(?:build|rebuild|pipeline|deploy|release|extract|materiali[sz]|"
        r"install|publish|stage|probe|runtime|emulator|debugger|lua|breakpoint|"
        r"infrastructure|identification)\w*\b"
    ),
    "gui-session": re.compile(
        r"(?i)(?:workbench|session\.|_session|panel|widget|dialog|editor|tab\b|"
        r"window|atlas|profile|gui\b|chrome|shell|scrollbar|qwidget|qt\b)"
    ),
}

_FLAG_BITS: dict[str, int] = {"i": re.IGNORECASE, "m": re.MULTILINE}


@dataclass(frozen=True, slots=True)
class TermEntry:
    """One forbidden term: its group, a matching sample, and its needle."""

    key: str
    sample: str
    pattern: re.Pattern[str]
    guard: str
    needle: str


def _decode_term_table() -> tuple[TermEntry, ...]:
    payload = json.loads(base64.b64decode(_ENCODED_TERMS).decode("utf-8"))
    table = []
    for key, sample, pattern, flags, guard, needle in payload:
        bits = 0
        for letter in flags:
            bits |= _FLAG_BITS[letter]
        table.append(
            TermEntry(
                str(key),
                str(sample),
                re.compile(str(pattern), bits),
                str(guard),
                str(needle).lower(),
            )
        )
    return tuple(table)


#: The decoded table, in encoded order.
TERM_TABLE: tuple[TermEntry, ...] = _decode_term_table()

#: Group keys present in the table, e.g. "provider-name" or "workflow-phrase".
TERM_KEYS: tuple[str, ...] = tuple(sorted({entry.key for entry in TERM_TABLE}))


def term_entries(key: str) -> tuple[TermEntry, ...]:
    """Table entries in one group. Tests select terms this way, never by name."""
    return tuple(entry for entry in TERM_TABLE if entry.key == key)


def _combine(groups: Sequence[tuple[str, str, str]]) -> re.Pattern[str]:
    """One alternation with a named group per source: (name, pattern, flags).

    Used where a class has several patterns and only one search per line is
    affordable. Scoped ``(?i:...)`` keeps each source's own case sensitivity.
    """
    parts = []
    for name, source, flags in groups:
        if source.startswith("(?i)"):
            # A leading global flag is only legal at the start of the whole
            # expression; lift it into the group's own scoped flag.
            source = source[4:]
            flags += "i"
        body = f"(?i:{source})" if "i" in flags else source
        parts.append(f"(?P<{name}>{body})")
    return re.compile("|".join(parts))


# --- lexical model ---------------------------------------------------------


@dataclass(slots=True)
class _LexState:
    """Carried across lines: an open block comment or an open long string."""

    block_end: str | None = None
    string: str | None = None


@lru_cache(maxsize=None)
def _scanner(language: Language) -> re.Pattern[str]:
    """One token scan per language, instead of a character loop per line.

    The alternative (walking each character and asking whether a comment marker
    starts here) cost 24 million ``startswith`` calls on this tree. Searching
    for the next token of interest makes the same decision in C.
    """
    tokens = [language.line_comment, *language.string_delimiters]
    if language.block_comment is not None:
        tokens.append(language.block_comment[0])
    ordered = sorted(set(tokens), key=len, reverse=True)
    return re.compile("|".join(re.escape(token) for token in ordered))


def _closing(text: str, token: str, position: int) -> int:
    """The next *token* that is not backslash-escaped, or -1 when there is none."""
    end = text.find(token, position)
    while end != -1:
        if not (len(text[:end]) - len(text[:end].rstrip("\\"))) % 2:
            return end
        end = text.find(token, end + 1)
    return -1


def _split_line(text: str, language: Language, state: _LexState) -> tuple[str, str]:
    """Split one raw line into (code, comment); string bodies leave both empty.

    Here-strings, long-bracket strings and template literals count as ordinary
    quoted strings, so their bodies read as string text and never as code.
    """
    code: list[str] = []
    comment: list[str] = []
    block = language.block_comment
    position = 0
    length = len(text)

    if state.block_end is not None:
        end = text.find(state.block_end, position)
        if end < 0:
            return "", text
        comment.append(text[: end + len(state.block_end)])
        position = end + len(state.block_end)
        state.block_end = None
    if state.string is not None:
        end = _closing(text, state.string, position)
        if end < 0:
            return "", "".join(comment)
        position = end + len(state.string)
        state.string = None

    scanner = _scanner(language)
    while position < length:
        match = scanner.search(text, position)
        if match is None:
            code.append(text[position:])
            break
        code.append(text[position : match.start()])
        token = match.group(0)
        position = match.end()
        if token == language.line_comment:
            comment.append(text[match.start() :])
            break
        if block is not None and token == block[0]:
            end = text.find(block[1], position)
            if end < 0:
                comment.append(text[match.start() :])
                state.block_end = block[1]
                position = length
            else:
                comment.append(text[match.start() : end + len(block[1])])
                position = end + len(block[1])
            continue
        # A string delimiter: its body, which may run on to the next line, is
        # never code and never a comment.
        end = _closing(text, token, position)
        if end < 0:
            state.string = token
            position = length
        else:
            position = end + len(token)
    return "".join(code), "".join(comment)


@dataclass(frozen=True, slots=True)
class LineView:
    """One line as the detectors see it."""

    number: int
    raw: str
    code: str
    comment: str
    comment_only: bool
    depth: int


def _indent_units(raw: str) -> int:
    width = 0
    for character in raw:
        if character == " ":
            width += 1
        elif character == "\t":
            width += 4
        else:
            break
    return width // 4


def _bracket_balance(code: str) -> int:
    return (
        code.count("(")
        + code.count("[")
        + code.count("{")
        - code.count(")")
        - code.count("]")
        - code.count("}")
    )


def _line_views(text: str, language: Language) -> tuple[LineView, ...]:
    views: list[LineView] = []
    state = _LexState()
    brace_depth = 0
    continuation = 0
    for number, raw in enumerate(text.splitlines(), 1):
        code, comment = _split_line(raw, language, state)
        stripped = code.strip()
        comment_only = not stripped and bool(comment.strip())
        if language.indent_nesting:
            depth = _indent_units(raw) if stripped and continuation == 0 else 0
            continuation = max(0, continuation + _bracket_balance(code))
        else:
            if stripped:
                brace_depth += code.count("{") - code.count("}")
            depth = brace_depth
        views.append(
            LineView(
                number=number,
                raw=raw,
                code=code,
                comment=comment,
                comment_only=comment_only,
                depth=depth,
            )
        )
    return tuple(views)


def _docstring_lines(text: str, language: Language) -> frozenset[int]:
    """The lines a Python docstring occupies: the first statement of a module, class or function."""
    if language is not PYTHON:
        return frozenset()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return frozenset()
    spans: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.body:
            continue
        first = node.body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            spans.update(range(first.lineno, (first.end_lineno or first.lineno) + 1))
    return frozenset(spans)


def _comment_body(comment: str, language: Language) -> str:
    """The text of a comment with its markers and decoration removed."""
    body = comment
    if language.block_comment is not None:
        body = body.replace(language.block_comment[0], " ")
        body = body.replace(language.block_comment[1], " ")
    body = body.replace(language.line_comment, " ")
    return body.strip().lstrip("*").strip()


# --- hard detectors --------------------------------------------------------

#: A banner, a table rule or a separator: filler, never an implementation.
_BANNER = re.compile(r"^[-=*#~_+|/\\<>.,:;\s{}()]+$")
_TABLE_ROW = re.compile(r"^\|.*\|$")
_URL = re.compile(r"(?:https?://|www\.)\S", re.IGNORECASE)

#: Commented-out code is recognised from how a statement begins or ends, not
#: from a bag of keywords: "do NOT re-derive" and "``Path()`` sees it" are prose
#: that a keyword list reads as code, and both were false positives here.
_STATEMENT_START = re.compile(
    r"^(?:if|elif|else|elseif|for|foreach|while|return|switch|case|break|"
    r"continue|def|class|function|local|let|const|var|import|from|try|except|"
    r"catch|finally|param|throw|raise|yield|await|async|print|echo|exit)\b"
)
_LVALUE_START = re.compile(r"^[A-Za-z_$][\w.$\[\]'\"]*\s*(?:=(?!=)|\+=|-=|\*=|/=|:=)")
_CALL_END = re.compile(r"\b[A-Za-z_$][\w.$]*\([^()]*\)\s*$")
_TERMINATOR_END = re.compile(r"[;{}]\s*$")
_SELF_TERMINATING = re.compile(r"\b(?:end|fi|done|break|continue|pass|return)\s*$")
#: Something a statement does: assigns, calls, or opens a block. A line that
#: only ends with a semicolon is a list separator in the comment banners this
#: repository uses, not code.
_CODE_TOKEN = re.compile(
    r"(?:[A-Za-z_$][\w.$]*\s*=(?!=)|\b[A-Za-z_$][\w.$]*\(|\b(?:if|elif|else|for|"
    r"foreach|while|return|def|class|function|local|let|const|var|import|from|"
    r"switch|case|try|except|catch|finally|param|print|echo)\b)"
)


def _looks_like_code(body: str) -> bool:
    """Whether a stripped comment body reads as an implementation line.

    A line counts when it opens like a statement (a control keyword or an
    assignment to a named target) or closes like one (a call ending the line, or
    a terminator on a line that also does something). Prose that quotes a call
    mid-sentence, prose bullets ending in a list semicolon, and address tables
    whose lines start with a literal all fail this and are not code.
    """
    if len(body) < 4 or _BANNER.match(body) or _TABLE_ROW.match(body) or _URL.search(body):
        return False
    if _STATEMENT_START.match(body) or _LVALUE_START.match(body) or _CALL_END.search(body):
        return True
    if _TERMINATOR_END.search(body) and _CODE_TOKEN.search(body):
        return True
    return bool(_SELF_TERMINATING.search(body))


def _detect_narration(rel_path: str, views: Sequence[LineView]) -> list[Finding]:
    findings = []
    for index, view in enumerate(views):
        lowered = view.raw.lower()
        for entry in TERM_TABLE:
            if entry.needle not in lowered:
                continue
            match = entry.pattern.search(view.raw)
            if match is None:
                continue
            guard = _SENSE_GUARDS.get(entry.guard) if entry.guard else None
            if guard is not None and guard.search(_window_text(views, index)):
                continue
            findings.append(
                Finding(rel_path, view.number, "process_narration", HARD, match.group(0))
            )
            break
    return findings


def _window_text(views: Sequence[LineView], index: int) -> str:
    start = max(0, index - _SENSE_WINDOW)
    end = min(len(views), index + _SENSE_WINDOW + 1)
    return "\n".join(view.raw for view in views[start:end])


def _detect_commented_out_code(
    rel_path: str, views: Sequence[LineView], language: Language
) -> list[Finding]:
    findings = []
    start: LineView | None = None
    run = 0
    for view in views:
        body = _comment_body(view.comment, language) if view.comment_only else ""
        if body and _looks_like_code(body):
            if start is None:
                start = view
            run += 1
            continue
        if run >= CODEFLAG_MIN_RUN and start is not None:
            findings.append(
                Finding(
                    rel_path,
                    start.number,
                    "commented_out_code",
                    HARD,
                    start.raw.strip(),
                )
            )
        start = None
        run = 0
    if run >= CODEFLAG_MIN_RUN and start is not None:
        findings.append(
            Finding(rel_path, start.number, "commented_out_code", HARD, start.raw.strip())
        )
    return findings


_DEBT_MARKER = re.compile(r"\b(?:TODO|FIXME|XXX|HACK)\b")
_DEBUG_AID = re.compile(
    r"(?:\bprint\s*\(|\bconsole\.(?:log|debug|warn|error)\b|\bWrite-(?:Host|Output|Debug)\b|"
    r"\bDebug\.\w+|\bprintf\b|\bputs\b|\bbreakpoint\b|\bpdb\b|\bdebugger\b|\bStop-Process\b)"
)
_ABSOLUTE_LOCAL_PATH = re.compile(r"[A-Za-z]:\\|/home/|/Users/")
_SELF_REMOVAL = re.compile(
    r"(?i)\b(?:temporary|for now|remove (?:this|me|before)|delete (?:this|me)|"
    r"do not commit|don't commit|not for commit)\b"
)


def _detect_debug_residue(rel_path: str, views: Sequence[LineView]) -> list[Finding]:
    findings = []
    for view in views:
        marker_text = view.comment or view.code
        if not _DEBT_MARKER.search(marker_text):
            continue
        if not (
            _DEBUG_AID.search(view.raw)
            or _ABSOLUTE_LOCAL_PATH.search(view.raw)
            or _SELF_REMOVAL.search(view.raw)
        ):
            continue
        findings.append(
            Finding(rel_path, view.number, "debug_residue", HARD, view.raw.strip())
        )
    return findings


#: An absolute path that starts in a per-user location. A drive-letter path
#: elsewhere (a build directory, a tool install) is machine-specific too, but it
#: is not a user-profile leak, and flagging it would bury the real ones.
_USER_PATH = re.compile(
    r"(?i)(?<![A-Za-z0-9_])[A-Za-z]:\\(?:Users|Documents and Settings|AppData|"
    r"Desktop|Downloads|OneDrive)\\[^\s\"'`;,\)]+"
)

#: A commercial game's image, save or state file inside an absolute path. The
#: absolute prefix is required, and that requirement is the whole calibration:
#: the tree names the canonical ROM's local filename in 99 places, all of them
#: the documented "put your own verified copy here" convention that `.gitignore`
#: covers (`roms/Dragon Ball Z - Buu's Fury (U).gba`). Flagging those would bury
#: the one reference that really is machine-specific. Against this tree: 99
#: relative references and 1 absolute.
_ROM_FILENAME = re.compile(
    r"(?i)(?:[A-Za-z]:\\|\\\\|/home/|/Users/)[^\"'\n]*?"
    r"(?:buu'*s?\s+fury|legacy of goku|dragon ball)[^\"'\n]{0,60}?"
    r"\.(?:gba|agb|sav|srm|sps|ss[0-9]|state)\b"
)

_CREDENTIALS: tuple[str, ...] = (
    r"\b(?:api[_-]?key|secret|password|passwd|token|bearer|access[_-]?key)"
    r"\b\s*[:=]\s*[\"'][^\"']{16,}[\"']",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"\bsk-[A-Za-z0-9_-]{20,}\b",
    r"\bghp_[A-Za-z0-9]{30,}\b",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
)

#: One alternation for the whole proprietary class, for the same reason the term
#: table has a needle filter: six searches per line, 196,000 lines. The cheap
#: literals below gate it, because a line with no backslash, no game title and
#: no credential-shaped word cannot hold any of these patterns.
_PROPRIETARY_COMBINED = _combine(
    [
        ("user_path", _USER_PATH.pattern, "i"),
        ("rom_filename", _ROM_FILENAME.pattern, "i"),
        ("credential", "|".join(f"(?:{source})" for source in _CREDENTIALS), "i"),
    ]
)
_PROPRIETARY_NEEDLES: tuple[str, ...] = (
    "\\",
    "/home/",
    "/users/",
    "buu",
    "goku",
    "dragon ball",
    "akia",
    "sk-",
    "ghp_",
    "private key",
    "api",
    "token",
    "secret",
    "password",
    "passwd",
    "bearer",
)
_PROPRIETARY_SIGNAL: dict[str, str] = {
    "user_path": "proprietary_user_path",
    "rom_filename": "proprietary_rom_filename",
    "credential": "credential_shaped",
}


def _detect_proprietary(rel_path: str, views: Sequence[LineView]) -> list[Finding]:
    findings = []
    for view in views:
        lowered = view.raw.lower()
        if not any(needle in lowered for needle in _PROPRIETARY_NEEDLES):
            continue
        for match in _PROPRIETARY_COMBINED.finditer(view.raw):
            signal = _PROPRIETARY_SIGNAL[match.lastgroup]
            findings.append(Finding(rel_path, view.number, signal, HARD, match.group(0)))
    return findings


# --- advisory detectors ----------------------------------------------------


def _detect_comment_blocks(rel_path: str, views: Sequence[LineView]) -> list[Finding]:
    findings = []
    for start, length in _comment_runs(views):
        if length <= COMMENT_BLOCK_MAX_LINES:
            continue
        findings.append(
            Finding(
                rel_path,
                start.number,
                "oversized_comment_block",
                ADVISORY,
                start.raw.strip(),
            )
        )
    return findings


def _comment_runs(views: Sequence[LineView]) -> list[tuple[LineView, int]]:
    """Maximal runs of consecutive comment-only lines, as (first, length)."""
    runs: list[tuple[LineView, int]] = []
    start: LineView | None = None
    length = 0
    for view in views:
        if view.comment_only:
            if start is None:
                start = view
            length += 1
            continue
        if start is not None:
            runs.append((start, length))
        start = None
        length = 0
    if start is not None:
        runs.append((start, length))
    return runs


def _detect_excessive_prose(
    rel_path: str, views: Sequence[LineView], file_comment_ratio: float
) -> list[Finding]:
    if len(views) < FILE_PROSE_MIN_LINES or file_comment_ratio < FILE_PROSE_RATIO:
        return []
    return [
        Finding(
            rel_path,
            1,
            "excessive_prose",
            ADVISORY,
            f"{file_comment_ratio:.2f} of {len(views)} lines are comment",
        )
    ]


def _detect_todo_debt(
    rel_path: str, views: Sequence[LineView], already: Iterable[Finding]
) -> list[Finding]:
    reported = {finding.line for finding in already}
    findings = []
    for view in views:
        if view.number in reported:
            continue
        text = view.comment or view.code
        hit = _DEBT_MARKER.search(text)
        if hit is None:
            continue
        findings.append(
            Finding(rel_path, view.number, "todo_debt", ADVISORY, view.raw.strip())
        )
    return findings


_PLACEHOLDER_ASSIGNMENT = re.compile(
    r"(?<![\w.])(?:tmp2?|foo|bar|baz|data1|obj2|xxx|todo)\s*(?:=(?!=)|:=|:)"
)
_SINGLE_LETTER_DEFINITION = re.compile(r"\b(?:def|class|function)\s+([A-Za-z])\b")
_DECOMPILER_NAME = re.compile(r"\b(?:sub|FUN|loc|DAT|unk)_[0-9A-Fa-f]{4,8}\b")


def _detect_placeholder_identifiers(
    rel_path: str, views: Sequence[LineView]
) -> list[Finding]:
    findings = []
    for view in views:
        if not view.code.strip():
            continue
        hit = (
            _PLACEHOLDER_ASSIGNMENT.search(view.code)
            or _SINGLE_LETTER_DEFINITION.search(view.code)
            or _DECOMPILER_NAME.search(view.code)
        )
        if hit is None:
            continue
        findings.append(
            Finding(
                rel_path,
                view.number,
                "placeholder_identifier",
                ADVISORY,
                hit.group(0),
            )
        )
    return findings


def _detect_deep_nesting(rel_path: str, views: Sequence[LineView]) -> list[Finding]:
    findings = []
    inside = False
    for view in views:
        too_deep = bool(view.code.strip()) and view.depth > NESTING_MAX_DEPTH
        if too_deep and not inside:
            findings.append(
                Finding(
                    rel_path,
                    view.number,
                    "deep_nesting",
                    ADVISORY,
                    f"depth {view.depth}",
                )
            )
        inside = too_deep
    return findings


_PY_FUNCTION = re.compile(r"^(?P<indent>\s*)(?:async\s+)?def\s+\w+")
_JS_FUNCTION = re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+\w+")
_PS_FUNCTION = re.compile(r"^\s*function\s+[\w:-]+", re.IGNORECASE)
_LUA_FUNCTION = re.compile(r"^\s*(?:local\s+)?function\s+[\w.:]*")
_LUA_OPEN = re.compile(r"\b(?:function|if|for|while|repeat)\b")
_LUA_CLOSE = re.compile(r"\b(?:end|until)\b")


def _detect_giant_functions(
    rel_path: str, views: Sequence[LineView], language: Language
) -> list[Finding]:
    findings: list[Finding] = []
    for index, view in enumerate(views):
        span = _function_span(views, index, language)
        if span is None or span < FUNCTION_MAX_LINES:
            continue
        findings.append(
            Finding(
                rel_path,
                view.number,
                "giant_function",
                ADVISORY,
                f"{span} lines: {view.raw.strip()[:80]}",
            )
        )
    return findings


def _function_span(
    views: Sequence[LineView], index: int, language: Language
) -> int | None:
    """Length in lines of the definition starting at *index*, or None.

    Coverage is deliberately lexical and stated in the README of the signal:
    Python by indentation, brace languages by brace depth, Lua by block
    keywords. Nested definitions are measured separately, so a long outer
    function and a long inner one are two findings rather than one.
    """
    line = views[index]
    if language is PYTHON:
        match = _PY_FUNCTION.match(line.raw)
        if match is None:
            return None
        indent = len(match.group("indent"))
        end = len(views)
        for offset in range(index + 1, len(views)):
            raw = views[offset].raw
            if not raw.strip():
                continue
            if len(raw) - len(raw.lstrip()) <= indent:
                end = offset
                break
        return end - index
    if language is LUA:
        if _LUA_FUNCTION.match(line.raw) is None:
            return None
        # A one-line definition (``local function r8(a) return read(a) end``) is
        # common in the runtime probes; count its own closer so it is not read
        # as opening a block that a later line has to close.
        balance = len(_LUA_OPEN.findall(line.code)) - len(_LUA_CLOSE.findall(line.code))
        if balance <= 0:
            return None
        for offset in range(index + 1, len(views)):
            code = views[offset].code
            balance += len(_LUA_OPEN.findall(code)) - len(_LUA_CLOSE.findall(code))
            if balance <= 0:
                return offset - index + 1
        return len(views) - index
    if language is POWERSHELL:
        if _PS_FUNCTION.match(line.raw) is None:
            return None
    elif _JS_FUNCTION.match(line.raw) is None:
        return None
    balance = line.code.count("{") - line.code.count("}")
    if balance <= 0:
        return None
    for offset in range(index + 1, len(views)):
        code = views[offset].code
        balance += code.count("{") - code.count("}")
        if balance <= 0:
            return offset - index + 1
    return len(views) - index


#: Raw address arithmetic: an address-sized literal (six hex digits, the width
#: of a GBA address) combined with another literal by + or -. The first draft
#: accepted any two hex literals with any operator and flagged 29 lines, nearly
#: all of them size deltas and bit masks in tests, so the address width and the
#: arithmetic operators are both required. 11 lines remain, every one of them a
#: real address pair the code should name.
_HEX_ARITHMETIC = re.compile(
    r"(?:0[xX][0-9a-fA-F]{6,}\s*[+\-]\s*0[xX][0-9a-fA-F]+"
    r"|0[xX][0-9a-fA-F]+\s*[+\-]\s*0[xX][0-9a-fA-F]{6,})"
)
_NUMBER = re.compile(r"(?<![\w.])(0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?)(?![\w.])")


def _detect_address_arithmetic(rel_path: str, views: Sequence[LineView]) -> list[Finding]:
    findings = []
    for view in views:
        hit = _HEX_ARITHMETIC.search(view.code)
        if hit is None:
            continue
        findings.append(
            Finding(
                rel_path,
                view.number,
                "duplicated_address_arithmetic",
                ADVISORY,
                hit.group(0),
            )
        )
    return findings


def _detect_repeated_magic_values(
    rel_path: str, views: Sequence[LineView]
) -> list[Finding]:
    first_line: dict[str, int] = {}
    counts: dict[str, int] = {}
    for view in views:
        for value in _NUMBER.findall(view.code):
            if value[:2].lower() == "0x":
                digits, numeric = value[2:], int(value, 16)
            else:
                digits, numeric = value.replace(".", ""), float(value)
            if len(digits) < MAGIC_VALUE_MIN_DIGITS or numeric == 0:
                # Short literals repeat for arithmetic reasons and a zero is a
                # sentinel; neither is a value worth naming.
                continue
            counts[value] = counts.get(value, 0) + 1
            first_line.setdefault(value, view.number)
    findings = []
    for value in sorted(counts, key=lambda item: (-counts[item], item)):
        if counts[value] <= MAGIC_VALUE_MIN_COUNT:
            continue
        findings.append(
            Finding(
                rel_path,
                first_line[value],
                "repeated_magic_value",
                ADVISORY,
                f"{value} appears {counts[value]} times",
            )
        )
    return findings


_TEMPORARY_WORD = re.compile(r"(?i)\b(?:temporary|for now|placeholder)\b")
#: Only the sense in which the word describes the code's own incompleteness
#: counts. This repository also uses the words for local artifacts that are
#: meant to be transient (a temporary sibling file, a scratch project) and for
#: a named record in the game data (an absent-layer placeholder), and the first
#: draft flagged nine of those. ``for now`` has no such sense and always counts.
_TEMPORARY_CODE_SENSE = re.compile(
    r"(?i)\bfor now\b"
    r"|\btemporary\b(?!\s+(?:\w+\s+){0,2}(?:root|dir|directory|file|path|storage|"
    r"space|copy|folder|project|sibling|record|container|marker|token|buffer|"
    r"table|entry|slot|image|layer|grid|substitute))"
    r"|\bplaceholder\b(?=\s+(?:value|values|implementation|impl|code|function|"
    r"method|name|id|identifier|return|branch|parameter|argument|shim|workaround|"
    r"hack|constant|default))"
)
#: The documented provisional mechanism: a comment may call something temporary
#: when the same comment run also names it as unmeasured, or carries the ticket
#: that owns the measurement. Without one of these the wording has outlived its
#: reason, which is the whole signal.
_PROVISIONAL_MARKER = re.compile(
    r"(?i)\b(?:provisional|unmeasured|unverified|not measured|not yet measured|"
    r"unproven|unknown|TODO|FIXME)\b|\b[A-Z][A-Z0-9]{2,}-\d{3}\b"
)


def _detect_stale_temporary(
    rel_path: str, views: Sequence[LineView], language: Language
) -> list[Finding]:
    findings = []
    for start, length in _comment_runs(views):
        window = views[start.number - 1 : start.number - 1 + length]
        joined = " ".join(_comment_body(view.comment, language) for view in window)
        if not _TEMPORARY_WORD.search(joined):
            continue
        if _PROVISIONAL_MARKER.search(joined):
            continue
        for view in window:
            body = _comment_body(view.comment, language)
            if not _TEMPORARY_CODE_SENSE.search(body):
                continue
            findings.append(
                Finding(
                    rel_path,
                    view.number,
                    "stale_temporary",
                    ADVISORY,
                    view.raw.strip(),
                )
            )
    return findings


# --- per-file analysis -----------------------------------------------------


@dataclass(frozen=True, slots=True)
class Finding:
    path: str
    line: int
    signal: str
    severity: str
    text: str

    def as_document(self) -> dict[str, object]:
        return {
            "path": self.path,
            "line": self.line,
            "signal": self.signal,
            "severity": self.severity,
            "text": _excerpt(self.text),
        }


def _excerpt(text: str) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= EXCERPT_LIMIT:
        return collapsed
    return collapsed[: EXCERPT_LIMIT - 3] + "..."


@dataclass(frozen=True, slots=True)
class FileReport:
    path: str
    language: str
    lines: int
    comment_lines: int
    docstring_lines: int
    changed_lines: int
    changed_comment_lines: int
    findings: tuple[Finding, ...]


def analyze_text(
    rel_path: str, text: str, language: Language | None = None
) -> tuple[Finding, ...]:
    """Every finding in *text*, sorted by (path, line, signal).

    The single entry point the tests use: no filesystem, no git, no import of
    the text under test.
    """
    resolved = language if language is not None else language_for(rel_path)
    if resolved is None:
        raise ValueError(f"unsupported source suffix: {rel_path}")
    return analyze_file(rel_path, text, resolved).findings


def analyze_file(
    rel_path: str,
    text: str,
    language: Language,
    *,
    changed_lines: Collection[int] | None = (),
) -> FileReport:
    views = _line_views(text, language)
    comment_lines = sum(1 for view in views if view.comment.strip())
    ratio = comment_lines / len(views) if views else 0.0
    docstrings = _docstring_lines(text, language)
    if changed_lines is None:
        measured = list(views)
    else:
        changed = set(changed_lines)
        measured = [view for view in views if view.number in changed]

    findings: list[Finding] = []
    findings.extend(_detect_narration(rel_path, views))
    findings.extend(_detect_commented_out_code(rel_path, views, language))
    hard_residue = _detect_debug_residue(rel_path, views)
    findings.extend(hard_residue)
    findings.extend(_detect_proprietary(rel_path, views))
    findings.extend(_detect_comment_blocks(rel_path, views))
    findings.extend(_detect_excessive_prose(rel_path, views, ratio))
    findings.extend(_detect_todo_debt(rel_path, views, hard_residue))
    findings.extend(_detect_placeholder_identifiers(rel_path, views))
    findings.extend(_detect_deep_nesting(rel_path, views))
    findings.extend(_detect_giant_functions(rel_path, views, language))
    findings.extend(_detect_address_arithmetic(rel_path, views))
    findings.extend(_detect_repeated_magic_values(rel_path, views))
    findings.extend(_detect_stale_temporary(rel_path, views, language))

    ordered = tuple(
        sorted(findings, key=lambda finding: (finding.path, finding.line, finding.signal))
    )
    return FileReport(
        path=rel_path,
        language=language.name,
        lines=len(views),
        comment_lines=comment_lines,
        docstring_lines=len(docstrings),
        changed_lines=len(measured),
        changed_comment_lines=sum(
            1 for view in measured if view.comment.strip() or view.number in docstrings
        ),
        findings=ordered,
    )


def _percent(part: int, whole: int) -> float:
    return 100.0 * part / whole if whole else 0.0


@dataclass(frozen=True, slots=True)
class CommentShare:
    path: str
    lines: int
    comment_lines: int
    changed_lines: int
    changed_comment_lines: int

    @property
    def percent(self) -> float:
        return _percent(self.comment_lines, self.lines)

    @property
    def changed_percent(self) -> float:
        return _percent(self.changed_comment_lines, self.changed_lines)

    def as_document(self) -> dict[str, object]:
        return {
            "path": self.path,
            "lines": self.lines,
            "comment_and_docstring_lines": self.comment_lines,
            "percent": round(self.percent, 2),
            "changed_lines": self.changed_lines,
            "changed_comment_and_docstring_lines": self.changed_comment_lines,
            "changed_percent": round(self.changed_percent, 2),
        }


# --- exceptions ------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ExceptionRule:
    path: str
    signal: str
    reason: str


@dataclass(frozen=True, slots=True)
class ExceptionTable:
    rules: tuple[ExceptionRule, ...] = ()
    invalid: tuple[str, ...] = ()


def load_exceptions(path: Path) -> ExceptionTable:
    """Read the exceptions file. A missing file is an empty table, not an error.

    An entry without a reason is rejected rather than honoured: a suppression
    nobody can read is indistinguishable from a detector that stopped working.
    """
    if not path.is_file():
        return ExceptionTable()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"{path}: {error}") from error
    if not isinstance(payload, dict) or not isinstance(payload.get("exceptions"), list):
        raise ValueError(f"{path}: expected an object with an 'exceptions' list")
    rules = []
    invalid = []
    for index, entry in enumerate(payload["exceptions"]):
        if not isinstance(entry, dict):
            invalid.append(f"exceptions[{index}]: not an object")
            continue
        rule_path = str(entry.get("path", "")).strip()
        signal = str(entry.get("signal", "")).strip()
        reason = str(entry.get("reason", "")).strip()
        if not rule_path or not signal:
            invalid.append(f"exceptions[{index}]: needs both 'path' and 'signal'")
            continue
        if signal not in SIGNAL_BY_ID:
            invalid.append(f"exceptions[{index}]: unknown signal {signal!r}")
            continue
        if not reason:
            invalid.append(f"exceptions[{index}] ({rule_path}, {signal}): empty reason")
            continue
        rules.append(ExceptionRule(rule_path, signal, reason))
    return ExceptionTable(rules=tuple(rules), invalid=tuple(invalid))


def apply_exceptions(
    findings: Sequence[Finding], table: ExceptionTable
) -> tuple[tuple[Finding, ...], tuple[Finding, ...], tuple[ExceptionRule, ...]]:
    """Split *findings* into (kept, suppressed) and report the rules never used."""
    kept: list[Finding] = []
    suppressed: list[Finding] = []
    used: set[int] = set()
    for finding in findings:
        for index, rule in enumerate(table.rules):
            if finding.signal != rule.signal:
                continue
            if not fnmatch.fnmatchcase(finding.path, rule.path):
                continue
            used.add(index)
            suppressed.append(finding)
            break
        else:
            kept.append(finding)
    unused = tuple(rule for index, rule in enumerate(table.rules) if index not in used)
    return tuple(kept), tuple(suppressed), unused


# --- repository scan -------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ScanResult:
    selector: str
    revision: str | None
    files_scanned: int
    total_lines: int
    comment_lines: int
    findings: tuple[Finding, ...]
    suppressed: tuple[Finding, ...]
    exceptions: ExceptionTable
    unused_exceptions: tuple[ExceptionRule, ...]
    unreadable: tuple[str, ...] = ()
    blocked: str | None = None
    comment_share: tuple[CommentShare, ...] = ()

    @property
    def comment_share_percent(self) -> float:
        return _percent(
            sum(row.comment_lines for row in self.comment_share),
            sum(row.lines for row in self.comment_share),
        )

    @property
    def comment_share_median(self) -> float | None:
        measured = [row.changed_percent for row in self.comment_share if row.changed_lines]
        return statistics.median(measured) if measured else None

    @property
    def hard_findings(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity == HARD)

    @property
    def advisory_findings(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity == ADVISORY)

    def per_signal(self) -> dict[str, int]:
        counts = {signal.id: 0 for signal in SIGNALS}
        for finding in self.findings:
            counts[finding.signal] += 1
        return counts

    def per_signal_suppressed(self) -> dict[str, int]:
        counts = {signal.id: 0 for signal in SIGNALS}
        for finding in self.suppressed:
            counts[finding.signal] += 1
        return counts


def _git(args: Sequence[str], root: Path) -> str | None:
    """Run git in *root*; None when git is absent or the command fails."""
    if shutil.which("git") is None:
        return None
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout


def _tracked_source_paths(root: Path) -> list[str] | None:
    output = _git(["ls-files"], root)
    if output is None:
        return None
    return [line.strip() for line in output.splitlines() if line.strip()]


def _untracked_paths(root: Path) -> list[str] | None:
    output = _git(["ls-files", "--others", "--exclude-standard"], root)
    if output is None:
        return None
    return [line.strip() for line in output.splitlines() if line.strip()]


def _changed_source_paths(root: Path, revision: str) -> list[str] | None:
    tracked = _git(["diff", "--name-only", "--diff-filter=ACMR", revision], root)
    if tracked is None:
        return None
    untracked = _untracked_paths(root)
    if untracked is None:
        return None
    paths = [line.strip() for line in tracked.splitlines() if line.strip()]
    paths += untracked
    return sorted(set(paths))


_HUNK_START = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

#: The added line numbers come from the diff, so comments already in a file
#: cannot be failed by a later change to it.
def _changed_line_numbers(root: Path, revision: str) -> dict[str, frozenset[int]] | None:
    output = _git(
        ["diff", "--unified=0", "--no-color", "--diff-filter=ACMR", "-M", revision],
        root,
    )
    if output is None:
        return None
    added: dict[str, set[int]] = {}
    path: str | None = None
    number = 0
    in_hunk = False
    for line in output.splitlines():
        if line.startswith("diff --git"):
            in_hunk = False
            continue
        if not in_hunk and line.startswith("+++ "):
            target = line[4:].strip()
            path = None if target == "/dev/null" else target.removeprefix("b/")
            continue
        if line.startswith("@@"):
            start = _HUNK_START.match(line)
            in_hunk = start is not None and path is not None
            if in_hunk:
                number = int(start.group(1))
            continue
        if not in_hunk or path is None:
            continue
        if line.startswith("+"):
            added.setdefault(path, set()).add(number)
            number += 1
    return {name: frozenset(numbers) for name, numbers in added.items()}


def _comment_share_out_of_scope(rel_path: str) -> bool:
    return any(
        rel_path == prefix or rel_path.startswith(prefix + "/")
        for prefix in COMMENT_SHARE_OUT_OF_SCOPE
    )


def _in_scan_root(rel_path: str) -> bool:
    for scan_root in SCAN_ROOTS:
        if scan_root.direct_files_only:
            parent = PurePosixPath(rel_path).parent.as_posix()
            expected = scan_root.path or "."
            if parent == expected:
                return True
            continue
        if rel_path == scan_root.path or rel_path.startswith(scan_root.path + "/"):
            return True
    return False


def is_scanned_path(rel_path: str) -> bool:
    """Whether *rel_path* is in scope: a covered suffix under a covered root."""
    if language_for(rel_path) is None:
        return False
    if any(rel_path == exclusion.path for exclusion in SELF_EXCLUSION):
        return False
    parts = PurePosixPath(rel_path).parts
    if any(part in SKIP_DIRECTORY_NAMES for part in parts[:-1]):
        return False
    return _in_scan_root(rel_path)


def scan_paths(
    paths: Iterable[str],
    *,
    root: Path = REPO_ROOT,
    selector: str = "all",
    revision: str | None = None,
    table: ExceptionTable | None = None,
    changed: Mapping[str, Collection[int] | None] | None = None,
) -> ScanResult:
    """Scan an explicit list of repository-relative paths.

    *changed* maps a path to the added lines, or to None when the file is new.
    """
    table = table if table is not None else ExceptionTable()
    findings: list[Finding] = []
    shares: list[CommentShare] = []
    files_scanned = 0
    total_lines = 0
    comment_lines = 0
    unreadable: list[str] = []
    for rel_path in sorted({path for path in paths if is_scanned_path(path)}):
        language = language_for(rel_path)
        if language is None:  # pragma: no cover - is_scanned_path already filtered
            continue
        source = root / rel_path
        try:
            text = source.read_text(encoding="utf-8", errors="replace")
        except OSError:
            # A path git knows but the working tree does not have (a staged
            # deletion, say). Recorded rather than dropped: a scan that quietly
            # reads fewer files than it lists is the failure this gate exists to
            # avoid, so the count is visible in the report.
            unreadable.append(rel_path)
            continue
        changed_here = changed.get(rel_path, ()) if changed is not None else ()
        report = analyze_file(rel_path, text, language, changed_lines=changed_here)
        files_scanned += 1
        total_lines += report.lines
        comment_lines += report.comment_lines
        findings.extend(report.findings)
        if _comment_share_out_of_scope(rel_path):
            continue
        share = CommentShare(
            path=rel_path,
            lines=report.lines,
            comment_lines=report.comment_lines + report.docstring_lines,
            changed_lines=report.changed_lines,
            changed_comment_lines=report.changed_comment_lines,
        )
        shares.append(share)
        if share.changed_lines and share.changed_percent >= COMMENT_SHARE_MAX_PERCENT:
            anchor = 1 if changed_here is None else min(changed_here)
            findings.append(
                Finding(
                    path=rel_path,
                    line=anchor,
                    signal="comment_share",
                    severity=HARD,
                    text=(
                        f"{share.changed_percent:.1f}% comment and docstring in "
                        f"{share.changed_comment_lines} of {share.changed_lines} added lines"
                    ),
                )
            )

    kept, suppressed, unused = apply_exceptions(findings, table)
    return ScanResult(
        selector=selector,
        revision=revision,
        files_scanned=files_scanned,
        total_lines=total_lines,
        comment_lines=comment_lines,
        findings=tuple(sorted(kept, key=lambda f: (f.path, f.line, f.signal))),
        suppressed=tuple(sorted(suppressed, key=lambda f: (f.path, f.line, f.signal))),
        exceptions=table,
        unused_exceptions=unused,
        unreadable=tuple(unreadable),
        comment_share=tuple(shares),
    )


def scan_repository(
    *,
    selector: str = "all",
    revision: str | None = None,
    root: Path = REPO_ROOT,
    exceptions_path: Path | None = None,
) -> ScanResult:
    """Scan tracked source under *root*; the selector picks the file list.

    A blocked result carries the one-line reason and no findings. Blocking is
    reserved for the two conditions under which the file list itself is not
    knowable: no usable git, and a request that needs revision history.
    """
    if shutil.which("git") is None:
        return _blocked(selector, revision, "git is not available on PATH")
    probe = _git(["rev-parse", "--is-inside-work-tree"], root)
    if probe is None or probe.strip() != "true":
        return _blocked(selector, revision, f"{root} is not a git checkout")

    if selector == "changed":
        paths = _changed_source_paths(root, revision or "HEAD")
        if paths is None:
            return _blocked(
                selector, revision, f"git could not diff against {revision or 'HEAD'}"
            )
        changed = _changed_line_numbers(root, revision or "HEAD")
        if changed is None:
            return _blocked(
                selector,
                revision,
                f"git could not diff added lines against {revision or 'HEAD'}",
            )
        untracked = _untracked_paths(root)
        if untracked is None:
            return _blocked(selector, revision, "git ls-files --others failed")
        changed = changed | dict.fromkeys(untracked)
    else:
        paths = _tracked_source_paths(root)
        if paths is None:
            return _blocked(selector, revision, "git ls-files failed")
        changed = None

    config = exceptions_path if exceptions_path is not None else root / DEFAULT_EXCEPTIONS_PATH
    try:
        table = load_exceptions(config)
    except ValueError as error:
        return _blocked(selector, revision, f"exceptions file unreadable: {error}")
    return scan_paths(
        paths,
        root=root,
        selector=selector,
        revision=revision,
        table=table,
        changed=changed,
    )


def _blocked(selector: str, revision: str | None, reason: str) -> ScanResult:
    return ScanResult(
        selector=selector,
        revision=revision,
        files_scanned=0,
        total_lines=0,
        comment_lines=0,
        findings=(),
        suppressed=(),
        exceptions=ExceptionTable(),
        unused_exceptions=(),
        unreadable=(),
        blocked=reason,
    )


# --- reporting -------------------------------------------------------------

#: Every field of the stored document except the findings themselves. Keep the
#: key set stable: a report is a record, and a reader should not have to guess
#: which version of the schema it is looking at.
def to_document(result: ScanResult) -> dict[str, object]:
    return {
        "schema": SCHEMA_VERSION,
        "selector": result.selector,
        "revision": result.revision,
        "scan_roots": [scan_root.path or "." for scan_root in SCAN_ROOTS],
        "excluded_paths": [exclusion.path for exclusion in SELF_EXCLUSION],
        "thresholds": THRESHOLDS,
        "signals": [
            {"id": signal.id, "severity": signal.severity} for signal in SIGNALS
        ],
        "metrics": {
            "files_scanned": result.files_scanned,
            "total_lines": result.total_lines,
            "comment_lines": result.comment_lines,
            "hard_hits": len(result.hard_findings),
            "advisory_hits": len(result.advisory_findings),
            "suppressed_hits": len(result.suppressed),
            "unreadable_files": list(result.unreadable),
        },
        "per_signal": result.per_signal(),
        "per_signal_suppressed": result.per_signal_suppressed(),
        "comment_share": {
            "aggregate_percent": round(result.comment_share_percent, 2),
            "median_percent": result.comment_share_median,
            "out_of_scope": list(COMMENT_SHARE_OUT_OF_SCOPE),
            "files": [row.as_document() for row in result.comment_share],
        },
        "findings": [finding.as_document() for finding in result.findings],
        "suppressed": [finding.as_document() for finding in result.suppressed],
        "exceptions": {
            "applied": len(result.suppressed),
            "unused": [
                {"path": rule.path, "signal": rule.signal, "reason": rule.reason}
                for rule in result.unused_exceptions
            ],
            "invalid": list(result.exceptions.invalid),
        },
        "blocked": result.blocked,
    }


def to_json(result: ScanResult) -> str:
    """The stored document. Byte-identical for identical input: sorted keys, no
    timestamps, LF endings, trailing newline."""
    return json.dumps(to_document(result), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_summary(result: ScanResult) -> str:
    lines: list[str] = []
    lines.append(f"Webfoot source readability scan (schema {SCHEMA_VERSION})")
    if result.blocked is not None:
        lines.append(f"BLOCKED: {result.blocked}")
        return "\n".join(lines) + "\n"

    if result.selector == "changed":
        lines.append(f"selector: changed against {result.revision or 'HEAD'}")
    else:
        lines.append("selector: all")
    lines.append(
        f"scanned {result.files_scanned} files, {result.total_lines} lines, "
        f"{result.comment_lines} comment lines"
    )
    lines.append("")

    hard = sorted(result.hard_findings, key=lambda f: f.signal)
    advisories = sorted(result.advisory_findings, key=lambda f: f.signal)
    for signal in SIGNALS:
        group = [f for f in hard if f.signal == signal.id] if signal.severity == HARD else [
            f for f in advisories if f.signal == signal.id
        ]
        if not group:
            continue
        lines.append(f"{signal.severity.upper()}: {signal.id} ({len(group)}) - {signal.description}")
        for finding in sorted(group, key=lambda f: (f.path, f.line)):
            lines.append(f"  {finding.path}:{finding.line}  {_excerpt(finding.text)}")
        lines.append("")

    if result.exceptions.invalid:
        lines.append("rejected exception entries (not honoured):")
        for entry in result.exceptions.invalid:
            lines.append(f"  {entry}")
        lines.append("")
    if result.unused_exceptions:
        lines.append("exceptions that matched nothing (prune them):")
        for rule in result.unused_exceptions:
            lines.append(f"  {rule.path} [{rule.signal}]")
        lines.append("")

    lines.append("per-signal counts")
    counts = result.per_signal()
    suppressed = result.per_signal_suppressed()
    for signal in SIGNALS:
        lines.append(
            f"  {signal.id:<28} {signal.severity:<8} {counts[signal.id]:>4}"
            + (f"   suppressed {suppressed[signal.id]}" if suppressed[signal.id] else "")
        )
    lines.append("")

    lines.append(
        f"comment share (C1: under {COMMENT_SHARE_MAX_PERCENT:.0f}% of the lines a change "
        f"adds, median at or below {COMMENT_SHARE_MEDIAN_MAX_PERCENT:.0f}%)"
    )
    for row in result.comment_share:
        detail = f"  {row.path}  {row.comment_lines} of {row.lines} lines ({row.percent:.1f}%)"
        if row.changed_lines:
            detail += (
                f"   added {row.changed_comment_lines} of {row.changed_lines} "
                f"({row.changed_percent:.1f}%)"
            )
        lines.append(detail)
    lines.append(
        f"  aggregate ................... {result.comment_share_percent:.1f}% comment and docstring"
    )
    median = result.comment_share_median
    lines.append(
        "  added-lines median .......... "
        + ("not measured" if median is None else f"{median:.1f}%")
    )
    for prefix in COMMENT_SHARE_OUT_OF_SCOPE:
        lines.append(f"  out of scope ................ {prefix}, which the SDK rewrite replaces")
    lines.append("")

    lines.append("trends (counts only, not a score)")
    lines.append(f"  files scanned ......... {result.files_scanned}")
    lines.append(f"  total lines ........... {result.total_lines}")
    lines.append(f"  comment lines ......... {result.comment_lines}")
    lines.append(f"  hard hits ............. {len(result.hard_findings)}")
    lines.append(f"  advisory hits ......... {len(result.advisory_findings)}")
    lines.append(f"  suppressed ............ {len(result.suppressed)}")
    lines.append("")
    lines.append("Advisories are a reading list and never change the exit code.")
    return "\n".join(lines) + "\n"


# --- command line ----------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.quality.readability",
        description=(
            "Report readability and residue observations over the repository's "
            "public source files. Nothing is executed and nothing is scored."
        ),
    )
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument(
        "--all",
        action="store_true",
        help="Scan the whole configured source tree (default).",
    )
    selector.add_argument(
        "--changed",
        nargs="?",
        const="HEAD",
        default=None,
        metavar="REV",
        help=(
            "Scan files changed against REV (default HEAD), including untracked "
            "but not ignored source files."
        ),
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        default=None,
        metavar="PATH",
        help="Write the full report document as JSON to PATH, and still print the summary.",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Report hard findings but always exit 0.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    selector = "changed" if args.changed is not None else "all"
    result = scan_repository(selector=selector, revision=args.changed)

    if result.blocked is not None:
        print(f"BLOCKED: {result.blocked}")
        return 2

    document = to_json(result)
    if args.json_path:
        Path(args.json_path).write_text(document, encoding="utf-8", newline="\n")
    sys.stdout.write(render_summary(result))

    if args.no_fail:
        return 0
    if result.hard_findings:
        return 1
    median = result.comment_share_median
    return 1 if median is not None and median > COMMENT_SHARE_MEDIAN_MAX_PERCENT else 0


if __name__ == "__main__":  # pragma: no cover - exercised through main()
    raise SystemExit(main())
