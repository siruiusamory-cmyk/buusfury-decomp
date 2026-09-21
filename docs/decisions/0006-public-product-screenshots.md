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
