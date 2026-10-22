	CODE16
|loc_080429C4|
|unk_080429C4|
		B        |inc_0x042118_0x049114| + 0x8de
|loc_080429C6|
|unk_080429C6|
		B        |inc_0x042118_0x049114| + 0x8e2
|loc_080429C8|
|unk_080429C8|
		B        |loc_08042A3C|
		CMP r0, #0
		BNE      |loc_080429D2|
		MOV r7, #0xff
		STRB r7, [r5, #6]
