"""The deterministic partition of the portable suite into parallel shards.

The GitHub workflow runs the whole of ``tests/unit`` as ten parallel jobs, so
every collected node has to land in exactly one of them, in every process that
computes the answer. That is the whole contract here: the key is the node's own
identifier and nothing else, so there is no ``hash()`` (which is randomised per
process), no working directory, no case folding and no randomness.

The partition is by NODE, not by file. A file-keyed partition cannot meet the
wall-clock target: ``--dist loadfile`` keeps every node of one file on one worker,
the heaviest file measured 783 s of test time, and a shard that received it would
carry that alone. A node key spreads one heavy file across all ten shards.

Two environment variables name the shard this process should run: ``count`` is the
number of shards, ``index`` this one. Both unset means no sharding at all, which
is the single-process arrangement the local full-CI record uses.
"""

from __future__ import annotations

from collections.abc import Iterable
import hashlib
import os
from pathlib import PureWindowsPath

#: The number of shards this process is one of.
SHARD_COUNT_VARIABLE = "WEBFOOT_SHARD_COUNT"

#: Which of them this process is.
SHARD_INDEX_VARIABLE = "WEBFOOT_SHARD_INDEX"


def node_identifier(path: str, name: str) -> str:
    """One collected node as ``<repo-relative path with forward slashes>::<name>``.

    The separator is normalised rather than the case: two spellings of the same
    path must not land in two shards, and two nodes differing only in case are
    two different nodes.
    """
    return f"{PureWindowsPath(str(path)).as_posix()}::{name}"


def shard_of(identifier: str, count: int) -> int:
    """The shard ``identifier`` belongs to, out of ``count``.

    The digest is taken over the identifier alone, so two processes that see the
    same node compute the same shard without sharing any state.
    """
    digest = hashlib.sha256(identifier.encode("utf-8")).hexdigest()
    return int(digest, 16) % count


def partition(identifiers: Iterable[str], count: int) -> dict[int, list[str]]:
    """Every identifier, once, keyed by the shard that owns it.

    Every shard key is present even when it owns nothing, so a caller can tell an
    empty shard from a missing one.
    """
    shards: dict[int, list[str]] = {index: [] for index in range(count)}
    for identifier in identifiers:
        shards[shard_of(identifier, count)].append(identifier)
    return shards


def selection_from_environment() -> tuple[int, int] | None:
    """``(count, index)`` for this process, or None when neither variable is set.

    A half-configured or malformed selection raises rather than returning
    something a caller could read as "run everything", because a misconfigured
    shard that silently runs the whole suite, or nothing at all, would make a red
    run look green.
    """
    raw_count = os.environ.get(SHARD_COUNT_VARIABLE)
    raw_index = os.environ.get(SHARD_INDEX_VARIABLE)
    if raw_count is None and raw_index is None:
        return None
    if raw_count is None or raw_index is None:
        raise RuntimeError(
            f"sharding needs both {SHARD_COUNT_VARIABLE} and "
            f"{SHARD_INDEX_VARIABLE}; found {SHARD_COUNT_VARIABLE}={raw_count!r} "
            f"and {SHARD_INDEX_VARIABLE}={raw_index!r}"
        )
    count = _whole_number(raw_count, SHARD_COUNT_VARIABLE)
    index = _whole_number(raw_index, SHARD_INDEX_VARIABLE)
    if count < 1:
        raise RuntimeError(f"{SHARD_COUNT_VARIABLE} must be at least 1, got {count}")
    if not 0 <= index < count:
        raise RuntimeError(
            f"{SHARD_INDEX_VARIABLE} must satisfy 0 <= index < {count}, got {index}"
        )
    return count, index


def _whole_number(raw: str, variable: str) -> int:
    """The integer ``raw`` names, or a refusal naming the variable that is wrong."""
    try:
        return int(raw)
    except ValueError:
        raise RuntimeError(
            f"{variable} must be an integer, got {raw!r}"
        ) from None
