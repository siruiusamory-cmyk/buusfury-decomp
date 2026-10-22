	CODE16
|sub_08026F04|
|unk_08026F04|
		MOV r0, #0
		STR r0, [sp]
		STR r0, [sp, #4]
		MOV r2, #1
		ADD r0, r4, #0
		MOV r1, sp
		BL       |inc_0x1c3f2_0x2ab4c| + 0xa9f2
		LDR r0, [pc, #0x70]
		STR r0, [r4]
		STR r6, [r4, #0x2c]
		LDR r0, [r5]
		LDR r1, [r5, #4]
		SUB r0, #4
		STR r0, [r4, #0x24]
		SUB r1, #4
		STR r1, [r4, #0x28]
		ADD r0, r4, #0
		DCW     0xE7EA
