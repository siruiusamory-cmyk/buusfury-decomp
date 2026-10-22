	CODE16
|sub_0803B728|
|unk_0803B728|
		LDR r2, [sp, #0x30]
		NEG r2, r2
|loc_0803B72C|
|unk_0803B72C|
		STR r1, [sp, #0x24]
		STR r2, [sp, #0x28]
		STR r1, [sp, #0x34]
		STR r2, [sp, #0x38]
		STR r1, [sp, #0x3c]
		STR r2, [sp, #0x40]
		LDR r1, [r7, #8]
		LDR r2, [r0]
		LDR r0, [r0, #4]
		STR r2, [sp, #0x34]
		ADD r2, sp, #0x3c
		STR r0, [sp, #0x38]
		LDMIA r2!, {r0, r2}
		CMP r0, r2
		BLT      |sub_0803B772|
		LDR r3, [sp, #0x40]
		LDR r0, [sp, #0x3c]
		ASR r3, r3, #8
		LSL r5, r3, #1
		ADD r6, r5, #0
		ASR r2, r0, #8
		ADD r0, r2, #1
		SUB r5, r5, r2
		SUB r2, r3, r2
		LSL r2, r2, #1
		STR r2, [sp, #0x2c]
		MOV r2, #0xff
		ADD r2, #1
		MOV r3, #0
		STR r3, [sp, #0x28]
		STR r2, [sp, #0x24]
		STR r2, [sp, #0x1c]
		STR r2, [sp, #0x20]
		STR r6, [sp, #0x30]
		B        |inc_0x351c0_0x3d4d0| + 0x65d8
