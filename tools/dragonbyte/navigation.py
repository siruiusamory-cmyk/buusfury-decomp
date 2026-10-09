"""Back and forward over destinations, in memory, bounded.

Navigation is not edit undo and holds no edit concept at all: an entry names
where the user was, and moving the cursor changes no data. The list is capped so
a long session cannot grow without bound, and the cap drops the OLDEST entry,
because the most recent places are the ones a user is working between.

No Qt here. A test drives the whole model with no window open.
"""

from __future__ import annotations

from dataclasses import dataclass

#: How many visited destinations are kept. The oldest is dropped past this.
MAX_HISTORY = 100


@dataclass(frozen=True, slots=True)
class NavEntry:
    """One visited place. A destination id is the whole of it for now."""

    destination: str


class NavigationHistory:
    """A bounded back/forward list with one cursor.

    ``push`` records a new visit and drops the forward tail, because the user
    has taken a different branch. ``back`` and ``forward`` only move the cursor:
    neither creates an entry, and neither does anything at the end of its tail.
    """

    def __init__(self, destination: str | None = None) -> None:
        self._entries: list[NavEntry] = []
        self._cursor = -1
        if destination is not None:
            self.push(destination)

    @property
    def current(self) -> NavEntry | None:
        """The entry the cursor is on, or None when nothing was ever visited."""
        if self._cursor < 0:
            return None
        return self._entries[self._cursor]

    def push(self, destination: str) -> None:
        """Record a visit to ``destination``.

        Pushing the destination that is already current is a no-op, so repeated
        selection does not fill the history with one place.
        """
        current = self.current
        if current is not None and current.destination == destination:
            return
        del self._entries[self._cursor + 1 :]
        self._entries.append(NavEntry(destination))
        self._cursor = len(self._entries) - 1
        if len(self._entries) > MAX_HISTORY:
            del self._entries[0]
            self._cursor -= 1

    def back(self) -> NavEntry | None:
        """Step one entry towards the oldest, or None at that end."""
        if self._cursor <= 0:
            return None
        self._cursor -= 1
        return self.current

    def forward(self) -> NavEntry | None:
        """Step one entry towards the newest, or None at that end."""
        if self._cursor < 0 or self._cursor >= len(self._entries) - 1:
            return None
        self._cursor += 1
        return self.current

    @property
    def can_go_back(self) -> bool:
        return self._cursor > 0

    @property
    def can_go_forward(self) -> bool:
        return 0 <= self._cursor < len(self._entries) - 1

    def __len__(self) -> int:
        return len(self._entries)
