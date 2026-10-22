	CODE16
|sub_08025E6E|
|unk_08025E6E|
		ADD r0, r4, #0
		BL       |loc_08024A7C|
		LDR r0, [pc, #0x30c]
		ASR r2, r5, #3
		STR r0, [r4]
		STR r6, [r4, #0x18]
		LDR r0, [pc, #0x308]
		LSL r6, r5, #0x1d
		LDR r1, [r0, #8]
		LSR r6, r6, #0x1d
		ADD r1, r2, r1
		ADD r1, #0xc0
		MOV r3, #1
		LDRB r2, [r1, #5]
		LSL r3, r6
		ORR r2, r3
		STRB r2, [r1, #5]
		LSL r1, r5, #4
		LDR r2, [pc, #0x2f4]
		MOV r5, #0
		ADD r1, r1, r2
		STR r1, [r4, #0x20]
		MOV r1, #0
		STR r1, [r4, #0x10]
		STR r1, [r4, #0x1c]
		STRB r1, [r4, #0xc]
		STRB r1, [r4, #0xd]
		STR r1, [sp]
		STR r1, [sp, #4]
		MOV r1, #0x68
		STR r1, [sp, #8]
		MOV r1, #0x38
		STR r1, [sp, #0xc]
		LDR r1, [r0, #0xc]
		ADD r6, sp, #0x10
		ADD r0, r6, #0
		MOV r2, sp
		BL       |inc_0x03d784_0x041118| + 0x2f4
		LDR r0, [r4, #0x20]
		LDR r1, [pc, #0x2cc]
		LDRH r0, [r0, #2]
		MOV r7, sp
		LSL r0, r0, #2
		LDR r0, [r1, r0]
		STR r0, [sp, #4]
|loc_08025ECC|
		ADD r3, r7, #0
		MOV r2, #0x68
		ADD r0, r6, #0
		LDR r1, [sp, #4]
		BL       |inc_0x03d784_0x041118| + 0x6e6
		LDR r0, [sp, #0xc]
		ADD r5, #1
		CMP r0, #0
		BEQ      |loc_08025ECC|
		LSL r0, r5, #4
		SUB r0, #0x38
		STR r0, [r4, #0x14]
		BPL      |loc_08025EEC|
		MOV r1, #0
		STR r1, [r4, #0x14]
|loc_08025EEC|
		ADD r0, r4, #0
		DCW     0xE7BC
