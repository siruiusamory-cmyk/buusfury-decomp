"""Command surfaces that need more than a thin argparse block in :mod:`cli`.

Each module here registers its own parser and owns its own run path, so the
central CLI stays a wiring file and a large feature cannot bloat it. The enemy
randomizer pack lives here because it composes several SDK layers (maps,
transitions, placement events, stat tables, the writer) and that composition is
worth reading on its own.
"""
