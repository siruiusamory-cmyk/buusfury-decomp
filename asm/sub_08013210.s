	CODE16
|sub_08013210|
|unk_08013210|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1c
		BEQ      |loc_080132E2|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		MOV r5, #0
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		STR r0, [sp, #8]
		LDRH r0, [r0, #2]
		MOV r2, #0x47
		LSL r2, r2, #3
		ADD r6, r7, r2
		ADD r7, #0xff
		LSL r1, r0, #0x1a
		LSR r1, r1, #0x1f
		ADD r7, #0xa1
		CMP r1, #0
		BEQ      |loc_0801326A|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #4]
		ADD r0, r1, #0
		STR r1, [sp]
		LDR r1, [r6]
		MOV r2, #2
		SUB r0, r0, r1
		STR r0, [sp]
		ADD r0, r4, #0
		MOV r1, sp
		BL       |inc_0x0158_0x143f2| + 0x12808
		MOV r5, #1
		B        |loc_0801328C|
|loc_0801326A|
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BEQ      |loc_0801328C|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #4]
		ADD r0, r1, #0
		STR r1, [sp]
		LDR r1, [r6]
		MOV r2, #2
		ADD r0, r0, r1
		STR r0, [sp]
		ADD r0, r4, #0
		MOV r1, sp
		BL       |inc_0x0158_0x143f2| + 0x12808
		MOV r5, #2
|loc_0801328C|
		LDR r0, [sp, #8]
		LDRH r0, [r0, #2]
		LSL r1, r0, #0x19
		LSR r1, r1, #0x1f
		BEQ      |loc_080132B2|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #4]
		STR r1, [sp]
		LDR r2, [r6]
		MOV r1, sp
		SUB r0, r0, r2
		STR r0, [sp, #4]
		MOV r2, #1
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x12808
		ADD r5, #3
		B        |loc_080132D2|
|loc_080132B2|
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1f
		BEQ      |loc_080132D2|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #4]
		STR r1, [sp]
		LDR r2, [r6]
		MOV r1, sp
		ADD r0, r0, r2
		STR r0, [sp, #4]
		MOV r2, #1
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x12808
		ADD r5, #6
|loc_080132D2|
		LDR r1, [pc, #0x58]
		LSL r0, r5, #2
		ADD r1, #0x94
		ADD r0, r0, r1
		LDRB r1, [r4, #0x10]
		LDRB r0, [r0, r1]
		STRB r0, [r4, #0x10]
		B        |loc_080132F0|
|loc_080132E2|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
|loc_080132F0|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1f
		BEQ      |loc_0801330C|
		ADD r0, r4, #0
		BL       |sub_08012A24|
|loc_0801330A|
		B        |inc_0x0158_0x143f2| + 0x130b4
|loc_0801330C|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1f
		BEQ      |loc_0801330A|
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x12a06
		B        |inc_0x0158_0x143f2| + 0x130b4
