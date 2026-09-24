"""One evidence-backed authored Buu script effect; not a native-handler census.

The text-table bound this effect's `text` argument is checked against is the
profile's own declared `text_strings.count`, read by the consumers that hold a
loaded text domain (`scene.visible_text_options`, the specialized placement
editor). It is deliberately NOT restated here: a second copy of a per-game count
inside a contract is exactly the duplicate-authority defect CQA-15 closed.
"""


SCRIPT_EFFECTS = {
    'buus_fury_usa_rev0_01c1707f': {
        'show_centered_sprite_text': {
            'native_opcode': 'native_stack',
            'native_slot': 178,
            'native_handler_raw': 0x08003031,
            'arguments': ('text', 'x', 'y'),
            'coordinate_ranges': {'x': (0, 239), 'y': (0, 159)},
            'evidence': (
                'docs/research/BUU_DIALOG_RUNTIME.md:115-230; handler 0x08003030 '
                'pops three values, passes the deepest as an index into text table '
                '0x0806BCE8, passes the other two as coordinates, and builds centred '
                'OAM sprite text'
            ),
        },
    },
}
