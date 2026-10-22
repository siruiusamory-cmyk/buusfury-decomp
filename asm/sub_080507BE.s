	CODE16
|sub_080507BE|
|unk_080507BE|
		LDR r0, [pc, #0x58]
		LDR r7, [pc, #0x58]
		STR r0, [r4]
		STRH r5, [r4, #0xe]
		LDR r0, [r7, #4]
		ADD r1, r5, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_080507E2|
		ADD r1, r5, #0
		LDR r0, [r7, #4]
		BL       |sub_08011732|
		ADD r1, r5, #0
		LDR r0, [r7, #4]
		BL       |loc_0801124C|
|loc_080507E2|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LDR r1, [pc, #0x38]
		STRH r0, [r4, #0xc]
		STR r1, [r4]
		LDR r1, [sp, #8]
		LSL r0, r0, #5
		STR r1, [r4, #0x28]
		STRB r6, [r4, #8]
		LDRB r3, [r1, #2]
		LDRB r5, [r1, #3]
		LDR r1, [r1, #8]
		MUL r3, r5
		ADD r2, r3, #0
		LDR r3, [pc, #0x24]
		ADD r0, r0, r3
		BL       |Thunk_VramCopy|
		LDR r0, [pc, #0x20]
		STR r0, [r4]
		LDR r1, [sp, #0xc]
		ADD r0, r4, #0
		LDR r2, [r1]
		LDR r1, [r1, #4]
		STR r1, [r4, #0x30]
		STR r2, [r4, #0x2c]
		B        |inc_0x049120_0x055620| + 0x769a
