	CODE16
|sub_08015D30|
|unk_08015D30|
		MOV r2, #0
		MVN r2, r2
		ADD r1, r2, #0
		STR r1, [sp, #4]
		STR r2, [sp, #8]
		STR r7, [sp]
		ADD r3, sp, #0x18
		LDMIA r3!, {r1, r2, r3}
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x5e66
		LDR r0, [pc, #0x148]
		STR r0, [r4]
		ADD r0, r4, #0
		ADD r0, #0x24
		LDMIA r6!, {r1, r2, r3, r6}
		STMIA r0!, {r1, r2, r3, r6}
		MOV r0, #0
		STR r0, [r4, #0x4c]
		STR r5, [r4, #0x44]
		STR r0, [r4, #0x1c]
		STR r0, [r4, #0x20]
		STR r0, [r4, #0x34]
		STR r0, [r4, #0x38]
		STR r0, [r4, #0x3c]
		MOV r1, #0xff
		ADD r1, #0x11
		STR r0, [r4, #0x40]
		STR r0, [r1, r4]
		MOV r1, #1
		MOV r2, #0
		STR r2, [sp, #0xc]
		STR r1, [sp, #8]
		STR r5, [sp, #4]
		LDR r2, [r4, #0x28]
		STR r2, [sp]
		LDR r1, [r4, #4]
		LDR r3, [r4, #0x24]
		MOV r2, #4
		BL       |loc_08013E64|
		STR r0, [r4, #0x1c]
		LDR r0, [r4, #0x44]
		MOV r2, #0
		MOV r1, #1
		STR r1, [sp, #8]
		STR r2, [sp, #0xc]
		STR r0, [sp, #4]
		LDR r2, [r4, #0x28]
		STR r2, [sp]
		LDR r3, [r4, #0x2c]
		MOV r2, #5
		SUB r3, #0x10
		MOV r0, #0
		LDR r1, [r4, #4]
		BL       |loc_08013E64|
		STR r0, [r4, #0x20]
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0x93a
