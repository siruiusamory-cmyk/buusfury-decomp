	CODE16
|sub_08011F7A|
|unk_08011F7A|
		LDR r0, [pc, #0x21c]
		STMIA r5!, {r0, r6}
		MOV r0, #0
		LDR r2, [r4, #0x14]
		STR r0, [sp]
		STR r0, [sp, #0x44]
		SUB r5, #8
		ADD r1, r7, #0
		MOV r0, sp
		BL       |loc_08004038|
		LDR r0, [sp]
		CMP r0, #1
		BNE      |loc_08011F9C|
		LDR r0, [sp, #4]
		LDR r1, [r5, #4]
		STRH r0, [r1]
|loc_08011F9C|
		LDR r0, [sp, #0x58]
		LDR r1, [r4, #0x14]
		CMP r0, r1
		BEQ      |loc_08011FC2|
		LDR r0, [sp, #0x58]
		LDR r0, [r0]
		STR r0, [r4, #0x18]
		LDR r0, [sp, #0x58]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x1c]
		LDR r0, [sp, #0x58]
		LDR r0, [r0, #8]
		STR r0, [r4, #0x20]
		LDR r0, [sp, #0x58]
		LDR r0, [r0, #0xc]
		STR r0, [r4, #0x24]
		ADD r0, r4, #0
		ADD r0, #0x18
		STR r0, [r4, #0x14]
|loc_08011FC2|
		ADD r0, r5, #0
		B        |inc_0x0158_0x143f2| + 0x11e1e
