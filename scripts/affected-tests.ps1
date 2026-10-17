param(
    # The commit, branch or ref the change is measured from.
    [Parameter(Mandatory, Position = 0)][string]$Base
)

# Print the test files a change since <base> can reach. The union of two rules:
# a test file that imports a module changed since <base>, and a test file whose
# source names a class, function or assigned name defined in a changed file - a
# name reached through a re-export counts, and so does one imported under an
# alias, because the original name is recorded beside it. It matches names in
# the source: an object reached without naming it, through getattr or a string,
# is not seen. It prints; it never runs the suite. Only tracked changes are
# measured: `git diff --name-only` says nothing about an untracked file until it
# is added.

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path

$python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    $command = Get-Command python -ErrorAction SilentlyContinue
    if (-not $command) { throw 'affected-tests.ps1: no interpreter; run scripts\setup.ps1' }
    $python = $command.Source
}

$code = @'
import ast
import subprocess
import sys
from pathlib import Path

base = sys.argv[1]

# The repository is the one this invocation is standing in. Found by walking up to
# `.git` rather than by `git rev-parse --show-toplevel`: the git on this machine's
# PATH is msys2's, which answers that question in POSIX form (`/c/...`) and Python
# then cannot open it. Every git call below runs with the repository as its cwd.
root = Path.cwd()
while not (root / ".git").exists() and root != root.parent:
    root = root.parent
if not (root / ".git").exists():
    raise SystemExit("affected-tests.ps1: not inside a git work tree")

result = subprocess.run(
    ["git", "diff", "--name-only", base, "--"],
    cwd=root, capture_output=True, text=True,
)
if result.returncode != 0:
    sys.stderr.write(result.stderr)
    raise SystemExit(result.returncode)
changed = [line.strip() for line in result.stdout.splitlines() if line.strip()]


def module_of(relative):
    if not relative.endswith(".py"):
        return None
    parts = relative[:-3].split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


modules = {path: module_of(path) for path in changed}
modules = {path: name for path, name in modules.items() if name}


def definitions(path):
    if not path.endswith(".py"):
        return set()
    file = root / path
    if not file.is_file():
        return set()
    tree = ast.parse(file.read_text(encoding="utf-8"))
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


#: Every name a changed file defines. A consumer that reached one through a
#: re-export names it too, and that is the case the import scan cannot see.
defines = set()
for path in changed:
    defines |= definitions(path)


def imports_of(tree):
    targets = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                targets.add(node.module if alias.name == "*" else node.module + "." + alias.name)
    return targets


def names_of(tree):
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.alias):
            # An alias hides the name the changed file contributes, so keep both.
            names.add(node.name.rsplit(".", 1)[-1])
            if node.asname:
                names.add(node.asname)
    return names


affected = []
for file in sorted((root / "tests").rglob("test_*.py")):
    tree = ast.parse(file.read_text(encoding="utf-8"))
    imports = imports_of(tree)
    reached = any(
        module == target or module.startswith(target + ".")
        for module in modules.values()
        for target in imports
    )
    if reached or defines & names_of(tree):
        affected.append(file.relative_to(root).as_posix())

for path in affected:
    print(path)
'@

$code | & $python - $Base
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
