	CODE16
|loc_08042A3C|
		CMP r6, #0xff
		BNE      |loc_08042A1C|
		MOV r1, #0
		MOV r0, #0xf2
		BL       |loc_0804333c|
		BL       |sub_08043368|
		B        |inc_0x042118_0x049114| + 0x7e8
