	CODE16
|sub_0802851E|
|unk_0802851E|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		STR r0, [sp, #8]
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1c
		DCW     0xD053
		MOV r0, #0
		STR r0, [r5, #4]
		LDR r0, [sp, #8]
		LDRH r0, [r0, #2]
		LSL r1, r0, #0x1a
		LSR r1, r1, #0x1f
		BEQ      |loc_08028566|
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
		LDR r0, [r5, #4]
		ADD r0, #1
		STR r0, [r5, #4]
		B        |loc_0802858C|
|loc_08028566|
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BEQ      |loc_0802858C|
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
		LDR r0, [r5, #4]
		ADD r0, #2
		STR r0, [r5, #4]
|loc_0802858C|
		LDR r0, [sp, #8]
		LDRH r0, [r0, #2]
		LSL r1, r0, #0x19
		LSR r1, r1, #0x1f
		DCW     0xD010
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
		LDR r0, [r5, #4]
		ADD r0, #3
		STR r0, [r5, #4]
		B        |loc_0802869C|
|loc_080285B6|
|unk_080285B6|
; cited by 0x08028392 (a pc-relative load targets 0x080286B8)
		B        |loc_08028600|
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1f
		BEQ      |loc_0802869C|
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
		LDR r0, [r5, #4]
		ADD r0, #6
		STR r0, [r5, #4]
		B        |loc_0802869C|
		MOV r0, #4
		DCD     0xFFEAF014
		CMP r0, #0
		BEQ      |loc_080285EC|
		LDR r1, [pc, #0xe4]
		STR r1, [r0]
|loc_080285EC|
		ADD r5, r0, #0
		MOV r1, #0
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800ED18|
		B        |loc_0802869C|
