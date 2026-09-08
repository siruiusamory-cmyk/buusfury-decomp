"""Shared, read-only placement descriptors and proven script attachments.

Identity follows first semantic consumer, never address sorting. Numeric addresses
are provenance. Only trusted profile metadata can promote descriptor payloads.
"""
from dataclasses import dataclass

from .binary import FileOffset, GbaRomAddress
from .data.placement_contracts import CONTRACTS
from .formats.map_placements import DescriptorRecord, HANDLERS, SCRIPT_DISPATCH_HANDLER
from .formats import placement_links as links
from .formats.script_vm import Entry, disassemble, assemble, ScriptError
from .layout import Anchor, AnchorId, Provenance, Reference, ReferenceClass, ReferenceEncoding, RomRange
from .write import ByteChange

FAMILY = 'placement_descriptor_event'


@dataclass(frozen=True)
class Descriptor:
    identity: str
    record: DescriptorRecord
    file_offset: int
    placements: tuple[str, ...]
    event: str | None


@dataclass(frozen=True)
class Event:
    identity: str
    file_offset: int
    original_bytes: bytes


class PlacementEvents:
    def __init__(self, maps):
        self.maps = maps
        contract = CONTRACTS.get(maps.profile.id)
        if contract is None or contract['sha256'] != maps.identification.hashes.sha256:
            raise ScriptError('no verified placement descriptor contract for this profile')
        self.contract = contract
        image = maps.base_bytes
        groups = {}
        for p in maps.placements():
            groups.setdefault(p.record.descriptor_pointer_raw, []).append(str(p.identity))
            for child in p.record.child_pointers_raw:
                GbaRomAddress(child).to_file_offset(len(image))
        if set(groups) != set(contract['descriptors']):
            raise ScriptError('descriptor pointer outside declared ownership provenance')
        roots = dict(contract['roots'])
        owned = set(contract['owned_descriptors'])
        events = {}
        descriptors = []
        for pointer, consumers in sorted(groups.items(), key=lambda pair: pair[1][0]):
            offset, record = links.descriptor_at(image, pointer)
            if record.handler_pointer_raw not in HANDLERS:
                raise ScriptError('descriptor has an unverified handler')
            key = consumers[0] + '/descriptor'
            event = None
            if record.handler_pointer_raw == SCRIPT_DISPATCH_HANDLER:
                if pointer not in owned or record.payload_raw not in roots:
                    raise ScriptError('script attachment outside verified owned subset')
                if record.payload_raw not in events:
                    start, raw = links.root_at(image, record.payload_raw, roots[record.payload_raw])
                    events[record.payload_raw] = Event(key + '/event', start, raw)
                event = events[record.payload_raw].identity
            elif pointer in owned:
                raise ScriptError('owned descriptor no longer dispatches script')
            descriptors.append(Descriptor(key, record, offset, tuple(consumers), event))
        if set(events) != set(roots):
            raise ScriptError('owned script roots differ from trusted subset')
        self.descriptors = tuple(descriptors)
        self.events = tuple(events.values())
        self._placement = {p: d for d in descriptors for p in d.placements}

    def descriptor_of(self, placement):
        try:
            return self._placement[str(placement)]
        except KeyError:
            raise ScriptError(f'unknown owned placement {placement}') from None

    def events_for_map(self, identity):
        return tuple(sorted({self.descriptor_of(p.identity).event
                             for p in self.maps.map_placements(identity)
                             if self.descriptor_of(p.identity).event is not None}))

    def corpus(self):
        from .scripts import Attachment, ScriptCorpus, ScriptSegment, OPCODE_SETS
        spec = OPCODE_SETS[self.contract['encoding']]
        if self.maps.profile.id not in spec.profiles:
            raise ScriptError('VM is not verified for this profile')
        entries, segments = [], []
        raw = b''
        for e in self.events:
            # Each root is independently bounded before combining virtual IR.
            ir = disassemble(e.original_bytes, (Entry(e.identity, 0),), spec)
            if ir.opaque or assemble(ir) != e.original_bytes:
                raise ScriptError('owned script extent does not round-trip')
            entries.append(Entry(e.identity, len(raw)))
            segments.append(ScriptSegment(e.identity, len(raw), e.file_offset, len(e.original_bytes)))
            raw += e.original_bytes
        ir = disassemble(raw, tuple(entries), spec)
        if ir.opaque or assemble(ir) != raw:
            raise ScriptError('owned script corpus does not round-trip')
        attachments = tuple(Attachment(d.identity, d.event, 'placement_descriptor', (),
                                       self.contract['evidence'])
                            for d in self.descriptors if d.event is not None)
        return ScriptCorpus(self.maps.profile.id, None, ir, FAMILY, attachments, tuple(segments))

    def project_document(self):
        corpus = self.corpus()
        return {
            'schema': 1,
            'family': FAMILY,
            'descriptors': {d.identity: {
                'handler': HANDLERS[d.record.handler_pointer_raw],
                'handler_pointer_raw': d.record.handler_pointer_raw,
                'payload_raw': d.record.payload_raw,
                'placements': list(d.placements),
                'event': d.event or '',
            } for d in self.descriptors},
            'events': {e.identity: {'raw': e.original_bytes.hex(),
                                   'extent': len(e.original_bytes)} for e in self.events},
            'instruction_count': corpus.instruction_count,
        }

    def changes(self):
        # Decode/encode every represented byte on normal build, without edits.
        self.corpus()
        return tuple([ByteChange(d.file_offset, d.record.to_bytes(), d.record.to_bytes(),
                                 d.identity, 'descriptor unchanged') for d in self.descriptors] +
                     [ByteChange(e.file_offset, e.original_bytes, e.original_bytes,
                                 e.identity, 'owned event unchanged') for e in self.events])

    def extend_references(self, document):
        """Extend the existing common graph; shared objects get one anchor each."""
        from .document import RomDocument
        anchors, refs = list(document.anchors), list(document.references)
        prov = Provenance(self.maps.profile.id, self.maps.profile.sha256, self.contract['evidence'] + '; ' + self.contract['native_evidence'])
        def anchor(key, offset, size, kind, alignment=1):
            anchors.append(Anchor(AnchorId(key), RomRange(FileOffset(offset), size),
                                  kind, key, alignment, False, prov))
        def ref(offset, target, delta=0):
            refs.append(Reference(FileOffset(offset), AnchorId(target), delta,
                                  ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                                  ReferenceClass.CONFIRMED_REFERENCE, prov))
        for raw, key in sorted(HANDLERS.items()):
            anchor(key, links.thumb_fetch(document.image, raw), 2,
                   'thumb_entry', 2)
        for d in self.descriptors:
            anchor(d.identity, d.file_offset, 8, 'placement_descriptor', 4)
            ref(d.file_offset, HANDLERS[d.record.handler_pointer_raw], 1)
            if d.event:
                ref(links.payload_source(d.file_offset), d.event)
        for e in self.events:
            anchor(e.identity, e.file_offset, len(e.original_bytes), FAMILY)
        for p in self.maps.placements():
            ref(links.descriptor_source(p.file_offset), self.descriptor_of(p.identity).identity)
        # Verified native-dispatch operands index slots; slots store raw Thumb
        # pointers. Neither the index nor the target receives gameplay meaning.
        corpus = self.corpus()
        slots, handlers = {}, {}
        for call in links.native_bindings(document.image, corpus.ir, corpus.segments,
                                         self.contract['native_table'], self.contract['native_opcodes']):
            key = f'native_dispatch:{call.index:04d}'
            if call.index not in slots:
                if call.handler_raw not in handlers:
                    handlers[call.handler_raw] = key + '/handler'
                    anchor(handlers[call.handler_raw], call.handler_fetch, 2, 'thumb_entry', 2)
                slots[call.index] = key
                anchor(key, call.slot, 4, 'native_dispatch_slot', 4)
                ref(call.slot, handlers[call.handler_raw], 1)
            refs.append(Reference(FileOffset(call.source), AnchorId(key), 0,
                                  ReferenceEncoding.INDEX_U8, ReferenceClass.CONFIRMED_REFERENCE,
                                  prov, FileOffset(call.table), 4))
        return RomDocument.from_bytes(document.image, document.profile,
                                      anchors=tuple(anchors), references=tuple(refs))
