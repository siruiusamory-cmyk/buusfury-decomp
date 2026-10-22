	CODE16
|sub_08038AF8|
|unk_08038AF8|
		MOV r1, #1
		LSL r1, r1, #0xc
		CMP r7, #0
		BEQ      |loc_08038B02|
		LSR r1, r1, #2
|loc_08038B02|
		ADD r2, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x2bc]
		STR r0, [r4]
		LDR r1, [r6]
		LDR r2, [r6, #4]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		LDR r0, [sp, #0x28]
		MOV r1, #0x40
		STR r0, [r4, #0x4c]
		MOV r0, #0
		STR r0, [r4, #0x44]
		STRB r0, [r1, r4]
		STR r0, [r4, #0x50]
		STR r0, [r4, #0x54]
		LDRB r0, [r5, #0x10]
		LDR r1, [pc, #0x298]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #4
		ADD r0, r0, r1
		STR r0, [r4, #0x5c]
		CMP r7, #0
		BNE      |loc_08038B5A|
		ADD r0, #0xc
		STR r0, [r4, #0x5c]
		MOV r0, #0
		STR r0, [r4, #0x48]
		LDR r1, [r5]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r5, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		STR r0, [r4, #0x58]
		B        |loc_08038BA4|
|loc_08038B5A|
		LDRB r0, [r5, #0x10]
		LDR r1, [pc, #0x270]
		SUB r3, r7, #1
		LSL r0, r0, #3
		ADD r0, r0, r1
		MOV r1, #6
		LDR r2, [r0]
		SUB r1, r1, r7
		LDR r0, [r0, #4]
		MUL r2, r1
		MUL r0, r1
		STR r0, [sp, #8]
		LDR r1, [sp, #8]
		ADD r0, r2, #0
		STR r2, [sp, #4]
		LDR r2, [r6]
		ADD r0, r2, r0
		LDR r2, [r6, #4]
		STR r0, [sp, #4]
		ADD r1, r2, r1
		STR r1, [sp, #8]
		STR r1, [sp, #0x10]
		ADD r1, r5, #0
		STR r0, [sp, #0xc]
		MOV r0, #0
		ADD r2, sp, #0xc
		STR r4, [sp]
		BL       |inc_0x351c0_0x3d4d0| + 0x3918
		ADD r1, r0, #0
		STR r0, [r4, #0x48]
		LDR r0, [pc, #0x238]
		LDR r0, [r0]
		BL       |List_Append|
		MOV r0, #0
		STR r0, [r4, #0x58]
|loc_08038BA4|
		LDR r0, [r4, #0x5c]
		STR r0, [r4, #0x18]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x3934
