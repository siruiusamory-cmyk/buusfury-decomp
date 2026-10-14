"""One evidence-backed authored Buu script effect, whose text bound is the profile's declared text_strings.count and is never restated here."""

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
