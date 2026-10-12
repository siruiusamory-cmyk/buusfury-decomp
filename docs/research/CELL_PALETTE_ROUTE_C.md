# Route C: a per-actor palette for a custom actor

Owner decision: Perfect Cell gets his own colours as a REUSABLE mechanism. This note is step 1: what the engine
does today, where a dedicated palette can live without touching another actor's colours, how the Legacy of Goku
II art converts, and the interface a future actor would use. Nothing here is built.

Every claim below is measured. Canonical Buu's Fury sha256
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`; Legacy of Goku II sha256
`6E6C370C339EC9171CB1956ADF837A0D342A197F78964882EF46C3086656FF75`.

## 1. How the engine selects an actor's palette and depth today

**Depth is 8bpp, everywhere, and it is a global property of the OBJ layer.** The piece attribute word carries the
256-colour flag at bit 13, and every one of the 11,005 sampled pieces carries it. Across twelve actors the only
attribute words seen are `0xC0002000`, `0x80002000`, `0x8000A000`, `0xD0002000`, `0x90002000` and three more,
all with bit 13 set.

**The actor-to-OAM path never writes the palette-bank bits.** In `0x0800F24C`..`0x0800F2BE` the piece word is
stored verbatim into the first OAM word, then X and Y are computed into it, and `attr2` receives only the tile
index (bits 0 to 9) and priority (bits 10 and 11). Bits 12 to 15 of `attr2`, the palette bank, are never set.
That is consistent with 8bpp, where those bits are ignored.

**So there is one 256-entry OBJ palette for the whole screen.** A per-actor palette does not exist and cannot be
created while the layer is 8bpp. The relevant hardware fact is that the OBJ character mode is global (DISPCNT
bit 12), so one actor cannot be 4bpp while the others are 8bpp.

**The same is true of the background side.** All thirty `BGxCNT` writes in the image set bit 7, which is 8bpp.
There is **no 4bpp background precedent anywhere**; the only 4bpp value present is the power-on default, which no
code site writes and which is shown only under forced blank. And every palette transfer is exactly one full
256-entry bank (`0x200` bytes): eleven sites load `0x0805652C` into the BG palette, twelve into the OBJ palette,
one site loads `0x0805632C` into the BG palette, and the rest fill with zero. No scene has more than one
16-colour palette resident.

**The map scene uses all four background layers.** Programmer `0x0800938C` writes `BG0CNT` to `BG3CNT` from a
table row (`0x080716D8` = `0x1C80 0x1D80 0x1E80 0x1F80`, i.e. screen bases 28 to 31, character base 0, 256x256)
plus a per-map priority addend, and then `DISPCNT` from the map context shadow at `ctx+0xA2`. Runtime readings
in this repository show `DISPCNT 0x1F40` (mode 0, BG0 to BG3 on, OBJ on) with `BG0CNT 0x1C82`, `BG1CNT 0x1D82`,
`BG2CNT 0x1E83`, `BG3CNT 0x1F83`. Fights in this engine run on the map scene: there is no separate battle video
programmer.

## 2. Where the colours can live without touching another actor

The rule is that no other actor's appearance may change. Combined with the measurements, the options are:

| route | verdict |
| --- | --- |
| per-actor palette on the OBJ layer | **not possible.** The OBJ layer is 8bpp and the palette bits are ignored there, so the only way is a global mode change, which would break every actor painting more than 16 indices |
| switch the OBJ layer to 4bpp and give every actor a bank | **forbidden by the rule.** Measured colours per actor: 47 paints 75, 72 paints 83, Spopovich 42, 43 paints 46, 31 paints 35, 104 paints 23 |
| a custom actor rendered on a 4bpp BACKGROUND layer | **the only route that satisfies the rule**, and it is a new path because no 4bpp background exists today |
| a per-scene palette swap, scoped to Cell's scenes | that is route A, which the owner rejected because it recolours other actors sharing his indices |

For the background route, the constraint that replaces "a dedicated palette slot" is sharper and more honest:
**the background palette is one shared 256-entry bank**, so Cell's palettes would be 16-entry ranges of a bank
that map tiles also index. Choosing such a range is safe only where nothing else on screen paints those
entries, which is a measurable property of each scene, not an assumption.

## 3. The art conversion, measured

Cell's Legacy of Goku II art is 24 records, 17 distinct 4096-byte containers, 64x64 at one byte per pixel,
painted with **22 distinct indices**:

```
0, 1, 2, 10, 11, 13, 14, 23, 36, 42, 97, 112, 120, 124, 129, 132, 152, 209, 211, 222, 229, 248
```

Cutting all 1536 of his 8x8 tiles and counting colours per tile:

| colours in the tile | tiles |
| --- | --- |
| 1 | 156 |
| 2 | 50 |
| 3 | 174 |
| 4 | 326 |
| 5 | 195 |
| 6 | 227 |
| 7 | 210 |
| 8 | 90 |
| 9 | 72 |
| 10 | 30 |
| 11 | 4 |
| 12 | 2 |

**No tile needs more than 12 colours, and zero tiles need more than 16.** So a 4bpp layer's per-tile palette
selection holds the art. A greedy cover over the 1536 tiles needs **four** 16-colour palettes, with every tile
covered and none left unassigned:

| palette | colours |
| --- | --- |
| 0 | 0, 1, 2, 10, 11, 14, 36, 42, 112, 120, 129, 132, 209, 211, 229, 248 |
| 1 | 0, 1, 11, 13, 14, 42, 97, 112, 120, 129, 132, 152, 209, 211, 222, 229 |
| 2 | 0, 1, 2, 11, 13, 14, 23, 42, 97, 112, 120, 129, 132, 211, 229, 248 |
| 3 | 0, 1, 11, 13, 14, 23, 42, 97, 124, 129, 132, 209, 211, 222 |

Four of the sixteen a 4bpp layer offers, leaving twelve for future actors. Each palette needs its colours
converted from the Legacy of Goku II bank to this image's values, and since the four sets overlap, a tile's
palette assignment also decides how its shared colours resolve; the converter must therefore pin shared entries
(for example index 0 and 1) so nothing flickers between tiles.

## 4. The interface a future actor would use

1. A per-definition marker: this actor renders from a 4bpp tile layer with palette set N, instead of through the
   OBJ path.
2. A converter that takes indexed art plus a palette list and emits 4bpp tiles with per-tile palette ids,
   asserting that no tile exceeds 16 colours, and reporting the palettes it needed.
3. A renderer the actor system calls instead of the OBJ path: build the tilemap from the frame's pieces, upload
   the tiles and the tilemap, place the layer, and sort its priority against OBJ actors.
4. Any later actor then ships art plus palettes and needs no engine change.

## 5. Size estimate

| piece | estimate |
| --- | --- |
| art to 4bpp with per-tile palette assignment and the 16-colour assertion | 80 to 120 lines, reusing the existing port tooling |
| the tile-layer actor renderer: tilemap build, tile upload, placement, priority against OBJ actors | 400 to 700 lines plus tests, a new subsystem |
| the two censuses below, which decide the palettes and the layer | 100 to 150 lines, both static |
| engine wiring: choose the layer and the palette range for Cell's scenes, load them at scene entry | small, once the censuses answer |
| runtime proof: a visible emulator run showing Cell in his own colours with the rest of the scene unchanged, plus a before/after census of every actor and background tile on screen | one session |

## 6. What must be measured before building, in order

1. **Background palette indices in use, per scene.** Which of the 256 entries the map layers actually paint in
   Cell's scenes, so a 16-entry range can be chosen that nothing else uses. This is the measurement that makes
   the rule provable rather than assumed. Shape: the existing palette census, pointed at background tiles.
2. **Layer occupancy per map.** All 452 map roots carry four non-null layer slots, so "free layer" is a content
   question: which screen blocks of BG2 and BG3 are actually populated. Static, through the map layer records.
3. **A per-tick register dump inside a fight**, to confirm the fight runs the map video state rather than a
   distinct one. The repository already holds map-scene readings; a fight reading is the missing one.
4. **The OAM cursor target**, one breakpoint, to be sure the component the renderer must not disturb is known.

## 7. Recommendation

Proceed with the background-layer route, but only after measurement 1, because that is the one that decides
whether the rule "no other actor's appearance changes" can be proven for the palettes. If measurement 1 shows no
clean 16-entry range in Cell's scenes, the honest fallback is the quantised approach: remap Cell's art onto the
existing bank's nearest colours, which changes nothing else by construction and accepts approximate colour, and
that is a different owner decision.
