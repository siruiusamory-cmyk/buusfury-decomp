# Text files and line endings

This repository has **no line-ending policy**. `.gitattributes` contains only
`*.patch -whitespace`; `core.autocrlf`, `core.eol` and `core.whitespace` are all
unset. Tracked blobs therefore carry whatever endings their author's editor
produced, and some of them are mixed.

Measured on `origin/master` (`git cat-file` on the blobs, 609 tracked files):

| kind | count | notes |
| --- | --- | --- |
| bare LF only | 593 | the overwhelming majority |
| CRLF only | 7 | includes `docs/DEVELOPMENT.md` and `docs/DEVELOPMENT.md` |
| mixed | 9 | CRLF-dominant with interspersed bare-LF lines |

The mixed files on `origin/master` are `config/roms.yaml`,
`src/data/project.ts`, `tests/unit/test_mgba_capture.py`,
`tools/runtime/inject_mgba_lua.ps1`, `tools/runtime/p002_walk_probe.lua`,
`tools/runtime/p003_hit_dump.lua`, `tools/webfoot/data/roms.yaml`,
`tools/webfoot/profile.py` and `tools/webfoot/project/model.py`.

## The one rule

**Never rewrite the ending of a line you did not otherwise change, and write
every line you add with a bare LF.**

That single rule keeps the diff minimal and keeps `git diff --check` clean in
every case, including inside a CRLF-only or already-mixed file. `git diff
--check` treats a `CR` before the newline of an **added** line as trailing
whitespace (there is no `cr-at-eol` in `core.whitespace`), so CRLF added lines
fail it even when the file is CRLF-only throughout. It cannot see the `CR` on
*unchanged* lines, which is why the mixed state at `HEAD` is invisible to it.

Adding LF lines to a CRLF-dominant file produces another mixed file. That is
the established outcome here, not a defect: 9 tracked files are already mixed
for exactly this reason.

## What goes wrong

The failure is always the same shape: a tool round-trips the file through a
newline-translating API and rewrites **every** line, so the diff becomes the
whole file.

- Python `Path.read_text()` / `open(..., "r")` use universal newlines and
  silently turn `\r\n` into `\n`; a later `write_text()` then emits LF for the
  entire file. This is the single most common cause.
- The `edit`/`write` file tools may normalise endings on files they touch.
- PowerShell `Set-Content` and `Out-File` emit CRLF, `Get-Content | Set-Content`
  round-trips, and both mangle LF-only files.

## Detect it before you commit

```text
git diff --numstat                    # equal add/delete counts for a whole file
git diff --ignore-cr-at-eol --stat    # empty output means pure ending churn
git diff --check                      # CR on an ADDED line = trailing whitespace
```

If `--ignore-cr-at-eol` reports no change but the plain diff shows hundreds of
lines, you converted endings. Restore the file and redo the edit byte-safely.

## Byte-safe editing recipe

```python
raw = path.read_bytes()
text = raw.decode("utf-8")
lines = text.split("\n")        # a line keeps its trailing "\r" if it had one
tail = lines.pop()              # "" when the file ends with a newline
assert tail == ""
# replace whole lines by index (index i is lines[i - 1]);
# every replacement line is written WITHOUT a trailing "\r"
path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
```

Apply multiple regions in **descending** line order so earlier indices stay
valid, and assert on the content of each region before writing.

## Do not "fix" endings as a side effect

A repo-wide CRLF/LF normalisation is a separate, deliberate decision. It is
**not** an acceptable side effect of an unrelated change, and it must never be
committed inside a feature or ticket branch: it destroys reviewability and
buries the real change. If you find a worktree full of pure ending churn, report
it; do not commit it.
