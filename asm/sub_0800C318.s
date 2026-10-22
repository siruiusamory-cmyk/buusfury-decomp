	CODE16
|sub_0800C318|
|unk_0800C318|
		LDR r0, [pc, #0x124]
		MOV r6, #1
		LSL r6, r6, #9
		LDR r5, [pc, #0x110]
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		LDR r0, [r5]
		ADD r1, r6, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0800C340|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |loc_0801124C|
|loc_0800C340|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x100]
		MOV r1, #8
		STR r0, [r4]
		STR r7, [r4, #0x14]
		LDRB r2, [r7, #4]
		LDR r0, [r5]
		BL       |loc_08011C70|
		STR r0, [r4, #0x10]
		LDR r1, [r0, #4]
		ADD r1, #1
		STR r1, [r4, #4]
		LDRB r0, [r0, #8]
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_0800C298|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xc1be
