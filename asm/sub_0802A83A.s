	CODE16
|sub_0802A83A|
|unk_0802A83A|
		LDR r0, [pc, #0x1bc]
		ADD r1, r5, #0
		STR r0, [r4]
		LDR r0, [pc, #0x1b8]
		STRH r5, [r4, #0xe]
		LDR r0, [r0]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0802A862|
		LDR r0, [pc, #0x1ac]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |sub_08011732|
		LDR r0, [pc, #0x1a0]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |loc_0801124C|
|loc_0802A862|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x198]
		MOV r3, #0
		STR r0, [r4]
		LDR r1, [sp, #8]
		LDR r2, [r1]
		LDR r1, [r1, #4]
		STR r1, [r4, #0x14]
		STR r2, [r4, #0x10]
		LDR r0, [sp, #0xc]
		STR r0, [r4, #0x34]
		LDR r1, [sp, #0x10]
		STR r1, [r4, #0x3c]
		STR r7, [r4, #0x40]
		MOV r1, #0
		STR r1, [r4, #0x38]
		STR r1, [r4, #0x30]
		STRB r6, [r4, #8]
		LDR r2, [r4, #0x14]
		STR r2, [r4, #4]
		LDRSB r5, [r0, r3]
		LDR r1, [r4, #0x10]
		MOV r3, #1
		SUB r1, r1, r5
		STR r1, [r4, #0x20]
		LDRSB r5, [r0, r3]
		SUB r3, r2, r5
		STR r3, [r4, #0x24]
		LDRB r2, [r0, #2]
		LDRB r0, [r0, #3]
		ADD r1, r1, r2
		ADD r0, r3, r0
		STR r0, [r4, #0x2c]
		STR r1, [r4, #0x28]
		ADD r0, r4, #0
		DCW     0xE7C5
