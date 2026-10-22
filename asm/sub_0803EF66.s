	CODE16
|sub_0803EF66|
|unk_0803EF66|
		CMP r1, #1
		BNE      |loc_0803EF74|
		ADD r1, r3, #0
		ADD r1, #0x50
		LDRB r2, [r1, #9]
		STRB r2, [r1, #8]
		B        |sub_0803EF82|
|loc_0803EF74|
		LDR r2, [r0, #0xc]
		LDR r2, [r2, #0xc]
		ADD r1, r2, r1
		SUB r1, #0x10
		LDRB r1, [r1, #0xe]
		MOV r2, #0x58
		STRB r1, [r2, r3]
