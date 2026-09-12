# Buu's Fury dialogue text stores

Measured against canonical `buus_fury_usa_rev0_01c1707f`, sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, verified
unchanged before and after every runtime run below.

TOOLKIT-037 asked whether ordinary in-game dialogue can consume relocated
authored text through TOOLKIT-036's storage mechanism. It cannot, and the
reason is not a missing edge in the reference graph.

## Headline

**Spoken NPC dialogue is not stored in the `text_strings` table.**

```
text_strings 0x0806BCE8   ->  menus, items, equipment, bestiary, quest objectives
0x0877F09A..0x087801D4    ->  shop NPC dialogue with menu choices   (UNOWNED)
0x086B7400..0x086B758E    ->  developer assertion strings           (UNOWNED)
```

Evidence class: **CONFIRMED_ROM** for the census, **CONFIRMED_RUNTIME** for the
consumer separation.

## 1. What the declared table actually contains

`text_strings` is 1,534 entries of UTF-16LE at pointer table `0x0806BCE8`,
pool `0x0805792C`, and TOOLKIT-004 verified its codec. This ticket censused its
*content* rather than its format, which no prior ticket had done.

Filtering all 1,534 entries for conversational shape returns item flavour text,
prompts and bestiary bios. Not one entry is a line of character speech.

Entries 613-632 are a contiguous **quest-objective block**, which is the
closest the table comes to narrative text:

```
text:0613  A New Beginning
text:0614  Go to King Yemma's Castle
text:0619  Fight Crime in Hercule City
text:0622  Tell Your Mother That Goku's Coming Back
text:0623  Tell Piccolo and Dende That Goku's Coming Back
text:0630  Find Babidi's Spaceship
```

These are journal/objective lines, not dialogue. The operator confirmed
independently that text 623 is quest text and was never on screen during the
capture.

## 2. Runtime consumer separation

Two instrumented sessions on map 39, read-only observer
`tools/runtime/toolkit037_dialogue_watch.lua`, mGBA 0.11 dev build.

Run `t037-run2`, 399 rows, operator playing normally (NPC interactions,
chests, equipment menu):

| Channel | Site | Hits |
|---|---|---:|
| DIALOGUE (struct field state) | `0x03003AE4` | 300 |
| ALT-SLOT (struct field state) | `0x03003A3C` | 29 |
| **TEXT-FETCH (execution)** | **`0x0802BFBC`** | **0** |
| LIVENESS (execution control) | `0x08004038` | 3 |

**23 distinct semantic text indices were consumed and zero indexed table reads
occurred.** Liveness confirms the breakpoints were installed, so the negative is
real rather than an unproven instrument (skill rule 8).

Observed indices: 3, 87, 213, 220, 295, 377, 432, 548, 623, 745, 882, 897, 986,
1033, 1035, 1040, 1119, 1219, 1229, 1309, 1325, 1333, 1531.

Every sampled body decoded and reconciled byte-exact against the toolkit's own
`text show`, including its offset into the owning entry. Examples:

| Index | Runtime body | Offset | Decoded |
|---:|---|---:|---|
| 1229 | `0x080675A3` | +23 | `soldier of fortune. Armed with rocket propelled grenades.` |
| 213 | `0x08058B32` | +24 | `l samurai armor carved out of stone.` |
| 1325 | `0x080698F4` | +102 | `ile of internal energy.  Press the B Button...` |

### The engine walks a cursor, it does not re-index

Text 623 was observed at `+58, +50, +42, +34, +26, +18` into its own body across
consecutive frames. The consumer holds a **moving pointer into the body** and
advances it, which is a typewriter reveal. That is why no indexed table read
occurs during display: the index is resolved once, before the window this
observer could see, and the visible work is cursor advancement.

`0x03003AE4` and `0x03003A3C` are fields of one structure based at
`0x03003898`. That base has 83 word-aligned references, 12 in low ROM code
(`0x08054FC0`, `0x080561C4`, `0x080561E0`, `0x0807013C`, `0x0807014C`,
`0x08070160`, `0x08070168`, `0x08070184`, `0x08071C94`, `0x080725B8`,
`0x080725E0`, `0x08072828`). `0x03003AE4 - 0x03003898 = 0x24C`.

That consumer cluster (`0x08070000`-`0x08072FFF`) is disjoint from slot 178's
text path (`0x0802Bxxx`). **Not claimed**: that these are the same subsystem, or
which routine writes the field. Neither was pinned down.

## 3. Whole-image UTF-16 census

