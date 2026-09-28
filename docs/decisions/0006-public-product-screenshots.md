# ADR 0006 - Public product screenshots

- **Status:** accepted (2026-09-21)
- **Evidence:** `WEBFOOT-SITE-VISUAL-DIRECTION-PASS-001`
  ([record](../tickets/archive/WEBFOOT-SITE-VISUAL-DIRECTION-PASS-001-COMPLETE.md),
  "Context delta" and "Known limits");
  [`docs/DEVELOPMENT.md`](../../docs/DEVELOPMENT.md) ("Original ROM Safety - Mandatory");
  `public/dbz-map-browser.png`, `public/dbz-layout-editor.png`.

## Decision

Real screenshots of DragonByte Z **in use may be committed and published** for
project documentation, project status and product demonstration, **when the
owner has explicitly approved them** - including screenshots in which the real
application visibly renders game content.

The first two published captures were approved individually on those terms: the
Map Browser capture shipped byte-identical to its source
(SHA-256 `f846aea3...a61671`) and the Edit Layout plate is an exact unscaled crop
of a second capture (SHA-256 `4af08ab2...d9862e`), both real captures of the real
application.

### Superseded 2026-09-27

Both of those files were replaced, because the 2026-09-22 visual-direction pass
changed the shipped shell (four primary editors and the Maps editor's modes) and
the application theme, so the published plates showed a window the product no
longer opens. The replacements were approved individually by the owner, captured
from the real application over the verified canonical ROM with
`tools/qa/visual_pass_capture.py`'s harness:

| Shipped path | Capture | Transform | SHA-256 of the shipped file |
| --- | --- | --- | --- |
| `public/dbz-map-browser.png` | Maps editor, Browse mode, `map:0040`, 1700x1264 | none | `849fe570...810a2e9` |
| `public/dbz-layout-editor.png` | Maps editor, Layout mode, `map:0040` BG1, one staged paint | crop of the Inspector pane, x=1399 y=86 w=301 h=746 | `36b24698...0e9dba` |

The two files above remain the record of the first approval and their SHAs are
history, not the current assets. This section is an instance of the decision, not
a new one, and it widens nothing in the "what this does not authorize" list.

## What this does not authorize

Recorded so the scoped approval cannot be read more widely than it is. This ADR
does **not** authorize committing:

- ROM files;
- standalone extracted commercial graphics;
- reusable tiles, sprites or maps;
- decompressed proprietary blobs;
- commercial asset packs.

`docs/DEVELOPMENT.md` continues to forbid all of those without a new owner decision, and
no later reader may treat the approved screenshots as having created that
decision. `public/` holds the approved PNGs and the pre-existing hand-written
favicon, and nothing else.

## Context

Project documentation and product status need to show the real application, and
a screenshot of a ROM editor necessarily contains rendered commercial game
graphics. That collides with a rule whose purpose is to keep commercial ROM
content out of version control. It was resolved by asking the owner and
recording the answer rather than by quietly interpreting the rule, because the
alternative - a rule that everyone understands to be bent - is worse than a
narrow, explicit exception.

## Consequences

- **Approval is per asset and explicit.** A screenshot is not publishable
  because an earlier screenshot was; the owner approves each one.
- **No claim that copyright is absent.** These are third-party commercial
  graphics rendered by the real application, published for project
  documentation under the owner's approval. Nothing in the repository asserts a
  licence, a waiver or a public-domain status for that content.
- **Publication hygiene still applies**: prefer crops that show the
  application's own surfaces, do not use the captures as an asset source, and do
  not derive reusable game art from them.
- Generative or invented "application screens" are not a substitute and are not
  permitted; the sanctioned images are real captures, and where a real capture
  has a defect (a rendering seam, an illegible panel at small sizes) the correct
  response is to record it, not to fabricate a cleaner one.
- The next DragonByte Z desktop visual pass is a separate, later decision; this
  ADR governs what may be published about it, not what it may change.
