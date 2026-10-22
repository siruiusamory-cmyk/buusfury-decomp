	CODE16
|sub_0800BF4C|
|unk_0800BF4C|
		MOV r6, #0xf
		LSL r6, r6, #8
		LDR r0, [pc, #0x164]
		LDR r5, [pc, #0x154]
		ADD r1, r6, #0
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		SUB r5, #0xc
		LDR r0, [r5]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0800BF76|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |loc_0801124C|
|loc_0800BF76|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x140]
		STR r0, [r4]
		STR r7, [r4, #0x14]
		MOV r0, #0x10
		STRB r0, [r4, #8]
		MOV r0, #0
		STR r0, [r4, #4]
		MOV r0, #0xf0
		STRB r0, [r4, #0x10]
		ADD r0, r4, #0
		BL       |loc_0800BE90|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xbdf2
