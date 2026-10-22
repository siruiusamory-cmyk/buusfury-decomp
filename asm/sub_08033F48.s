	CODE16
|sub_08033F48|
|unk_08033F48|
		ADD r2, r7, #0
		MOV r1, #0x40
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x194]
		LDR r3, [pc, #0x194]
		STR r0, [r4]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		MOV r0, #0x16
		STR r0, [r4, #0x48]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		LDR r0, [r6]
		LDR r1, [r5]
		SUB r0, r0, r1
		LDR r1, [r6, #4]
		LDR r2, [r5, #4]
		STR r0, [sp, #4]
		SUB r1, r1, r2
		STR r1, [sp, #8]
		ADD r1, r0, #0
		LDR r0, [sp, #8]
		MUL r1, r3
		ASR r1, r1, #8
		STR r1, [r4, #0x40]
		LDR r1, [pc, #0x16c]
		MUL r0, r3
		ADD r0, r0, r1
		MOV r1, #1
		LSL r1, r1, #9
		ASR r0, r0, #8
		SUB r0, r0, r1
		STR r0, [r4, #0x44]
		LDR r0, [pc, #0x160]
		STR r0, [r4, #0x18]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		B        |inc_0x331c0_0x341c0| + 0xd84
		PUSH {r4, r5, r6, r7, lr}
		LDR r2, [r0, #0x44]
		SUB sp, #0x44
		ADD r2, #0x20
		STR r2, [r0, #0x44]
		ADD r4, r0, #0
		ADD r0, #0x40
		ADD r5, r1, #0
		LDR r1, [r4, #0x20]
		LDR r3, [r0]
		ADD r2, #0x20
		ADD r6, r1, r3
		STR r6, [r4, #0x20]
		ADD r1, r0, #4
		LDR r7, [r1]
		LDR r0, [r4, #0x24]
		ADD r0, r0, r7
		STR r0, [r4, #0x24]
		STR r2, [r4, #0x44]
		ADD r2, r6, r3
		STR r2, [r4, #0x20]
		LDR r1, [r1]
		ADD r0, r0, r1
		STR r0, [r4, #0x24]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [r4, #0x48]
		SUB r0, #1
		STR r0, [r4, #0x48]
		BNE      |loc_080340C6|
		ADD r6, r4, #0
		ADD r6, #0x20
		ADD r0, r5, #0
		ADD r5, r6, #4
		CMP r0, #0
		BEQ      |loc_08034088|
		LDR r0, [r6]
		LDR r1, [r5]
		ASR r0, r0, #8
		ASR r1, r1, #8
		STR r1, [sp, #0x38]
		STR r1, [sp, #0x40]
		LDR r1, [pc, #0xf8]
		STR r0, [sp, #0x34]
		SUB r1, #0xc
		ADD r1, r1, #4
		STR r0, [sp, #0x3c]
		LDMIA r1!, {r0, r1}
		LDR r2, [r4, #0x1c]
		ADD r3, sp, #0
		STR r2, [sp, #0x28]
		LDRB r2, [r4, #0x10]
		MOV r7, #0
		STRB r2, [r3, #0x1c]
		LDR r2, [pc, #0xe4]
		STR r7, [sp, #0x20]
		STR r2, [sp, #0x24]
		LDR r2, [sp, #0x3c]
		SUB r3, r2, r0
		LDR r2, [sp, #0x40]
		STR r3, [sp]
		SUB r2, r2, r1
		STR r2, [sp, #4]
		STR r2, [sp, #0x10]
		LDR r2, [sp, #0x3c]
		STR r3, [sp, #0xc]
		ADD r0, r2, r0
		LDR r2, [sp, #0x40]
		STR r0, [sp]
		ADD r1, r2, r1
		STR r1, [sp, #4]
		STR r1, [sp, #0x18]
		STR r0, [sp, #0x14]
		LDR r0, [pc, #0xb8]
		ADD r3, sp, #0
		STRB r7, [r3, #8]
		MOV r1, #1
		SUB r0, #0xc
		STR r4, [sp, #0x38]
		LDR r0, [r0]
		ADD r2, sp, #8
		BL       |List_CallMethod1|
		CMP r0, #0
		BEQ      |loc_08034088|
		LDR r0, [pc, #0xa0]
		LDR r7, [pc, #0xa8]
		SUB r0, #0xc
		LDR r0, [r0]
		STR r0, [sp, #4]
		MOV r0, #0x10
		DCD     0xFAACF009
		CMP r0, #0
		BEQ      |loc_08034072|
		MOV r1, #1
		STR r1, [r0, #4]
		LDR r1, [pc, #0x94]
		STR r1, [r0]
		STR r7, [r0, #8]
		MOV r7, #0
		STR r7, [r0, #0xc]
|loc_08034072|
		ADD r2, r0, #0
		LDR r0, [sp, #4]
		MOV r1, #0x61
		LSL r1, r1, #4
		ADD r0, r0, r1
		LDR r1, [r0]
		ADD r3, r1, #1
		STR r3, [r0]
		LSL r1, r1, #2
		ADD r0, r1, r0
		STR r2, [r0, #4]
|loc_08034088|
		LDR r7, [pc, #0x68]
		SUB r7, #0xc
		LDR r0, [r7]
		BL       |loc_080116FC|
		MOV r1, #1
		LSL r1, r1, #0xa
		CMP r0, r1
		BLT      |inc_0x331c0_0x341c0| + 0xf1c
		LSL r0, r1, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		MOV r1, #1
		LSL r1, r1, #0xc
		ADD r0, r0, r1
		LDR r1, [r6]
