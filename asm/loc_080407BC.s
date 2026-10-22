	CODE16
|loc_080407BC|
|unk_080407BC|
		CMP r0, #0x40
		DCW     0xD107
		LDR r1, [pc, #4]
		LDR r0, [pc, #8]
		STR r0, [r1]
		B        |loc_080407D8|
