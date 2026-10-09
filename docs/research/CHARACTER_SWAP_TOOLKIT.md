# The character-swap toolkit

One command to redraw a character's sprites or portrait in a friend image, or to rewrite spoken
lines in it. The two engines are pure (bytes in, bytes out); the front end owns the file system.

```powershell
python -m tools.webfoot.character_swap --image IN.gba --expect-sha256 <hex> --spec swap.json --out OUT.gba
```

An optional `--report report.json` writes the full account: every container touched, every
handle rewritten, the diff confinement, and the read-back.

## The spec

Asset names resolve against the spec file's own directory, so a swap directory is
self-contained.

```json
{
  "operations": [
    {"kind": "sprite", "sprite_id": 41,
     "slots": [{"slot": 0, "sheet": "stand.png", "frames": 2},
               {"slot": 1, "sheet": "walk.png", "frames": 4},
               {"slot": 12, "sheet": "arms_up.png", "frames": 2}],
     "frame": [16, 32], "cell": 32, "crop_x": 8,
     "anchor": [0, -24], "composition_size": 512},
    {"kind": "portrait", "slot": 17, "png": "portrait.png", "side": 64},
    {"kind": "dialogue", "selector": 2,
     "lines": [{"speaker": "tulma",
                "old": "the wording the record holds now",
                "new": "the wording to write",
                "record": [60182, 112]}]}
  ]
}
```

`frame`, `cell`, `crop_x`, `anchor` and `composition_size` are optional and default to the
geometry every donor measured so far uses: one 16x32 piece at anchor (0,-24) in the 16-wide
window at x=8 of each 32x32 sheet cell.

A sheet is one row of square cells, one cell per (direction, frame) in direction-major order.
A sprite's run index in the registry is its id minus ten. A portrait's `side` defaults to 64,
and the slot's container must declare exactly that many bytes.

## What a dialogue line means, and what it does not

A target is a record, never a string.

- The line is found by the wording it holds now. That wording must match **exactly one** record.
  No match is refused. More than one match is refused, with every candidate named. The first
  match is never picked.
- `record` may state the span as `[decoded start, decoded length]`. It is not a second opinion:
  if it disagrees with the wording's own single match, the run is refused.
- `speaker` is a **caller claim**. The speaker is the scene's actor, which is not a property of
  the text record, so this toolkit records the claim and reports the evidence a human needs to
  check it: every word that names the record, and every record whose span encloses it. Nothing
  derives a speaker from a name, a label or a position.

## What it refuses

The base digest, a spec with no operations or an unknown operation kind, a sprite with no slots,
a dialogue edit with no lines, a wording no record holds, a wording two records hold, a stated
span that contradicts the wording, a replacement carrying a control unit, dialogue records that
are not adjacent, a group with too little room, a container that is not the stored form, a
handle word that is not the one being replaced, a portrait slot whose declared size does not
match the raster, and a destination that is the source or any filesystem alias of it, including
a hard link. Every refusal leaves the source byte-identical.

## The two rules the front end owns exactly once

- **The source is an input on every path and an output on none.** Checked by file identity
  before the image is read, so a hard link of the verified image cannot be written through.
- **An image and a report are staged into sibling temporary files and renamed into place**, so a
  reader never sees a partial write.

Both live in `tools/webfoot/character_swap.py::guarded_apply`, which the ticket presets call
too, so there is one implementation rather than one per writer.

## Reproducibility, the acceptance for this toolkit

Driven by the same inputs, the front end reproduces the ticket that first needed it, byte for
byte, and so does the preset path. From the friend v3 text-pass image `20f2c140`:

| path | command | result |
| --- | --- | --- |
| sprite and portrait, preset | `python tools/research/apply_tulma_graphics.py` | `ef939dcd` |
| sprite and portrait, spec | `character_swap --spec graphics-spec.json` | `ef939dcd` |
| two lines, preset | `python tools/research/apply_tulma_dialogue.py` | `a4c12a95` |
| two lines, spec | `character_swap --spec dialogue-spec.json` | `a4c12a95` |

The first and third are `FRIEND-V3-TULMA-GRAPHICS-001`'s candidates, which were confirmed on
screen. The second and fourth prove the generalized path is the same path.

## Layout

| file | what it owns |
| --- | --- |
| `tools/webfoot/sprite_swap.py` | the graphics engine: geometry, the donor walk, the container plan, placement, and the diff and reopen checks |
| `tools/webfoot/dialogue_edit.py` | the dialogue engine: record matching, the region re-layout, handle rewriting, and the read-back |
| `tools/webfoot/character_swap.py` | the spec, the invocable command, the source-alias guard and the staged write |
| `tools/research/apply_tulma_graphics.py`, `tools/research/apply_tulma_dialogue.py` | that ticket's own invocations of the above, kept so its measurements stay reproducible |

## What is not claimed

A swap is pixels and, for dialogue, wording. Nothing here proves who speaks a line, moves an
animation, changes a palette entry or a frame rectangle, edits a packed (non-stored) dialogue
container, or grows a container. A dialogue replacement that does not fit its records' combined
region is refused, because that is a container re-layout and a different mechanism.

The toolkit's modules live in `tools/webfoot/`, which another lane was writing at the time this
was built. The three new module paths are claimed in the cross-session ledger, no file that lane
holds is modified, and there is no SDK module registry to join; if one appears, these modules
must be registered there by whoever introduces it.
