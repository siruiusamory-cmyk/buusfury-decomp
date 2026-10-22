	CODE16
|sub_08012DD0|
|unk_08012DD0|
		LDR r1, [r5]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r5, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1f
		BEQ      |inc_0x0158_0x143f2| + 0x12c76
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x12a06
		B        |inc_0x0158_0x143f2| + 0x12c76
		PUSH {r4, r5, r6, r7, lr}
		ADD r5, r1, #0
		ADD r4, r1, #0
		ADD r0, r1, #0
		LDR r1, [r1]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		SUB sp, #0x14
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		LDRH r1, [r0, #2]
		MOV r0, #0x11
		LSL r0, r0, #5
		ADD r0, r4, r0
		LDRH r0, [r0, #0x10]
		AND r1, r0
		CMP r1, r0
		BNE      |loc_08012EF8|
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0x198]
		ADD r6, r4, #0
		ADD r6, #0xff
		LSL r0, r0, #3
		ADD r0, r0, r1
		ADD r6, #0xa1
		LDR r1, [r6, #4]
		LDR r2, [r6]
		STR r1, [sp, #8]
		MOV r1, #0x8f
		LSL r1, r1, #2
		STR r2, [sp, #4]
		ADD r2, r4, r1
		LDR r1, [r0]
		LDR r3, [r2]
		LDR r7, [pc, #0x17c]
		MUL r3, r1
		LDR r1, [sp, #4]
		ADD r1, r1, r3
		STR r1, [sp, #4]
		LDR r0, [r0, #4]
		LDR r2, [r2]
		ADD r1, sp, #4
		MUL r2, r0
		LDR r0, [sp, #8]
		ADD r0, r0, r2
		SUB r2, r6, #4
		STR r2, [sp, #0x10]
		STR r0, [sp, #8]
		LDR r0, [r7, #8]
		BL       |loc_080097EA|
		CMP r0, #0
		BEQ      |loc_08012F1C|
		LDR r0, [sp, #4]
		MOV r2, #0x84
		STR r0, [r6]
		LDR r1, [sp, #8]
		ADD r0, r6, #4
		STR r0, [sp, #0xc]
		STR r1, [r6, #4]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r2, r1]
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		LDRH r0, [r0, #2]
		MOV r1, #0x47
		LSL r1, r1, #3
		LSL r0, r0, #0x19
		LSR r0, r0, #0x1f
		ADD r5, r5, r1
		CMP r0, #0
		BEQ      |loc_08012E92|
		LDRB r0, [r4, #0x10]
		CMP r0, #1
		BEQ      |loc_08012E92|
		LDR r0, [sp, #8]
		LDR r1, [r5]
		SUB r0, r0, r1
		STR r0, [sp, #8]
|loc_08012E92|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1f
		BEQ      |loc_08012EB6|
		LDRB r0, [r4, #0x10]
		CMP r0, #0
		BEQ      |loc_08012EB6|
		LDR r0, [sp, #8]
		LDR r1, [r5]
		ADD r0, r0, r1
		STR r0, [sp, #8]
|loc_08012EB6|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x1a
		LSR r0, r0, #0x1f
		BEQ      |loc_08012EDA|
		LDRB r0, [r4, #0x10]
		CMP r0, #2
		BEQ      |loc_08012EDA|
		LDR r0, [sp, #4]
		LDR r1, [r5]
		SUB r0, r0, r1
		STR r0, [sp, #4]
|loc_08012EDA|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BEQ      |loc_08012F02|
		LDRB r0, [r4, #0x10]
		CMP r0, #3
		BEQ      |loc_08012F02|
		B        |loc_08012EFA|
|loc_08012EF8|
		B        |sub_08012F60|
|loc_08012EFA|
		LDR r0, [sp, #4]
		LDR r1, [r5]
		ADD r0, r0, r1
		STR r0, [sp, #4]
|loc_08012F02|
		LDR r2, [sp, #0x10]
		LDR r0, [r7, #8]
		ADD r1, sp, #4
		BL       |loc_080097EA|
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0x12e16
		LDR r0, [sp, #4]
		STR r0, [r6]
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #8]
		STR r1, [r0]
		B        |inc_0x0158_0x143f2| + 0x12e16
|loc_08012F1C|
		MOV r1, #0x64
		MOV r0, #8
		BL       |loc_0800797C|
		MOV r0, #8
		DCW     0xF02A
		DCW     0xFB47
		CMP r0, #0
		BEQ      |loc_08012F36|
		MOV r1, #3
		STRB r1, [r0, #4]
		LDR r1, [pc, #0x84]
		STR r1, [r0]
|loc_08012F36|
		ADD r5, r0, #0
		MOV r1, #9
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800ED18|
		MOV r1, #0xb1
		LDR r2, [pc, #0x70]
		LSL r1, r1, #2
		ADD r1, r1, r2
		LDR r5, [pc, #0x6c]
		LDR r0, [r7]
		MOV r2, #0x40
		MOV r3, #0
		ADD r0, r0, r5
		BL       |inc_0x03d784_0x041118| + 0xbf4
		B        |inc_0x0158_0x143f2| + 0x12e16
