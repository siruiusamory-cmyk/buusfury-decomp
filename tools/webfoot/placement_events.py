"""Shared, read-only placement descriptors and proven script attachments.

Identity follows first semantic consumer, never address sorting. Numeric addresses
are provenance. Only trusted profile metadata can promote descriptor payloads.
"""
from dataclasses import dataclass

from .binary import FileOffset, GbaRomAddress
from .data.placement_contracts import CONTRACTS
from .formats.map_placements import DescriptorRecord, HANDLERS, SCRIPT_DISPATCH_HANDLER
from .formats import placement_links as links
from .data.script_specs import OPCODE_SETS
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
        #: TOOLKIT-025: the verified event contract is a proven SUBSET of the canonical
        #: descriptor universe, not an exhaustive census of it. The corrected
        #: engine-counted placement census (1,559 records) reaches 131 descriptors; the
        #: contract declares 82. The 49 additional descriptors all carry handlers this
        #: codec already verifies - 42 `0x0800424F` and 7 `0x0800421F` - so no unknown
        #: family appears, but seven of them point at script roots whose extents were
        #: never established under the VM evidence contract. Those seven are therefore
        #: NOT admitted to the decoded event corpus here; they are canonical structure
        #: whose decoded event membership is not yet evidenced.
        #:
        #: This stays an exact check in the direction that carries the evidence: every
        #: declared descriptor must still be present and still be reached by a canonical
        #: placement. A declared descriptor disappearing, or moving, still fails.
        missing = set(contract['descriptors']) - set(groups)
        if missing:
            raise ScriptError('declared descriptor is unreachable from canonical placements')
        roots = dict(contract['roots'])
        owned = set(contract['owned_descriptors'])
        declared = set(contract['descriptors'])
        events = {}
        descriptors = []
        for pointer, consumers in sorted(groups.items(), key=lambda pair: pair[1][0]):
            offset, record = links.descriptor_at(image, pointer)
            if record.handler_pointer_raw not in HANDLERS:
                raise ScriptError('descriptor has an unverified handler')
            key = consumers[0] + '/descriptor'
            event = None
            #: TOOLKIT-025: a descriptor outside the verified event contract is carried
            #: STRUCTURALLY - it gets an identity and a handler reference, so the
            #: placement->descriptor edge exists for all 1,559 canonical placements -
            #: but it is never decoded into an event. Seven of these use the verified
            #: `0x0800421F` script-dispatch handler and point at seven script roots
            #: whose extents were never established under the VM evidence contract;
            #: admitting them here would promote undecoded roots into the event corpus
            #: on reachability alone, which is not evidence. They stay out until a root
            #: extent is actually established.
            if record.handler_pointer_raw == SCRIPT_DISPATCH_HANDLER and pointer in declared:
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

    def operand_references(self):
        """Operands proven to select a stable resource; see TOOLKIT-018.

        No map-scene event reference to text is emitted. The strongest text
        candidates were traced to their consumers and refuted, so a numeric
        resemblance to the text table can never produce an edge here.
        Gameplay semantics of both resource classes remain UNKNOWN.
        """
        corpus = self.corpus()
        return links.operand_references(corpus.ir, corpus.segments,
                                        self.contract['event_resource'],
                                        self.contract['save_flag'])

    def resource_records(self):
        """Every event-resource record, tiled exactly from the pointer table."""
        return links.event_resource_records(self.maps.base_bytes,
                                            self.contract['event_resource'])

    def resource_show(self, index):
        """Structural view of one record, plus its code block when readable.

        Gameplay meaning stays UNKNOWN. The engine's own assertion string calls
        these dialogs, so the field is named for the branch the consumer takes,
        not for anything observed on screen.
        """
        records = self.resource_records()
        if not 0 <= int(index) < len(records):
            raise ScriptError(f'unknown event resource index {index}')
        record = records[int(index)]
        spec = OPCODE_SETS[self.contract['encoding']]
        block = links.dialog_code_block(self.maps.base_bytes, record, spec)
        view = {'identity': f'event_resource:{record.index:04d}',
                'slot_file_offset': record.slot_offset,
                'record_file_offset': record.start,
                'record_end_file_offset': record.end,
                'record_size': record.size,
                'dialog_file_offset': record.dialog_offset,
                'dialog_type': record.dialog_type,
                'supported': record.supported}
        if block is not None:
            start, raw, ir = block
            view['code_file_offset'] = start
            view['code_size'] = len(raw)
            view['instructions'] = sum(len(b.instructions) for b in ir.blocks)
        return view

    def dialog_text_references(self, index=None):
        """Text-table indices the supported dialogs prove they render.

        TOOLKIT-020. Slot 178 is the only one of the 107 native slots this
        corpus uses whose call graph reaches the verified text pointer table,
        and it reaches it at depth 1. Dialogs whose index is computed at
        runtime rather than pushed as a literal produce nothing here.

        This is a new relation, not a reversal: TOOLKIT-018's refutation
        concerned three map-scene *event* consumer families, none of them this
        native slot.
        """
        contract = self.contract.get('dialog_text')
        if contract is None:
            return ()
        spec = OPCODE_SETS[self.contract['encoding']]
        records = self.resource_records()
        if index is not None:
            if not 0 <= int(index) < len(records):
                raise ScriptError(f'unknown event resource index {index}')
            records = [records[int(index)]]
        found = []
        for record in records:
            found.extend(links.dialog_text_references(
                self.maps.base_bytes, record, spec, contract))
        return tuple(found)

    def dialogs_for_text(self, index):
        """Reverse traversal: which dialogs render this text entry.

        Kept separate from TOOLKIT-014's item->text consumers. Both reach the
        same table through distinct provenance paths and are not merged.
        """
        return tuple(sorted({r.dialog for r in self.dialog_text_references()
                             if r.index == int(index)}))

    def consumers_of(self, kind, index):
        """Reverse traversal: which events, placements and maps reach a resource."""
        events = tuple(sorted({r.event for r in self.operand_references()
                               if r.kind == kind and r.index == int(index)}))
        placements = tuple(sorted({p for d in self.descriptors
                                   if d.event in events for p in d.placements}))
        return {'events': events, 'placements': placements,
                'maps': tuple(sorted({p.split('/')[0] for p in placements}))}

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
            # Supplemental and derived: the raw event bytes above stay
            # authoritative. Several references per event are preserved
            # individually, keyed by instruction provenance, never collapsed
            # into one field per event.
            'operand_references': [{
                'kind': r.kind,
                'event': r.event,
                'block': r.block,
                'ir_offset': r.ir_offset,
                'source': r.source,
                'encoded_length': r.encoded_length,
                'index': r.index,
                'access': r.access,
            } for r in self.operand_references()],
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
        # TOOLKIT-018. Each referenced resource slot is a real, protectable ROM
        # object, so it earns an anchor, named structurally because the record's
        # meaning is UNKNOWN. A save flag gets no anchor: it lives in a runtime
        # bitfield, not in the ROM. The operand edges themselves are NOT graph
        # references either - an operand is a variable-width big-endian
        # signed-magnitude varint, while every ReferenceEncoding is fixed-width
        # little-endian, so the graph could not decode the field back. Those
        # edges live in operand_references(), which keeps exact provenance.
        resource = self.contract['event_resource']
        table = GbaRomAddress(resource['table']).to_file_offset(len(document.image))
        for index in sorted({r.index for r in self.operand_references()
                             if r.kind == 'event_resource'}):
            anchor(f'event_resource:{index:04d}', table + 4 * index, 4,
                   'event_resource_slot', 4)
        return RomDocument.from_bytes(document.image, document.profile,
                                      anchors=tuple(anchors), references=tuple(refs))
