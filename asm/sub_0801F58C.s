	CODE16
|sub_0801F58C|
|unk_0801F58C|
		LDRB r1, [r0, #5]
		LDR r0, [pc, #0x228]
		LDR r0, [r0, #0xc]
		BL       |loc_08004468|
		B        |loc_0801F5B2|
|loc_0801F598|
|unk_0801F598|
		LDR r1, [pc, #0x21c]
		LDRB r2, [r0, #5]
		LDR r1, [r1, #0xc]
		LDR r0, [r0]
		ADD r1, r1, r2
		LDRB r2, [r1, #2]
		SUB r0, r2, r0
		STRB r0, [r1, #2]
		B        |loc_0801F5B2|
