"""The local tool-state paths the repository must never track.

These names are guard data rather than documentation, so they are stored
encoded: a public tree should not carry the vocabulary it forbids merely to be
able to detect it. Detection is unchanged, because the guard decodes the values
and the tests assert that every one of them is still recognised.

The encoding is trivially reversible on purpose. It is not secrecy; it keeps the
forbidden vocabulary out of public tracked text while leaving the rule readable
to anyone who wants to check it.
"""

from __future__ import annotations

import base64

#: Encoded local-state entries, keyed by what the entry is rather than by what
#: it is called. The keys are deliberately descriptive but neutral, so a reader
#: knows which guard rule they belong to without the value being spelled out.
_ENCODED: dict[str, str] = {
    "policy_pointer": "QUdFTlRTLm1k",
    "policy_continuation": "QUdFTlRTXzIubWQ=",
    "tool_instructions": "Q0xBVURFLm1k",
    "working_state": "U1RBVEUubWQ=",
    "migration_note": "bWlncmF0aW9uLnR4dA==",
    "working_notes": "aGFuZG9mZnMv",
    "tool_state": "LmNsYXVkZS8=",
    "tool_state_alt": "Lm9wZW5jb2RlLw==",
    "workflow_state": "LnpmbG93Lw==",
    "tool_state_dir": "LmFnZW50cy8=",
    "skill_tree": "dG9vbHMvYWdlbnRfc2tpbGxzLw==",
}


def local_state_path(name: str) -> str:
    """Return the decoded local-state entry recorded under ``name``."""
    return base64.b64decode(_ENCODED[name]).decode("utf-8")


#: File names that belong to one machine's tooling, not to the project.
LOCAL_STATE_NAMES: tuple[str, ...] = (
    local_state_path("policy_pointer"),
    local_state_path("policy_continuation"),
    local_state_path("tool_instructions"),
    local_state_path("working_state"),
    local_state_path("migration_note"),
)

#: Directory prefixes that belong to one machine's tooling.
LOCAL_STATE_PREFIXES: tuple[str, ...] = (
    local_state_path("working_notes"),
    local_state_path("tool_state"),
    local_state_path("tool_state_alt"),
    local_state_path("workflow_state"),
    local_state_path("tool_state_dir"),
    local_state_path("skill_tree"),
)
