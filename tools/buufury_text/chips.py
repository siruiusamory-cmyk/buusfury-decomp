"""Dialogue text whose control units survive as single atoms.

The canonical value is the Python string `ChipTextEdit.serialized()` returns. The
QTextDocument is a presentation projection of that string and never the source of
truth, so an edit Qt made on its own is recomputed from the string, checked with
`protected_edit`, and the document is rebuilt from the allowed result.

A control unit is one atom. `protected_edit` is the rule behind every edit route -
keystrokes, paste, drop and cut - and the caret never enters an atom, so the chip's
appearance is never the only thing saying that the unit is locked.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSizeF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QPyTextObject,
    QTextCharFormat,
    QTextCursor,
    QTextFormat,
    QTextOption,
)
from PySide6.QtWidgets import QApplication, QTextEdit

from tools.webfoot import textedit

from . import theme

#: The object-replacement character stands in for one control unit.
ATOM = "\ufffc"
#: The object type the document layout routes to ChipObject.
OBJECT_TYPE = QTextFormat.ObjectTypes.UserObject + 1
_CHAR_PROPERTY = QTextFormat.Property.UserProperty + 1


def atom_ranges(text: str) -> tuple[tuple[int, int], ...]:
    """The (start, end) character span of every control unit in `text`."""
    ranges: list[tuple[int, int]] = []
    at = 0
    for unit in textedit.units(text):
        raw = _raw(unit)
        if isinstance(unit, textedit.Control):
            ranges.append((at, at + len(raw)))
        at += len(raw)
    return tuple(ranges)


def protected_edit(current: str, position: int, removed: int, inserted: str) -> str:
    """What the text becomes when a user edits it, with every atom intact.

    `position` and `removed` describe the edit as Qt reports it: replace
    `current[position:position + removed]` with `inserted`.

    Refused: a removal that crosses any part of an atom, a removal that contains a
    whole atom, an insertion strictly inside an atom, an insertion that itself
    carries a control unit, and a lone high surrogate. Every refusal returns
    `current` unchanged.
    """
    if removed > 0:
        end = min(len(current), position + removed)
        for start, stop in atom_ranges(current):
            if start < end and position < stop:
                return current
            if position <= start and stop <= end:
                return current
    elif position in _inside(current):
        return current
    elif any(start == position for start, _ in atom_ranges(current)):
        return current
    if any(isinstance(unit, textedit.Control) for unit in textedit.units(inserted)):
        return current
    result = current[:position] + inserted + current[position + removed:]
    if _lone_high_surrogate(result):
        return current
    return result


def _inside(text: str) -> frozenset[int]:
    """The interior positions of every atom: an insertion there would split it."""
    return frozenset(
        at
        for start, stop in atom_ranges(text)
        for at in range(start + 1, stop)
    )


def control_label(unit: str) -> str:
    """The readable form of one control unit.

    The RE Lab's control-code catalogue will name these; every label routes
    through this one function so that catalogue replaces it in one place.
    """
    if not unit:
        return ""
    code = ord(unit[0])
    if code == 0x0A:
        return "\u21b5"
    if code == 0x08 and len(unit) > 1:
        return f"{{08:{ord(unit[1]):02X}}}"
    return f"{code:04X}"


class ChipObject(QPyTextObject):
    """Paints one control unit: the data role, a 1 px control border, 3 px radius.

    The chip is the raised surface with the control border, which keeps it legible
    against both the editor surface and the selection without a second fill token.
    """

    def intrinsicSize(self, doc, fmt, _=None) -> QSizeF:  # noqa: N802
        label = control_label(str(fmt.property(_CHAR_PROPERTY)))
        metrics = theme.active_metrics()
        device = doc.documentLayout().paintDevice()
        width = device.fontMetrics().horizontalAdvance(label) if device is not None else 0
        return QSizeF(width + 2 * metrics.pad_sm, metrics.chip_height)

    def drawObject(self, painter, rect, doc, fmt):  # noqa: N802
        label = control_label(str(fmt.property(_CHAR_PROPERTY)))
        active = theme.active_theme()
        metrics = theme.active_metrics()
        painter.save()
        painter.setRenderHint(painter.RenderHint.Antialiasing, True)
        chip = QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5)
        painter.setBrush(QColor(active.surface_raised))
        painter.setPen(QColor(active.border))
        painter.drawRoundedRect(chip, metrics.radius, metrics.radius)
        painter.setFont(theme.type_scale().data)
        painter.setPen(QColor(active.text_primary))
        painter.drawText(QRectF(chip), Qt.AlignmentFlag.AlignCenter, label)
        painter.restore()


class ChipTextEdit(QTextEdit):
    """A QTextEdit that refuses every edit which would split an atom."""

    edited = Signal(str)

    def __init__(self, parent=None, editable: bool = True) -> None:
        super().__init__(parent)
        self.setReadOnly(not editable)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.setFont(theme.type_scale().data)
        # The layout holds the handler weakly; the widget has to keep it alive.
        self._object_handler = ChipObject()
        self.document().documentLayout().registerHandler(OBJECT_TYPE, self._object_handler)
        self._serialized = ""
        self._rebuilding = False
        self.document().contentsChange.connect(self._on_contents_change)

    # --- the canonical value -------------------------------------------------

    def set_text(self, text: str) -> None:
        """Rebuild the document from the canonical string. Read-only shows reference text."""
        self._rebuilding = True
        try:
            self._serialized = text
            self.document().clear()
            cursor = QTextCursor(self.document())
            cursor.beginEditBlock()
            for unit in textedit.units(text):
                is_atom = isinstance(unit, textedit.Control)
                cursor.insertText(ATOM if is_atom else _raw(unit),
                                  _format_for(unit.raw) if is_atom else QTextCharFormat())
            cursor.endEditBlock()
            self.setTextCursor(QTextCursor(self.document()))
        finally:
            self._rebuilding = False

    def serialized(self) -> str:
        return self._serialized

    def atom_count(self) -> int:
        return len(atom_ranges(self._serialized))

    # --- every route into the document --------------------------------------

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if not self.isReadOnly() and event.key() in (
                Qt.Key.Key_Backspace, Qt.Key.Key_Delete) and self._touches_atom():
            event.accept()
            return
        super().keyPressEvent(event)

    def canInsertFromMimeData(self, source) -> bool:  # noqa: N802
        return super().canInsertFromMimeData(source) and not _carries_atom(source)

    def insertFromMimeData(self, source) -> None:  # noqa: N802
        if self.isReadOnly() or not source.hasText():
            return
        cursor = self.textCursor()
        self._apply(cursor.selectionStart(), len(cursor.selectedText()), source.text())

    def paste(self) -> None:  # noqa: N802
        if not self.isReadOnly():
            self.insertFromMimeData(QApplication.clipboard().mimeData())

    def cut(self) -> None:  # noqa: N802
        if not self.isReadOnly() and not self._touches_atom():
            super().cut()

    def dropEvent(self, event) -> None:  # noqa: N802
        if self.isReadOnly() or _carries_atom(event.mimeData()):
            event.ignore()
            return
        super().dropEvent(event)

    # --- internals -----------------------------------------------------------

    def _touches_atom(self) -> bool:
        cursor = self.textCursor()
        position, removed = cursor.selectionStart(), len(cursor.selectedText())
        if removed == 0:
            position, removed = cursor.position(), 1
        return protected_edit(self._serialized, position, removed, "") == self._serialized

    def _apply(self, position: int, removed: int, inserted: str) -> None:
        result = protected_edit(self._serialized, position, removed, inserted)
        if result == self._serialized:
            return
        self._reload(result, min(len(result), position + len(inserted)))
        self.edited.emit(result)

    def _reload(self, text: str, caret: int) -> None:
        self.set_text(text)
        cursor = QTextCursor(self.document())
        cursor.setPosition(min(caret, len(text)))
        self.setTextCursor(cursor)

    def _on_contents_change(self, position: int, removed: int, added: int) -> None:
        """An edit the widget did not route itself: keep it only if it is allowed.

        Qt has already changed the document by the time this arrives, so the
        allowed value is recomputed from the canonical string and the document is
        left alone when it already reads that way.
        """
        if self.isReadOnly() or self._rebuilding:
            return
        inserted = _paragraphs(self._inserted(added))
        result = protected_edit(self._serialized, position, removed, inserted)
        if result == self._serialized:
            if added or removed:
                self._reload(self._serialized, position + len(inserted))
            return
        self._serialized = result
        if self.document().toPlainText() != _presentation(result):
            self._reload(result, position + len(inserted))
        self.edited.emit(result)

    def _inserted(self, added: int) -> str:
        """The characters an unattributed edit added, read back from the document."""
        if not added:
            return ""
        cursor = self.textCursor()
        end = max(0, cursor.position())
        cursor.setPosition(max(0, end - added))
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        return cursor.selectedText()


def _format_for(raw: str) -> QTextCharFormat:
    fmt = QTextCharFormat()
    fmt.setObjectType(OBJECT_TYPE)
    fmt.setProperty(_CHAR_PROPERTY, raw)
    return fmt


def _presentation(text: str) -> str:
    return "".join(ATOM if isinstance(unit, textedit.Control) else _raw(unit)
                   for unit in textedit.units(text))


def _raw(unit) -> str:
    """The characters one unit occupies: a Control's raw unit(s), a Text's value."""
    return unit.raw if isinstance(unit, textedit.Control) else unit.value


def _paragraphs(text: str) -> str:
    """QTextCursor reports a paragraph break as U+2029; the value keeps it as 0x0A."""
    return text.replace("\u2029", "\n")


def _carries_atom(source) -> bool:
    if source is None or not source.hasText():
        return False
    return any(isinstance(unit, textedit.Control) for unit in textedit.units(source.text()))


def _lone_high_surrogate(text: str) -> bool:
    return any(
        ord(character) in range(0xD800, 0xDC00)
        and (at + 1 >= len(text) or not 0xDC00 <= ord(text[at + 1]) <= 0xDFFF)
        for at, character in enumerate(text)
    )
