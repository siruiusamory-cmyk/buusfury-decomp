	CODE16
|sub_0801D44C|
|unk_0801D44C|
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r4, #0xff
		ADD r4, #1
		LDR r0, [r4, #0xc]
		LDR r1, [r4, #0x24]
		CMP r1, #0
		BNE      |loc_0801D460|
		ADD r0, #1
|loc_0801D460|
		LDR r1, [r4, #0x28]
		CMP r1, #0
		BNE      |loc_0801D46C|
		CMP r0, #1
		BLT      |loc_0801D46C|
		ADD r0, #1
|loc_0801D46C|
		CMP r0, #0
		BEQ      |loc_0801D4C4|
		CMP r0, #1
		BEQ      |loc_0801D4E4|
		CMP r0, #2
		BNE      |loc_0801D50A|
		MOV r1, #0x2f
		LDR r0, [r7, #0x14]
		LSL r1, r1, #6
		ADD r5, r0, r1
		MOV r2, #0
		MOV r1, #9
		LDR r0, [r5, #0x38]
		BL       |List_CallMethod1|
		ADD r6, r0, #0
		LDR r0, [r7, #0x10]
		ADD r0, #0x80
		LDR r0, [r0, #0x10]
		CMP r0, #0
		BNE      |loc_0801D4BC|
		CMP r6, #0
		BEQ      |loc_0801D4BC|
		ADD r2, r7, #0
		MOV r7, #0x61
		LDR r0, [r5, #0x38]
		LSL r7, r7, #4
		ADD r1, r0, r7
		LDR r3, [pc, #0x144]
		LDR r1, [r1]
		LDR r3, [r3]
		ADD r1, r1, r3
		CMP r1, #8
		BGE      |loc_0801D4BC|
		BL       |loc_080116FC|
		MOV r1, #0xff
		ADD r1, #1
		CMP r0, r1
		DCW     0xDA27
|loc_0801D4BC|
		MOV r0, #4
		BL       |inc_0x03d784_0x041118| + 0xf2
		DCW     0xE054
|loc_0801D4C4|
		LDR r0, [r4, #0x20]
		CMP r0, #0
		BEQ      |loc_0801D4E0|
		LDR r0, [r7, #0xc]
		ADD r4, #0x14
		LDRB r1, [r0]
		LDMIA r4!, {r2, r3}
		BL       |inc_0x0158_0x143f2| + 0x4470
		MOV r0, #1
		BL       |inc_0x03d784_0x041118| + 0xf2
		MOV r0, #1
		DCW     0xE7B3
|loc_0801D4E0|
		MOV r0, #0
		DCW     0xE7B1
|loc_0801D4E4|
		LDR r0, [r4, #0x30]
		MOV r3, #0x2c
		LDR r0, [r0]
		LDR r2, [pc, #0x104]
		LSL r1, r0, #4
		LSR r1, r1, #4
		MUL r1, r3
		ADD r1, r1, r2
		LDRB r2, [r1, #0x14]
		LSR r1, r0, #0x1c
		SUB r1, #1
		LDR r0, [r7, #0xc]
		BL       |loc_08004544|
		MOV r0, #3
		BL       |inc_0x03d784_0x041118| + 0xf2
		MOV r0, #1
		DCW     0xE79E
|loc_0801D50A|
|unk_0801D50A|
		B        |loc_0801D572|
		LDR r5, [r5, #0x38]
		ADD r1, r6, #0
		ADD r0, sp, #0xc
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ASR r1, r1, #1
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x20]
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		LDR r6, [r4, #0x18]
		MOV r0, #0x14
		DCW     0xF020
		DCW     0xF83F
		CMP r0, #0
		BEQ      |loc_0801D550|
		MOV r1, #1
		STR r1, [r0, #4]
		LDR r1, [pc, #0xb0]
		ADD r2, sp, #0x1c
		STR r1, [r0]
		LDMIA r2!, {r1, r2}
		ADD r0, #8
		STMIA r0!, {r1, r2, r6}
		SUB r0, #0x14
|loc_0801D550|
		ADD r1, r5, r7
		LDR r2, [r1]
		ADD r3, r2, #1
		STR r3, [r1]
		LSL r2, r2, #2
		ADD r1, r2, r1
		STR r0, [r1, #4]
		LDR r0, [pc, #0x84]
		LDR r1, [r4, #0x14]
		LDR r0, [r0, #0xc]
		BL       |inc_0x0158_0x143f2| + 0x44fe
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0xf2
		MOV r0, #1
		DCW     0xE76A
