"""ROM-ATLAS-001 seed knowledge: `seed_knowledge.jsonl`.

Ported verbatim from the earlier exploratory script `build_seed.py`. Every row is
harvested from a repository document; **no ROM bytes are read**, which is why
`build` takes no ROM path.

The only change from the original is that the hardcoded
`build/atlas/seed_knowledge.jsonl` destination
(build_seed.py:8) became the `out_dir` parameter. Row order, the
`(file_offset, identity)` sort key and the `ensure_ascii=False` / unsorted-keys
serialization (build_seed.py:589) are unchanged.
"""

from __future__ import annotations

from pathlib import Path

from ..binary import GBA_ROM_BASE as BASE
from ._io import write_jsonl

#: Every address in this seed table is a GBA address. `BASE` is the sanctioned
#: `binary.GBA_ROM_BASE` rather than a second literal of it, so the address
#: window this table is checked against has one owner.


def _rows() -> list[dict]:
    rows: list[dict] = []

    def add(off=None, addr=None, size=None, kind="other", identity="", conf="UNKNOWN",
            source="", evidence="", notes=""):
        """off = file offset int; addr = gba address int or None."""
        if off is None:
            assert addr is not None
            assert BASE <= addr <= 0x087FFFFF, hex(addr)
            off = addr - BASE
        if addr is None:
            addr_s = None
        else:
            assert addr - BASE == off, (hex(addr), hex(off))
            addr_s = "0x%08X" % addr
        rows.append({
            "file_offset": off,
            "size": size,
            "gba_address": addr_s,
            "kind": kind,
            "identity": identity,
            "confidence": conf,
            "source": source,
            "evidence": evidence,
            "notes": notes,
        })

    # ---------------------------------------------------------------- header
    add(off=0x000000, addr=BASE, size=0x100, kind="other",
        identity="gba_header",
        conf="CONFIRMED",
        source="docs/research/BUU_VERIFIED_CAPACITY.md:116",
        evidence="Positive control 'header_startup' window [0x000000,0x000100) is REJECTED by the "
                 "capacity scanner on checks 'bounds' and 'fill' - i.e. it is declared, occupied header, "
                 "above which every free window must lie. PROJECT_<local-state-name> records GBA title DBZBUUSFURY, "
                 "game code BG3E, maker 70, header checksum 0x84 valid.",
        notes="Declared header bound is quoted as 0x158 in BUU_VERIFIED_CAPACITY.md:86; the control window "
              "used is the first 0x100 bytes. Size 0x100 is the control window, not a proven header extent. "
              "ARM entry point 0x080000C0 (docs/PROJECT_<local-state-name>:162) lies inside.")

    # ---------------------------------------------------------- low code region
    add(addr=0x08004038, size=None, kind="function",
        identity="script_vm.interpreter",
        conf="CONFIRMED",
        source="docs/research/BUU_SCRIPT_VM.md:31",
        evidence="Interpreter loop 0x08004038: resets primary stack depth, fetches one opcode byte, indexes "
                 "dispatch table 0x080554C0, calls the handler through the __call_via veneer 0x08046AA4; "
                 "null slot 0x11 terminates.",
        notes="size null: the function's extent is not stated in the source.")

    add(addr=0x08004098, size=None, kind="function",
        identity="dialog.entry_point",
        conf="CONFIRMED",
        source="docs/research/BUU_EVENT_RESOURCE.md:101",
        evidence="Dialog entry point: branches on dialog type byte at +0x02 (0x080040BA..0x080040C2); type 0 "
                 "runs the code block at dialog+0x03 through interpreter 0x08004038; type 4 expands via "
                 "0x08049120. Fails an assertion carrying 'Expected dialog to start with a code block'. "
                 "TOOLKIT-038 re-measured the dispatch: 0x080040BA is ldrb r1,[r0,#2], the SAME type byte the "
                 "shop script census measures, and 0x080040BC/0x080040C0 compare against 0 and 4 only. Its "
                 "else-branch calls 0x0803DF14 with Webfoot's own source path "
                 "'T:\\\\Source\\\\ByteCodeInterpreter\\\\ByteCodeInterpreter.cpp'. Ten BL sites call it: "
                 "0x08003242, 0x08003276, 0x080032BA, 0x08004C00, 0x0800E1A6, 0x0800E666, 0x0800FC5E, "
                 "0x0801096C, 0x0801A1B8, 0x08026480.",
        notes="size null: extent not stated. BOUNDARY, TOOLKIT-038: because this routine accepts only types 0 "
              "and 4 and asserts on everything else, it CANNOT be the consumer of the 17 type-0x03 plaintext "
              "shop bodies. The routine that reads a type-0x03 body and advances the live dialogue cursor at "
              "0x03003898 +0x24C is NOT IDENTIFIED, and is the next measured blocker.")

    add(addr=0x08003030, size=None, kind="function",
        identity="native_slot_178.handler",
        conf="RUNTIME_CONFIRMED",
        source="docs/research/GAMEPLAY_EFFECT_NATIVE.md:54",
        evidence="Native slot 178 is table pointer 0x08003031 / entry 0x08003030. Pops three (index deepest, "
                 "read from the handler at 0x0800303E/0x0800304C/0x0800305A) and calls 0x0802BFBC. "
                 "TOOLKIT-033 captured runtime frame 3111 at handler pc 0x08003032 with depth 3 and exact "
                 "arguments 1525/120/105, and frame 3116 visibly rendered 'MATCH 2 FIGHT!'.",
        notes="size null: extent not stated.")

    add(addr=0x0802BFBC, size=None, kind="function",
        identity="text.indexed_fetch_worker",
        conf="CONFIRMED",
        source="docs/research/BUU_DIALOG_RUNTIME.md:141",
        evidence="0x0802BFC0 ldr r1,=0x0806BCE8 then 0x0802BFC2 lsls r0,#2 / 0x0802BFC4 ldr r4,[r1,r0] - the "
                 "byte-for-byte access shape TOOLKIT-014 proved at 0x0801F85E. Measures the string via "
                 "0x0803FFE8, reserves VRAM, builds the text object via 0x0802BECC.",
        notes="size null: extent not stated. TOOLKIT-037 observed ZERO executions of this site during normal "
              "NPC dialogue (BUU_DIALOGUE_TEXT_STORES.md:61), so it is not the ordinary dialogue path.")

    add(addr=0x0803FFE8, size=None, kind="function",
        identity="text.utf16_measure",
        conf="CONFIRMED",
        source="docs/research/BUU_DIALOG_RUNTIME.md:162",
        evidence="Walks a pointer as UTF-16LE halfwords to NUL (ldrh, cmp #0, adds #2), splitting wide/narrow "
                 "at 0xFF and summing per-glyph advance widths from a font metrics table - the exact encoding "
                 "TOOLKIT-004 verified.",
        notes="size null: extent not stated.")

    add(addr=0x0802BECC, size=None, kind="function",
        identity="text.object_builder",
        conf="CONFIRMED",
        source="docs/research/BUU_DIALOG_RUNTIME.md:182",
        evidence="Builds the text object; sibling emitter 0x0802BFEC writes 8-byte OAM entries (8-bit Y, "
                 "9-bit X, 32-pixel step) and 0x0802BF8E blits glyph tiles into 0x06010000, the GBA OBJ VRAM base.",
        notes="size null: extent not stated. 0x06010000 is VRAM, not a ROM location, and is deliberately not "
              "emitted as a row.")

    add(addr=0x0800F68C, size=None, kind="function",
        identity="placement_types.constructor",
        conf="CONFIRMED",
        source="config/roms.yaml:37",
        evidence="TOOLKIT-009 PLACEMENT_TYPES.md: the canonical FD54 wrapper computes table + 28 * placement[8] "
                 "then calls F68C. Declared in the profile as placement_types.constructor_address.",
        notes="size null: extent not stated.")

    add(addr=0x0800FD54, size=None, kind="function",
        identity="placement_types.factory_wrapper",
        conf="CONFIRMED",
        source="docs/research/PLACEMENT_TYPES.md:40",
        evidence="The canonical factory raw is 0x0800FD55; Thumb fetch is 0x0800FD54. Declared in the profile as "
                 "placement_types.factory_raw 0x0800fd55.",
        notes="size null: extent not stated. The raw 0x0800FD55 carries the Thumb state bit; the fetch address "
              "is 0x0800FD54 and that is the file offset recorded here.")

    add(addr=0x0800421E, size=None, kind="function",
        identity="script.dispatch_trampoline_0800421F",
        conf="CONFIRMED",
        source="docs/research/BUU_FD55_SCRIPT_OWNER.md:130",
        evidence="Raw 0x0800421F (fetch 0x0800421E) is 'ldr r1,[r0,#4]; bl 0x08004038' - interpret the "
                 "descriptor payload as a script. 57 records / 10 maps. It is the address of the trampoline, "
                 "not a factory tag for a separate record family.",
        notes="size null: extent not stated. Recorded at the Thumb fetch address; raw pointer is 0x0800421F.")

    add(addr=0x08046AA4, size=None, kind="function",
        identity="__call_via_rN_veneer",
        conf="CONFIRMED",
        source="docs/research/BUU_SCRIPT_VM.md:155",
        evidence="0x08046AA4 remains the gcc __call_via_rN veneer. Correction recorded in TOOLKIT-012: it is a "
                 "veneer, NOT a point query.",
        notes="size null: extent not stated. Earlier 'point query' naming is SUPERSEDED by TOOLKIT-012 "
              "(docs/PROJECT_<local-state-name>:19).")

    add(addr=0x080126D4, size=0x080127AE - 0x080126D4, kind="function",
        identity="spatial.point_query",
        conf="RUNTIME_CONFIRMED",
        source="docs/research/SUBSYSTEM_MAP.md:35",
        evidence="0x080126D4..0x080127AD point query: signed half-open AABB against +0x04..+0x0B, first-accept "
                 "exit, two-stage callback dispatch. L3 runtime (ROM-011/ROM-012).",
        notes="Size derived from the stated inclusive end 0x080127AD, exclusive 0x080127AE.")

    add(addr=0x080127AE, size=0x08012846 - 0x080127AE, kind="function",
        identity="spatial.aabb_query_2",
        conf="CONFIRMED",
        source="docs/research/SUBSYSTEM_MAP.md:36",
        evidence="0x080127AE..0x08012844 second AABB query routine; static entries with named callers.",
        notes="Size derived from the next routine's entry 0x08012846.")

    add(addr=0x08012846, size=None, kind="function",
        identity="spatial.aabb_query_3",
        conf="CONFIRMED",
        source="docs/research/SUBSYSTEM_MAP.md:37",
        evidence="0x08012846.. third query routine; static entry.",
        notes="size null: the source gives an entry with no stated end.")

    add(addr=0x08012664, size=None, kind="function",
        identity="population.registry_populate",
        conf="RUNTIME_CONFIRMED",
        source="docs/research/SUBSYSTEM_MAP.md:31",
        evidence="Descriptor-array iteration (backward), indirect factory dispatch via 0x08046AA2 BX r1, "
                 "registry append. AUTO-011: sole caller is the population adapter. L3 runtime.",
        notes="size null: extent not stated.")

    add(addr=0x080089CC, size=None, kind="function",
        identity="map.variation_word_resolver",
        conf="RUNTIME_CONFIRMED",
        source="docs/research/SUBSYSTEM_MAP.md:13",
        evidence="Resolves MapEntry[+0x2C] + 4*(selector-1); CONFIRMED L3. ROM-006 verified at runtime on the "
                 "trusted ROM: MapEntry 1 expected/observed 0x082B5FA0, MapEntry 4 expected/observed 0x082B5B2C.",
        notes="size null: extent not stated.")

    add(addr=0x080089FC, size=None, kind="function",
        identity="map.mapentry_lookup",
        conf="CONFIRMED",
        source="docs/research/SUBSYSTEM_MAP.md:12",
        evidence="Thumb MapEntry lookup: compares +0x00/+0x01, stride 0x38. BL sites 0x08004A82, 0x08008D2A, "
                 "0x08008D6C, 0x08008E94, 0x08009056. CONFIRMED (static + structure).",
        notes="size null: extent not stated.")

    add(addr=0x08007674, size=None, kind="function",
        identity="spatial.rect_object_factory",
        conf="RUNTIME_CONFIRMED",
        source="docs/PROJECT_<local-state-name>:112",
        evidence="ROM-007/ROM-008: raw factory target 0x08007675, Thumb fetch 0x08007674, allocation 0x18 bytes, "
                 "creates a 24-byte rectangle-aware runtime object registered by the population manager. "
                 "STRONGLY SUPPORTED generic 24-byte rectangle-aware runtime object.",
        notes="size null: extent not stated. Collision/trigger/transition semantics are explicitly NOT proven "
              "(docs/PROJECT_<local-state-name>:124). Recorded at the Thumb fetch address; raw is 0x08007675.")

    add(addr=0x0800FA50, size=None, kind="function",
        identity="combat.hp_writer",
        conf="RUNTIME_CONFIRMED",
        source="docs/PROJECT_<local-state-name>:175",
        evidence="P-006A confirmed signed current HP at target+0x28C, incoming damage at record+0x18, "
                 "authoritative writer 0x0800FA50, death threshold HP <= 0.",
        notes="size null: extent not stated. target+0x28C is EWRAM runtime state, not a ROM offset, and is "
              "deliberately not emitted as a row.")

    # --------------------------------------------------------- data: low ROM
    add(addr=0x0805632C, size=None, kind="palette",
        identity="background_palette",
        conf="CANDIDATE",
        source="docs/research/GRAPHICS_FORMAT.md:367",
        evidence="Background palette at file 0x0005632C, with 1 inbound word-aligned reference against the "
                 "object palette's 16, and 20 words with GBA's unused bit 15 set. Listed under DISCOVERED, "
                 "deliberately unexplored.",
        notes="size null: no extent measured. Doc explicitly files this under 'DISCOVERED only, deliberately "
              "unexplored', so it stays CANDIDATE.")

    add(addr=0x0805652C, size=None, kind="palette",
        identity="object_palette",
        conf="CONFIRMED",
        source="config/roms.yaml:19",
        evidence="TOOLKIT-010 GRAPHICS_FORMAT.md, verified against the canonical image: one global 256-entry "
                 "object palette declared as actor_sprites.object_palette_address. 16 inbound word-aligned "
                 "references against the background palette's 1; 255 distinct entries; only one word has GBA's "
                 "unused bit 15 set; reads as a deliberate ramp.",
        notes="size null: the profile declares only the address. A 256-entry GBA palette would be 512 bytes but "
              "no source states the extent, so it is not asserted.")

    TEXT_POOL = 0x0805792C
    TEXT_POOL_SIZE = 82874
    add(addr=TEXT_POOL, size=TEXT_POOL_SIZE, kind="string_pool",
        identity="text_strings.pool",
        conf="CONFIRMED",
        source="config/roms.yaml:58",
        evidence="TOOLKIT-004 verified against the canonical image: 1534 pointers strictly ascending with no "
                 "duplicate targets, whose strings tile 0x0005792c..0x0006bce6 exhaustively with no gap or "
                 "overlap. Encoding utf16le_nul_terminated, alignment 2, pool_size 82874. The pool base has "
                 "exactly one inbound word-aligned reference in the whole ROM (this table).",
        notes="TOOLKIT-037 (docs/research/BUU_DIALOGUE_TEXT_STORES.md:17) censused the CONTENT: menus, items, "
              "equipment, bestiary, quest objectives - NOT spoken NPC dialogue.")

    TEXT_TABLE = 0x0806BCE8
    add(addr=TEXT_TABLE, size=6136, kind="pointer_table",
        identity="text_strings.pointer_table",
        conf="CONFIRMED",
        source="config/roms.yaml:56",
        evidence="TOOLKIT-004: 1534 pointers at 0x0806bce8, strictly ascending, no duplicate targets, tiling the "
                 "pool exhaustively. Table base has 51 inbound word-aligned references - access is by index. "
                 "TEXT_FORMAT.md:86 gives the extent 0x0006BCE8..0x0006D4DF, 1,534 entries, 6,136 bytes. "
                 "TOOLKIT-036 set relocatable true for this table only.",
        notes="Size from docs/research/TEXT_FORMAT.md:86 (6,136 bytes = 1534*4). Five entries (indices 689, 818, "
              "819, 856, 1342) carry a second aligned word and are refused per entry as coincidence candidates.")

    # ---------------------------------------------------- placement / map data
    PLACEMENT_STREAM = 0x080728CC
    add(addr=PLACEMENT_STREAM, size=112916, kind="placement_data",
        identity="mapentry_2c_content_stream",
        conf="CONFIRMED",
        source="docs/research/COLLISION_FORMAT.md:99",
        evidence="MapEntry[+0x2C] is live on all 452 entries (452 distinct targets, zero shared) addressing one "
                 "heterogeneous factory-tagged stream 0x080728CC..0x0808E1E0, 112,916 bytes, ending exactly "
                 "where the MapEntry table begins. 40 interleaved families.",
        notes="Contains the placement records, object arrays and descriptor records this project decoded - "
              "genuine nesting; individual records are not enumerated here. CAVEAT: the source says it ends "
              "'exactly where the MapEntry table begins', but the measured end 0x0808E1E0 is 256 bytes below "
              "the declared map_entries base 0x0808E2E0. Those 256 bytes are UNCLAIMED by any source.")

    add(addr=0x0808E2E0, size=452 * 0x38, kind="record_table",
        identity="map_entries",
        conf="CONFIRMED",
        source="config/roms.yaml:44",
        evidence="Declared map_entries address 0x0808e2e0, count 452, record_size 0x38. MAP_FORMAT.md:14 gives "
                 "the extent 0x0008E2E0..0x000945C0. All 452 records parse and serialize byte-exactly; iteration "
                 "is fixed-count with no sentinel. Independently corroborated by DragonByteZ's Buu profile "
                 "(map_entry_table = 0x0008E2E0, count 452).",
        notes="Size = 452 * 0x38 = 25,312 bytes, which lands exactly on the stated exclusive end 0x000945C0.")

    add(addr=0x08009BD4, size=None, kind="function",
        identity="map_background.character_assembler",
        conf="CONFIRMED",
        source="docs/research/MAP_RENDER_FORMAT.md:80",
        evidence="MAP-VIS-002 static/runtime proof: expands descriptor +0x48 delta selectors; high selector "
                 "byte chooses descriptor +0x4C tileset pointer, low byte chooses one 64-byte tile, and "
                 "0x08009C62..0x08009C78 copies selected tiles to sequential VRAM destinations.",
        notes="Size null: the function's exact extent is not claimed. Runtime decompressor captures with "
              "LR 0x08009C5E independently establish its ROM -> EWRAM -> VRAM writer family.")

    add(addr=0x08007BDE, size=None, kind="function",
        identity="map_background.logical_chunk_loader",
        conf="CONFIRMED",
        source="docs/research/MAP_RENDER_FORMAT.md:146",
        evidence="MAP-VIS-002: reads layer-record +0x14/+0x15 chunk dimensions and +0x18 u32 container "
                 "array; 0x08007C82..0x08007C90 selects row-major y*width+x chunks, each decoding to "
                 "one 0x800-byte regular-BG entry block.",
        notes="Transient EWRAM buffers and camera-relative screenblock windows are deliberately not Atlas "
              "objects; the persistent object is the ROM layer/chunk relationship.")

    add(addr=0x082932F8, size=None, kind="graphics",
        identity="map:0040.tile_selector_container",
        conf="CONFIRMED",
        source="docs/research/MAP_RENDER_FORMAT.md:67",
        evidence="Descriptor 0x08293474 +0x48; Webfoot-LZ container decodes to 0x1DE bytes / 239 "
                 "delta-coded u16 selectors consumed by map_background.character_assembler.",
        notes="Packed ROM extent is decoder-measured at use time; no size asserted in the seed row.")

    add(addr=0x08294660, size=None, kind="graphics",
        identity="map:0039.tile_selector_container",
        conf="CONFIRMED",
        source="docs/research/MAP_RENDER_FORMAT.md:67",
        evidence="Descriptor 0x08294968 +0x48; Webfoot-LZ container decodes to 0x206 bytes / 259 "
                 "delta-coded u16 selectors consumed by map_background.character_assembler.",
        notes="Packed ROM extent is decoder-measured at use time; no size asserted in the seed row.")

    # ------------------------------------------------------------- script VM
    add(addr=0x080554C0, size=31 * 4, kind="pointer_table",
        identity="script_vm.primary_dispatch_table",
        conf="CONFIRMED",
        source="docs/research/BUU_SCRIPT_VM.md:43",
        evidence="Primary dispatch table 0x080554C0, resolved from the literal at 0x0800415C. Exactly 31 slots "
                 "(0x00..0x1E); slot 0x11 is NULL = terminate. It holds exactly 31 slots because slot 0x1F "
                 "onward is UTF-16 text - a measured bound.",
        notes="Size = 31 * 4 = 124 bytes, derived from the measured 31-slot bound.")

    add(addr=0x08055098, size=None, kind="pointer_table",
        identity="script_vm.native_dispatch_table",
        conf="CONFIRMED",
        source="docs/research/BUU_SCRIPT_VM.md:49",
        evidence="Secondary native-dispatch table 0x08055098 holding 283 Thumb handlers, with a paired table at "
                 "0x08055478. Both are referenced only from the interpreter region 0x08003F40..0x08004034, "
                 "confirming one self-contained VM.",
        notes="size null DELIBERATELY: the source states 283 handlers but no extent, and 283 * 4 = 1,132 bytes "
              "would run to 0x08055504, OVERRUNNING both the paired table at 0x08055478 and the primary dispatch "
              "table at 0x080554C0. The handler count and a dense 4-byte layout from this base are therefore not "
              "simultaneously consistent; no size is asserted. Semantics of all 283 handlers are UNKNOWN "
              "(docs/PROJECT_<local-state-name>:57). Flagged for follow-up.")

    add(addr=0x08055478, size=None, kind="pointer_table",
        identity="script_vm.native_paired_table",
        conf="OBSERVED",
        source="docs/research/BUU_SCRIPT_VM.md:50",
        evidence="A table paired with the native dispatch table 0x08055098, referenced only from the interpreter "
                 "region 0x08003F40..0x08004034.",
        notes="size null: no extent or entry count stated. Role beyond 'paired' is not established. "
              "See the overrun note on script_vm.native_dispatch_table.")

    add(addr=0x080555A0, size=None, kind="record_table",
        identity="null_handler_descriptor",
        conf="CONFIRMED",
        source="docs/research/BUU_FD55_SCRIPT_OWNER.md:133",
        evidence="0x080555A0 is the shared null-handler descriptor: it holds 0x0800421D ('bx lr', no behavior). "
                 "It appears as the constant +0x14 tail word in 1,361 (later 1,429) placement records, which is "
                 "simply the shared address of that descriptor rather than a per-record constant.",
        notes="size null: extent not stated. Shared, referenced by many placement records.")

    STATIC40_POOL = 0x08720340
    STATIC40_TABLE = 0x08720564
    add(addr=STATIC40_POOL, size=548, kind="script_pool",
        identity="scripts.static40.pool",
        conf="CONFIRMED",
        source="config/roms.yaml:86",
        evidence="TOOLKIT-013 BUU_SCRIPT_VM.md, verified against the canonical image: pool_address 0x08720340, "
                 "pool_size 548. All 120 pointers non-null, distinct, strictly ascending; the pool ends exactly "
                 "where the table begins; the 120 roots tile the 548-byte pool exhaustively with zero uncovered "
                 "bytes. 328 instructions, re-encode byte-identical.",
        notes="Pool [0x720340,0x720564) abuts the static40 table at 0x720564 exactly - adjacency, not overlap.")

    add(addr=STATIC40_TABLE, size=40 * 16, kind="record_table",
        identity="scripts.static40.table",
        conf="CONFIRMED",
        source="config/roms.yaml:82",
        evidence="TOOLKIT-013: table_address 0x08720564, count 40, stride 16, slots [4,8,12]. Walker 0x080141EE "
                 "loads this table, forms table + 16*i and interprets record +0x04, +0x08 and +0x0C, bounded by "
                 "cmp r6,#0x28 = 40 records.",
        notes="Size = 40 * 16 = 640 bytes, derived from the declared count and stride.")

    ITEM_POOL = 0x083BBBB0
    ITEM_TABLE = 0x083BD2F8
    add(addr=ITEM_POOL, size=703, kind="script_pool",
        identity="scripts.item_use.pool",
        conf="CONFIRMED",
        source="config/roms.yaml:109",
        evidence="TOOLKIT-014 BUU_SCRIPT_OWNERSHIP.md, verified against the canonical image: pool_address "
                 "0x083bbbb0, pool_size 703. 23 of the 83 item records carry a non-null +0x30 pointer; those 23 "
                 "are distinct, strictly ascending and tile the 703-byte pool 0x083BBBB0..0x083BBE6F "
                 "exhaustively with zero uncovered bytes, and the corpus re-encodes byte-identically.",
        notes="")

    add(addr=ITEM_TABLE, size=83 * 52, kind="record_table",
        identity="scripts.item_use.table",
        conf="CONFIRMED",
        source="config/roms.yaml:105",
        evidence="TOOLKIT-014: the static item table at 0x083BD2F8 holds 83 records of 52 bytes; twelve "
                 "independent code sites compute table + 52*index, and 0x0800D742 / 0x0800DDC2 pass the record to "
                 "0x0801E164, which interprets the pointer at record +0x30 through interpreter 0x08004038. "
                 "Owner identity established by its own text: index 0x028E decodes to 'Miso Soup'.",
        notes="Size = 83 * 52 = 4,316 bytes, derived from the declared count and stride. Halfwords at +0x02, "
              "+0x04, +0x06, +0x08 are proven text indices into 0x0806BCE8.")

    # ------------------------------------------------- stats / sprites / types
    add(addr=0x086B6BDC, size=297 * 4, kind="pointer_table",
        identity="actor_sprites.character_table",
        conf="CONFIRMED",
        source="config/roms.yaml:16",
        evidence="TOOLKIT-010 GRAPHICS_FORMAT.md, verified against the canonical image. All 297 table entries "
                 "are ROM pointers for logical ids 10..306, strictly ascending, and the last structure ends "
                 "immediately before the table itself. Their animation-pointer array at +0x54 is bounded by "
                 "the count at +0x00: 4,070 slots, 1,721 non-null, reaching 297 character-table slots with "
                 "art, 1,017 unique animation objects, 10,980 distinct frame records (11,005 piece records) "
                 "and 7,390 distinct container offsets reachable by a piece; every container decodes and "
                 "every decoded length equals its declared width by height.",
        notes="Size = 297 * 4 = 1,188 bytes, derived from the declared count. NOT a free-space declaration: "
              "containers are packed with no slack.")

    add(addr=0x086A89D0, size=0x086B6BDC - 0x086A89D0, kind="graphics",
        identity="actor_sprites.character_structures",
        conf="CONFIRMED",
        source="docs/research/GRAPHICS_FORMAT.md:146",
        evidence="The last structure (0x086B6B60) ends immediately before the table itself, but the structures "
                 "do not tile one contiguous region 0x006A89D0..0x006B6BDC: each of the 297 carries an "
                 "animation count at +0x00 and a count-bounded sparse inline animation-pointer array at "
                 "+0x54, 4,070 slots of which 1,721 are non-null.",
        notes="Size is the declared 0x006A89D0..0x006B6BDC span, not an exhaustive-tiling or free-space "
              "declaration. This region is the sprite/animation structure area; the compressed graphics "
              "containers it reaches live elsewhere and are not enumerated here.")

    ASSERT_START = 0x086B7400
    ASSERT_END = 0x086B758E
    add(addr=ASSERT_START, size=ASSERT_END - ASSERT_START, kind="assertion_strings",
        identity="developer_assertion_strings",
        conf="CONFIRMED",
        source="docs/research/BUU_DIALOGUE_TEXT_STORES.md:108",
        evidence="TOOLKIT-037 whole-image stride-1 UTF-16LE census, evidence class CONFIRMED_ROM. Region "
                 "0x086B7400..0x086B758E, 3 strings: 'Energy attack level set for attack which doesn't exist for "
                 "player!', 'Energy attack level requested for attack which doesn't exist for player!', 'Unable "
                 "to find sprite index in character state data'. Leftover developer diagnostics, no gameplay role.",
        notes="Marked UNOWNED in the doc's headline (line 18): no pointer table or consumer located. Size "
              "derived from the stated inclusive extent as an exclusive end.")

    add(addr=0x086FDA4C, size=9 * 0x12, kind="record_table",
        identity="character_base_stats",
        conf="CONFIRMED",
        source="config/roms.yaml:52",
        evidence="Declared in the toolchain profile: character_base_stats address 0x086fda4c, count 9, "
                 "record_size 0x12.",
        notes="Size = 9 * 0x12 = 162 bytes, derived from the declared count and record size. The profile entry "
              "carries no separate evidence string of its own.")

    add(addr=0x0870F514, size=None, kind="record_table",
        identity="behavior_state_table",
        conf="RUNTIME_CONFIRMED",
        source="docs/PROJECT_<local-state-name>:190",
        evidence="P-006C: state-table base is 0x0870F514, stride 8; entries are {node, table_slot}. Reading "
                 "wolf+0x238 per frame reproduced wolf selectors 434-439 with zero stops, confirming the table "
                 "at Level 3.",
        notes="size null: no entry count or extent is stated anywhere. BUU_MAP_SCRIPT_OWNERSHIP.md:233 records "
              "placement type +0x08 reaching this behavior-tree descriptor table rather than the script VM.")

    ENEMY_STATS = 0x08711274
    add(addr=ENEMY_STATS, size=141 * 0x1C, kind="record_table",
        identity="enemy_stats",
        conf="CONFIRMED",
        source="config/roms.yaml:48",
        evidence="Declared in the toolchain profile: enemy_stats address 0x08711274, count 141, record_size "
                 "0x1c. TOOLKIT-009 round-tripped 2,660 bytes across 95 enemy-linked types / 1,284 placements "
                 "(docs/PROJECT_<local-state-name>:27); GRAPHICS_FORMAT.md:380 probed all 141 records at 0x1C stride.",
        notes="CONFLICT: placement_types declares the SAME base address 0x08711274 with stride 28 (=0x1C) and "
              "max_selector 149 (config/roms.yaml:33). The two declarations share a base and a stride but "
              "disagree on count/extent - 141 records (3,948 bytes) versus a selector bound of 149. "
              "config/roms.yaml:41 states the max selector is the observed supported bound, NOT a total table "
              "count, and that targets outside the verified enemy_stats extent have no record codec.")

    add(addr=ENEMY_STATS, size=None, kind="record_table",
        identity="placement_types.table",
        conf="CONFIRMED",
        source="config/roms.yaml:33",
        evidence="TOOLKIT-009 PLACEMENT_TYPES.md: canonical FD54 wrapper computes table + 28 * placement[8], "
                 "then calls F68C. table_address 0x08711274, stride 28, max_selector 149. TOOLKIT-009 confirmed "
                 "101 stable shared type selectors selecting 0x08711274 + 28 * selector, CONFIRMED static LEVEL 2.",
        notes="CONFLICT: enemy_stats (config/roms.yaml:47) declares the same base 0x08711274 with count 141, "
              "record_size 0x1c - i.e. an explicit 3,948-byte extent - while this entry declares only a selector "
              "bound of 149 and explicitly refuses to treat it as a table count. size null because the profile "
              "states max_selector is NOT a total count. Six selectors (141,142,146,147,148,149) used by 11 "
              "placements remain reference-only with no record extent or enemy claim.")

    # --------------------------------------------------- free region / authored
    FREE = 0x007EA400
    add(off=FREE, addr=BASE + FREE, size=256, kind="free_region",
        identity="free_region.toolkit028",
        conf="CONFIRMED",
        source="config/roms.yaml:133",
        evidence="TOOLKIT-028 BUU_VERIFIED_CAPACITY.md, verified against the canonical image by "
                 "tools/research/capacity_proof.py. A bounded 256-byte window of the upstream tail, NOT the tail "
                 "itself. All seven checks pass: 256 bytes entirely FF fill; no CONFIRMED or DECLARED reference "
                 "targets any byte; no modelled anchor or declared table overlaps it; no candidate observation "
                 "targets any byte at any alignment, interior included; no candidate is sourced inside it; "
                 "nearest candidate target is 1,717 bytes below and 2,816 above against a required 1,024; it "
                 "lies far above the declared header. Four positive controls all REJECTED, each on its named check.",
        notes="Declared with file_offset in config/roms.yaml, so the GBA address is derived (0x087EA400). "
              "NESTING: this window is itself CONTAINED in upstream_tail_candidate [0x7B89A8,0x800000), and it "
              "CONTAINS the four authored.* rows (placement_body, descriptor, script_body, expanded_slot_array) "
              "which occupy its first 72 bytes. All such overlaps are genuine nesting, not conflicting claims. "
              "TOOLKIT-011's whole tail is REJECTED and remains so - 516 unresolved candidate references target "
              "it; only this carved window is CONFIRMED free.")

    add(off=0x007EA400, addr=0x087EA400, size=32, kind="placement_data",
        identity="authored.placement_body",
        conf="RUNTIME_CONFIRMED",
        source="docs/research/GAMEPLAY_EFFECT_NATIVE.md:90",
        evidence="TOOLKIT-033 production allocation inside [0x007EA400,0x007EA500): authored placement at "
                 "0x007EA400, 32 bytes. Runtime frame 3111 captured the authored chain executing and frame 3116 "
                 "visibly showed 'MATCH 2 FIGHT!' at the authored Y=105.",
        notes="NESTED inside free_region.toolkit028 [0x7EA400,0x7EA500) - this is SDK-authored content written "
              "into that verified free window, not canonical ROM structure. It does not exist in the canonical "
              "image; it is recorded because the atlas must know the window is now claimed by the SDK.")

    add(off=0x007EA420, addr=0x087EA420, size=8, kind="record_table",
        identity="authored.descriptor",
        conf="RUNTIME_CONFIRMED",
        source="docs/research/GAMEPLAY_EFFECT_NATIVE.md:91",
        evidence="Authored descriptor at 0x007EA420, 8 bytes, {handler, script_address}. Runtime: pc 0x08004220 "
                 "descriptor 0x087EA420 -> payload 0x087EA428.",
        notes="NESTED inside free_region.toolkit028. SDK-authored, not canonical.")

    add(off=0x007EA428, addr=0x087EA428, size=11, kind="script_pool",
        identity="authored.script_body",
        conf="RUNTIME_CONFIRMED",
        source="docs/research/GAMEPLAY_EFFECT_NATIVE.md:92",
        evidence="Authored script at 0x007EA428, 11 bytes: 1D 03 97 6A 81 70 81 52 02 B2 11 = push text "
                 "1525/X120/Y105, call native slot 178, terminate. Zero occurrences in canonical Buu. Runtime pc "
                 "0x0800403A read the live cursor 0x087EA428.",
        notes="NESTED inside free_region.toolkit028. SDK-authored, not canonical.")

    add(off=0x007EA434, addr=0x087EA434, size=20, kind="placement_data",
        identity="authored.expanded_slot_array",
        conf="CONFIRMED",
        source="docs/research/GAMEPLAY_EFFECT_NATIVE.md:93",
        evidence="Expanded five-slot array at 0x007EA434, 20 bytes. The highest occupied byte ends at "
                 "0x007EA448, leaving 184 bytes of the 256-byte window.",
        notes="NESTED inside free_region.toolkit028. SDK-authored, not canonical. OLD CLAIM of a 12-byte array "
              "(TOOLKIT-028) is SUPERSEDED by TOOLKIT-032: map 40 has 4 canonical slots so its array is 5*4=20 "
              "(docs/PROJECT_<local-state-name>:41).")

    # --------------------------------------------------- shop dialogue / events
    SHOP_START = 0x0877F09A
    SHOP_END = 0x087801D4
    add(addr=SHOP_START, size=SHOP_END - SHOP_START, kind="dialogue_store",
        identity="shop_dialogue_store",
        conf="CONFIRMED",
        source="docs/research/BUU_DIALOGUE_TEXT_STORES.md:107",
        evidence="TOOLKIT-037 whole-image stride-1 UTF-16LE census, evidence class CONFIRMED_ROM: region "
                 "0x0877F09A..0x087801D4, 22 strings, NPC speech plus menu choices, uncompressed UTF-16LE, same "
                 "encoding as the declared pool, different location. Examples: 'Welcome to the Hercule City "
                 "Z-Mart! How can I help you?', '-Buy', '-Sell', '-End'. A conversational dialogue system with "
                 "branching choices.",
        notes="OVERLAP RESOLVED by TOOLKIT-038 (docs/research/BUU_SHOP_SCENARIO_MODEL.md): this speech IS "
              "event-record payload, not a distinct store. The six stride-4 scenario arrays in the region are "
              "entries 28/30/31/33/34/36 of event_resource.pointer_table, and none of their 61 script targets is "
              "itself a table entry, so the region is owned through the table TOOLKIT-019 already proved. The "
              "OLD 'UNOWNED' label (BUU_DIALOGUE_TEXT_STORES.md:18) was correct for what it measured and is "
              "SUPERSEDED. All 61 scripts satisfy TOOLKIT-036's unique-ownership relocation gate. Size derived "
              "from the stated inclusive extent as an exclusive end.")

    # TOOLKIT-038 measured the six shop scenarios inside that region. Each is an
    # event record whose body is a stride-4 array of script pointers, preceded by
    # an 8-byte type-0x05 descriptor whose u16 count equals the entry count.
    # (array address, entry count, event pointer-table index)
    SHOP_SCENARIOS = (
        (0x0877F3B0, 10, 28),
        (0x0877F73C, 10, 30),
        (0x0877FAB8, 11, 31),
        (0x0877FE00, 10, 33),
        (0x08780008, 8, 34),
        (0x087803E4, 12, 36),
    )
    for _array, _count, _event in SHOP_SCENARIOS:
        add(addr=_array, size=_count * 4, kind="pointer_table",
            identity="shop_scenario.array_%06X" % (_array - BASE),
            conf="CONFIRMED",
            source="docs/research/BUU_SHOP_SCENARIO_MODEL.md:41",
            evidence="TOOLKIT-038, evidence class CONFIRMED_ROM: stride-4 array of %d script pointers, "
                     "addressed by event_resource.pointer_table entry %d. Its last slot points 8 bytes below "
                     "the base, at a type-0x05 descriptor whose u16 count equals %d. Every script target has "
                     "EXACTLY ONE word-aligned inbound reference in the whole 8 MiB image - its own slot - so "
                     "TOOLKIT-036's per-entry relocation gate is satisfied."
                     % (_count, _event, _count),
            notes="Scripts are NOT separately addressable: 0 of the 61 targets across all six scenarios appears "
                  "in the 522-entry pointer table. Branch correspondence to Buy/Sell/End is INFERRED, not "
                  "runtime-proven.")
        add(addr=_array - 8, size=8, kind="other",
            identity="shop_scenario.descriptor_%06X" % (_array - BASE - 8),
            conf="CONFIRMED",
            source="docs/research/BUU_SHOP_SCENARIO_MODEL.md:132",
            evidence="TOOLKIT-038: +0 u16 entry_count = %d, +2 u8 type = 0x05, +3 u8 = 0, "
                     "+4 u32 = 0x02CE74C0 (identical across all six scenarios). The count cross-checks the "
                     "array it precedes." % _count,
            notes="These 8 bytes fall inside the PRECEDING event record's extent, so whether they are that "
                  "record's trailing field or an 8-byte prefix the engine reads before the array is UNKNOWN "
                  "from bytes alone; both readings fit. The role of 0x02CE74C0 is UNKNOWN.")

    add(addr=0x0879B774, size=None, kind="pointer_table",
        identity="shop_scenario.master_index",
        conf="CANDIDATE",
        source="docs/research/BUU_SHOP_SCENARIO_MODEL.md:206",
        evidence="TOOLKIT-038: a contiguous run of aligned words listing every scenario array in the "
                 "0x0877Fxxx..0x0878xxxx region, including all six shop arrays. Found by scanning the image for "
                 "words equal to a scenario array address.",
        notes="size null: extent not measured. CANDIDATE, not CONFIRMED: the run's bounds and its consumer were "
              "not established, and it lies just past event_resource.pointer_table's end at 0x0879BF2C.")

    # TOOLKIT-038: the shop object records that carry a scenario pointer. This is
    # Data Crystal's "NPC structure contains a dialogue pointer" in stronger
    # form - the pointer is to a scenario, not to a string.
    for _record, _scenario in ((0x08074360, 0x0877F3B0), (0x080743C4, 0x0877F73C),
                               (0x08074450, 0x0877FAB8), (0x080744B4, 0x0877FE00),
                               (0x0807451C, 0x08780008)):
        add(addr=_record, size=None, kind="other",
            identity="shop_object.record_%06X" % (_record - BASE),
            conf="CONFIRMED",
            source="docs/research/BUU_SHOP_SCENARIO_MODEL.md:238",
            evidence="TOOLKIT-038: field +0x0C holds scenario 0x%08X. Fields +0x00, +0x04, +0x08, +0x10, +0x14, "
                     "+0x18 and +0x1C are byte-identical across all five records; +0x00/+0x10/+0x14 are Thumb "
                     "code pointers 0x0800775F / 0x08007675 / 0x080077DF that disassemble as object-lifecycle "
                     "callbacks, none of which touches text." % _scenario,
            notes="size null: the record's full extent was not measured. Event 36 (0x087803E4) has no record in "
                  "this cluster, so the five records do not account for all six scenarios.")

    EVENT_POOL = 0x0877C5A4
    EVENT_TABLE = 0x0879B704
    add(addr=EVENT_POOL, size=127328, kind="script_pool",
        identity="event_resource.record_pool",
        conf="CONFIRMED",
        source="docs/research/BUU_EVENT_RESOURCE.md:35",
        evidence="TOOLKIT-019: pool 0x0877C5A4..0x0879B704, 127,328 bytes, tiled exhaustively by the 522 records "
                 "with zero gap or overlap; sizes min 16 / max 3,168 / median 100, 166 distinct sizes, all "
                 "multiples of 4. The pool ends exactly where the table begins. 236 type-0 dialog records are "
                 "ROUND_TRIP over 10,263 code bytes; the remaining 286 are structurally classified by type byte "
                 "and explicitly refused by the codec.",
        notes="OVERLAP RESOLVED by TOOLKIT-038: this pool [0x77C5A4,0x79B704) CONTAINS the "
              "shop_dialogue_store region [0x77F09A,0x7801D4) because that speech is this pool's own record "
              "payload. The six shop scenario arrays are pool records addressed by entries 28/30/31/33/34/36 of "
              "the pointer table, and their 61 script targets are payload reached only through them. The pool's "
              "exhaustive zero-gap tiling and the shop region's contents are therefore consistent, not in "
              "conflict.")

    add(addr=EVENT_TABLE, size=2088, kind="pointer_table",
        identity="event_resource.pointer_table",
        conf="CONFIRMED",
        source="docs/research/BUU_EVENT_RESOURCE.md:34",
        evidence="TOOLKIT-019: table base 0x0879B704, 522 pointers, extent 0x0879B704..0x0879BF2C (2,088 bytes). "
                 "All 522 strictly ascending, all landing inside the pool, records tiling it exhaustively. "
                 "Exactly 2 inbound refs to the base, both consumer literal pools (file 0x31C0, 0x3444). The "
                 "bound is corroborated a second, independent way by Data Crystal's compressed-text start.",
        notes="The engine's own term is 'dialog' (assertion string 'Expected dialog to start with a code "
              "block'); stable identifiers remain event_resource. 2088 = 522 * 4.")

    add(addr=0x0879BF2C, size=None, kind="compressed_stream",
        identity="compressed_text_region",
        conf="CANDIDATE",
        source="docs/research/BUU_MAP_EVENT_REFERENCES.md:246",
        evidence="Data Crystal records seven compressed-text pointers beginning 0x0879BF2C, stored at "
                 "0x7B5B64..0x7B5B7C; all seven values were verified present in our image. Independently "
                 "corroborated as the terminus of the event_resource ascending-pointer walk "
                 "(BUU_EVENT_RESOURCE.md:44).",
        notes="size null: no extent measured. Explicitly UNTOUCHED / NOT REACHED by TOOLKIT-020, TOOLKIT-021 and "
              "TOOLKIT-037 (docs/research/BUU_DIALOGUE_TEXT_STORES.md:181). CANDIDATE because the region's start "
              "is upstream-sourced and only its presence was verified locally; no content was decoded here.")

    add(addr=0x087B5B64, size=0x087B5B7C + 4 - 0x087B5B64, kind="pointer_table",
        identity="compressed_text.pointer_table",
        conf="OBSERVED",
        source="docs/research/BUU_MAP_EVENT_REFERENCES.md:247",
        evidence="Seven compressed-text pointers stored at 0x7B5B64..0x7B5B7C; all seven values were verified "
                 "present in our image. Deliberately NOT investigated - recorded only as a lead. TEXT-HANDLE-001 "
                 "upgraded the structural claim: consumer 0x08012230 loads this very base as a literal "
                 "(0x08012242 ldr r1,=0x087B5B64) and indexes it by the packed handle's low 6 bits scaled by 4 "
                 "(0x08012248 ldr r0,[r1,r0]), so the table IS this region's container selector table and not "
                 "merely seven words that happen to be present. The seven values read from the canonical image "
                 "are [0]0x0879BF2C [1]0x087A04F0 [2]0x087A46C8 [3]0x087A8AD8 [4]0x087AD118 [5]0x087B1558 "
                 "[6]0x087B5AA0.",
        notes="Size = 7 * 4 = 28 bytes, derived from the stated inclusive range 0x7B5B64..0x7B5B7C. OLD "
              "'OBSERVED / no structural claim' grading is SUPERSEDED by TEXT-HANDLE-001: the consumer's own "
              "literal pool and indexed load make the table role CONFIRMED. STRUCTURAL GATE: exactly 7 "
              "containers. A live capture of 65 consumer hits selected only containers 0 and 1, and every hit "
              "decoded inside its container's bounds, so nothing observed argues for widening the gate; it must "
              "NOT be widened, because the 6-bit selector field can encode 64 values while only 7 are backed by "
              "a real pointer.")

    # ------------------------------------------- TEXT-HANDLE-001 packed handle
    # The packed compressed-text handle consumed from a runtime object's +0x04.
    # TEXT-HANDLE-001 asked which code WRITES it and measured that none does:
    # the "runtime object" pointer is a pointer INTO the ROM-resident dialog
    # record pool, so the field is already in the image and the record is its
    # durable owner. Producer stopping point A.
    add(addr=0x08012230, size=None, kind="function",
        identity="compressed_text.consumer_08012230",
        conf="RUNTIME_CONFIRMED",
        source="docs/research/BUU_EVENT_RESOURCE.md:35",
        evidence="Consumer of the packed compressed-text handle. The record object arrives in r1, NOT r0: "
                 "0x08012232 mov r5,r1; 0x08012240 ldr r0,[r5,#4] loads the packed handle from the object's "
                 "+0x04; 0x08012242 ldr r1,=0x087B5B64 loads the container table; 0x08012248 ldr r0,[r1,r0] "
                 "selects the container. The intervening 0x08012244 lsls #26 / 0x08012246 lsrs #24 isolate the "
                 "low 6 bits and scale them by 4, which is the selector-to-byte-offset conversion. Re-read from "
                 "the canonical image, the halfwords at 0x08012230 are B5F8 1C06 2001 1C0D 0400 F02B F9BD 1C04 "
                 "6868 4962 0680 0E00 5808, in which 1C0D is mov r5,r1 and 6868 is ldr r0,[r5,#4]. "
                 "TOOLKIT-031 captured 65 live hits at this site across frames 973..11367 covering 21 distinct "
                 "objects, every one of them a ROM address in the dialog record pool.",
        notes="size null: extent not measured. RUNTIME_CONFIRMED applies to the site EXECUTING and to the "
              "objects/handles observed there - both are in the capture "
              "(build/toolkit031/text-handle-001-target-01-20260912-1319/text-handle-001.jsonl). The r1 calling "
              "convention itself is a STATIC disassembly result that the capture assumes rather than proves: "
              "the capture latches the object from r1 at entry, so it could not have detected the object "
              "arriving anywhere else. The instruction bytes are the evidence for r1, and they are CONFIRMED "
              "strength, not runtime strength.")

    add(addr=0x080122B4, size=None, kind="function",
        identity="compressed_text.consumer_080122B4",
        conf="CONFIRMED",
        source="docs/research/BUU_EVENT_RESOURCE.md:35",
        evidence="Second consumer with the same access shape as 0x08012230: the object arrives in r1 "
                 "(0x080122BA mov r4,r1), and the handle is then read from its +0x04 and used to index the "
                 "0x087B5B64 container table. Re-read from the canonical image, the halfwords at 0x080122B4 are "
                 "B5F7 4B47 2001 1C0C 0400 449D F02B F97A 1C05 6860 4940 0680 0E00 5808, in which 1C0C is "
                 "mov r4,r1 and 6860 is ldr r0,[r4,#4] - the same load, one register different.",
        notes="size null: extent not measured. CONFIRMED and deliberately NOT RUNTIME_CONFIRMED: the "
              "TOOLKIT-031 capture recorded 65 consumer hits and ALL 65 were at 0x08012230. This site was armed "
              "and never observed executing, so its shape is proven from instruction bytes only. Do not read "
              "the sibling site's runtime evidence as covering this one.")

    add(addr=0x0801242C, size=14, kind="function",
        identity="compressed_text.opcode_05_handler_thunk",
        conf="RUNTIME_CONFIRMED",
        source="docs/research/BUU_DIALOG_RUNTIME.md:438",
        evidence="TEXT-HANDLE-002 captured ROM record 0x08781CF8 at this exact PC on 83 repeated hits, "
                 "with r1 = 0x08781CF8 and r5 = 0x080728AC. The selected table entry is raw Thumb "
                 "pointer 0x0801242D (fetch 0x0801242C). Its instructions preserve the record in r1 and "
                 "call 0x0801227E, which calls packed-handle consumer 0x08012230.",
        notes="The handler's executable key is record byte +0x02 = 0x05, not a full 0xNN05 halfword. "
              "Size 14 is the thunk 0x0801242C..0x0801243A, ending before the next push prologue.")

    add(addr=0x080124F8, size=None, kind="function",
        identity="compressed_text.opcode_05_dispatch_loop",
        conf="CONFIRMED",
        source="docs/research/BUU_DIALOG_RUNTIME.md:447",
        evidence="TEXT-HANDLE-002 static reading of the path observed at 0x0801242C: 0x08012556 ldrb "
                 "r0,[r1,#2], 0x08012558 lsls r0,#2, and 0x0801255A ldr r2,[r5,r0] select the entry. "
                 "For 0x05, r5=0x080728AC and table word 0x080728C0 is 0x0801242D. 0x0801255E calls "
                 "the 0x08046AA4 veneer, which is bx r2, entering fetch address 0x0801242C.",
        notes="Size null: the complete dispatcher extent was not measured. The confirmed relation is the "
              "one observed byte-2 dispatch branch only; no opcode census is implied.")

    add(addr=0x08781CF8, size=None, kind="other",
        identity="compressed_text.handle_owner_record_84",
        conf="RUNTIME_CONFIRMED",
        source="docs/research/BUU_EVENT_RESOURCE.md:35",
        evidence="TEXT-HANDLE-001 Producer stopping point A: there is NO runtime producer for the packed "
                 "compressed-text handle. A WRITE watchpoint armed for the whole capture recorded zero producing "
                 "writes, while the consumer read the value 65 times. The 'runtime object' the consumer receives "
                 "in r1 is 0x08781CF8, a ROM address lying inside the dialog record pool 0x0877C5A4..0x0879B704 "
                 "(BUU_EVENT_RESOURCE.md:35), so its +0x04 is ROM byte 0x781CFC and the value is already in the "
                 "image before the machine starts. All 21 distinct objects seen at the consumer are likewise "
                 "pool addresses in 0x087818C8..0x08781CF8. The ROM-resident record is therefore the durable "
                 "owner of the handle, and any edit must patch the record, not chase a writer.",
        notes="size null: this record's extent was not measured; it is identified by the pointer the consumer "
              "receives, not by a record census. This is the structural answer to TEXT-HANDLE-001 and it is a "
              "NEGATIVE result about producers, which is why the WRITE watchpoint's silence is quoted as "
              "evidence rather than omitted. The record is dialog record 84 and the handle sits at its +0x48; "
              "record numbering is from the 522-entry pointer table at 0x0879B704. TEXT-HANDLE-002 additionally "
              "confirmed the live dispatcher reaches this record's byte-2=0x05 thunk, whose consumer loads +0x04 "
              "as the packed handle.")

    add(off=0x781CFC, addr=0x08781CFC, size=4, kind="other",
        identity="compressed_text.handle_0x02002641",
        conf="RUNTIME_CONFIRMED",
        source="docs/research/BUU_EVENT_RESOURCE.md:35",
        evidence="Packed compressed-text handle 0x02002641, stored little-endian as bytes 41 26 00 02 at file "
                 "offset 0x781CFC, read back from the canonical image. Bit layout, corroborated in situ by the "
                 "consumer's lsls #26 / lsrs #24 at 0x08012244/0x08012246: bits 0-5 selector, table byte offset "
                 "= (v & 0x3F) * 4; bits 6-20 decoded start, bytes = ((v >> 6) & 0x7FFF) * 2; bits 21-31 length, "
                 "bytes = (v >> 21) * 2. Decoding 0x02002641 by that layout gives selector 1 -> container "
                 "0x087A04F0, decoded start 0x132, decoded length 0x20. Two independent surfaces agree: the live "
                 "capture decoded exactly those values at all 41 hits carrying this handle, and the atlas's own "
                 "decoded-container index independently reports container_index 1, "
                 "decoded_offset_of_phrase 0x132 and char_count 16 (= 0x20 bytes) for the phrase "
                 "'Good luck, Goku!'.",
        notes="IDENTITY IS PER-TEXT, NOT PER-SITE. The word 0x02002641 occurs word-aligned exactly three times "
              "image-wide - 0x08781C4C (record 83 +0x58), 0x08781CB0 (record 83 +0xBC) and 0x08781CFC "
              "(record 84 +0x48) - and this row is emitted once, at the site the capture actually read. The "
              "other two are additional REFERENCE/PATCH SITES for the SAME message identity, not two further "
              "messages: all three decode to the same container, offset and length, so re-pointing this text "
              "means patching three words, while renumbering it as three messages would be wrong. Size 4 is the "
              "handle word itself, not the text it addresses; the decoded bytes live in container 0x087A04F0.")

    # Selector-0 is included because it is what makes the 6-bit selector field a
    # real structural claim rather than a one-container coincidence: without a
    # second container observed, the selector bits could not be distinguished
    # from padding that happens to be zero.
    add(addr=0x0879BF2C, size=None, kind="compressed_stream",
        identity="compressed_text.container_0_selector_evidence",
        conf="CONFIRMED",
        source="docs/research/BUU_MAP_EVENT_REFERENCES.md:246",
        evidence="Container 0 of the seven-entry table, exercised by the selector field. Of the 21 distinct "
                 "objects seen at consumer 0x08012230, 20 carried handles selecting container 0 and one selected "
                 "container 1, so both a zero and a non-zero selector were observed decoding correctly through "
                 "the same field. Container 0 decompresses to 65,348 bytes; all 19 tested (start,length) pairs "
                 "decoded to literal readable English NPC dialogue, each range beginning on a sentence boundary "
                 "and ending on terminal punctuation, which is what a correct start/length interpretation looks "
                 "like and what an off-by-N interpretation does not. The atlas's decoded-container index "
                 "independently places the phrase 'five million pushups' at container_index 0, "
                 "decoded_offset_of_phrase 0xE2FC, exact match.",
        notes="This row records DECODE evidence for a stream whose start was already seeded as "
              "compressed_text_region at CANDIDATE from an upstream source; it does not restate the extent, "
              "which is still unmeasured, and it does not supersede that row. Counting note: the 20-of-21 "
              "figure counts DISTINCT OBJECTS, not consumer hits - by hit the same capture is 24 selector-0 and "
              "41 selector-1, because the single container-1 object was re-read 41 times. Both denominators are "
              "recorded so neither is mistaken for the other.")

    # ---------------------------------------------------------- rejected tail
    add(off=0x007B89A8, addr=0x087B89A8, size=0x00800000 - 0x007B89A8, kind="other",
        identity="upstream_tail_candidate",
        conf="UNKNOWN",
        source="docs/research/FREE_SPACE_RELOCATION.md:39",
        evidence="Pinned exact-match disassembly identifies candidate tail file [0x007B89A8, 0x00800000), "
                 "292,440 bytes, but INCBINs it rather than proving unused sections. Canonical bytes are FF. "
                 "All-byte u32 audit finds 516 unresolved CANDIDATE references, 99 word-aligned sources.",
        notes="SUPERSEDED by TOOLKIT-028: the whole region stays REJECTED and verified capacity from it is zero; "
              "only the carved 256-byte window [0x7EA400,0x7EA500) is CONFIRMED free "
              "(docs/PROJECT_<local-state-name>:200). Emitted as UNKNOWN so the atlas records that these 292,440 bytes "
              "are FF-filled but NOT usable, and that FF fill does not imply free space. CONTAINS the verified "
              "free region and the authored rows above - genuine nesting.")


    rows.sort(key=lambda r: (r["file_offset"], r["identity"]))
    return rows


def build(out_dir: Path) -> Path:
    """Write `seed_knowledge.jsonl` into `out_dir`. Reads nothing."""
    path = Path(out_dir) / "seed_knowledge.jsonl"
    write_jsonl(path, _rows(), sort_keys=False, compact=False, ensure_ascii=False)
    return path