A stride-1 sweep of all 8,388,608 bytes for NUL-terminated UTF-16LE ASCII runs
found 2,000 candidate runs in 17 clusters. Filtering for genuine prose (a
3+ letter word, a vowel, and a space) reduces this to **three** regions:

| Region | Extent | Strings | Content |
|---|---|---:|---|
| Declared pool | `0x0805794A..0x0806BCE4` | 1,213 | the known table |
| **Shop dialogue** | `0x0877F09A..0x087801D4` | 22 | **NPC speech + menu choices** |
| Assertions | `0x086B7400..0x086B758E` | 3 | developer debug strings |

The other 14 clusters are **false positives**: sequential byte values in tile
and map index data that coincidentally match the ASCII-plus-NUL pattern. They
are recorded here so a later pass does not re-investigate them.

### The shop dialogue region

Uncompressed UTF-16LE, same encoding as the declared pool, different location.
Speech is interleaved with its menu options:

```
0x0877F09A  Welcome to the Hercule City Z-Mart! How can I help you?
0x0877F10C  -Buy
0x0877F116  -Sell
0x0877F124  -End
0x0877F132  A fine day to you, good sir. What would you like from my humble shop?
0x0877F788  Welcome to the black market! You can spend your loot here.
0x0877F8D0  You think you can impress me with them fancy-schmancy clothes? Get real!
0x0877FBDE  Hmm, quite the dapper lad, aren't you? Have a look at our wares.
0x08780128  -Food Items
0x0878015A  -Body Equipment
```

This is a **conversational dialogue system with branching choices**, and it is
the shape TOOLKIT-037 was sent to find.

**Nothing else about it is proven.** No pointer table, no consumer, no ownership
measurement, no relocation eligibility, and no runtime observation. The Z-Marts
are not on map 39, so no capture in this ticket touched it.

### The assertion region

```
0x086B7400  "Energy attack level set for attack which doesn't exist for player!"
0x086B748C  "Energy attack level requested for attack which doesn't exist for player!"
0x086B7524  "Unable to find sprite index in character state data"
```

Leftover developer diagnostics. No gameplay role. Recorded for posterity only.

## 4. Why the static corpus looked the way it did

TOOLKIT-020 censused all 107 native slots and found exactly one reaching the
text table: slot 178, OAM sprite text. TOOLKIT-021 walked all four
map-reachable dialogs to depth 10 with positive controls and found none
reaching text, recording `map -> placement -> event -> dialog -> text` as
NOT ESTABLISHED.

Re-measured at HEAD this pass, both hold:

- map to dialog: **17 references, 4 dialogs** (393, 506, 508, 509)
- dialog to text: **7 references, 7 dialogs** (290, 291, 292, 295, 296, 297, 298)
- intersection: **empty**. `event consumers-of` returns no maps, placements or
  events for all seven text-bearing dialogs.

Those tickets were not missing an edge. **The chain does not close because
spoken dialogue is not in that table**, so no amount of graph walking inside it
could have reached speech.

## 5. Capability boundary

| Layer | Status |
|---|---|
| `text_strings` content is menu/item/objective, not speech | **CONFIRMED_ROM** |
| Ordinary text display does not use the indexed table read | **CONFIRMED_RUNTIME** |
| Consumer holds a walking cursor at `0x03003898 +0x24C` | **CONFIRMED_RUNTIME** |
| Whole-image UTF-16 census, 3 genuine regions | **CONFIRMED_ROM** |
| Shop dialogue region exists and decodes | **CONFIRMED_ROM** |
| Shop region pointer table | **UNKNOWN** |
| Shop region consumer | **UNKNOWN** |
| Shop region ownership / relocation eligibility | **UNMEASURED** |
| Which routine writes `0x03003AE4` | **UNKNOWN** |
| Compressed region `0x0879BF2C` | **CONFIRMED_RUNTIME** (TEXT-HANDLE-001: reached, decodes to NPC dialogue) |
| Relocated authored dialogue | **NO** |

## 6. Next measured blocker

> The shop dialogue region `0x0877F09A..0x087801D4` has no located pointer
> table and no identified consumer, so TOOLKIT-036's per-entry relocation gate
> (exactly one word-aligned inbound reference, and that reference is the entry's
> own table slot) cannot be evaluated against it.

That is a better target than the compressed region at `0x0879BF2C`: it is
uncompressed. (`0x0879BF2C` is also reached and decodes to real NPC dialogue --
TEXT-HANDLE-001 -- so decoding is no longer what separates the two.)
