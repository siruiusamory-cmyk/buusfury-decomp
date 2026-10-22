	CODE16
|sub_08033208|
|unk_08033208|
		LDR r0, [pc, #0xf4]
		LDR r1, [r0]
		ADD r0, sp, #8
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #8]
		LDR r1, [sp, #0x10]
		LDR r2, [sp, #0x14]
		ADD r1, r0, r1
		LDR r0, [sp, #0xc]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp]
		STR r1, [sp, #0x18]
		STR r0, [sp, #4]
		STR r0, [sp, #0x1c]
		ADD r0, sp, #0x20
		ADD r1, r4, #0
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0x20]
		LDR r1, [sp, #0x28]
		LDR r2, [sp, #0x2c]
		ADD r1, r0, r1
		LDR r0, [sp, #0x24]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		STR r0, [sp, #4]
		STR r0, [sp, #0x34]
		ASR r1, r1, #1
		LDR r0, [sp, #0x18]
		STR r1, [sp]
		SUB r0, r0, r1
		STR r1, [sp, #0x30]
		LDR r1, [sp, #0x1c]
		LDR r2, [sp, #0x34]
		STR r0, [sp]
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #4]
		STR r1, [sp, #0x3c]
		STR r0, [sp, #0x38]
		BGE      |loc_0803326C|
		NEG r0, r2
|loc_0803326C|
		ADD r1, r0, #0
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BGE      |loc_08033276|
		NEG r0, r0
|loc_08033276|
		STR r1, [sp, #0x30]
		STR r0, [sp, #0x34]
		LDRB r3, [r4, #0x10]
		ADD r0, r1, #0
		LDR r1, [sp, #0x34]
		CMP r3, #0
		BEQ      |inc_0x331c0_0x341c0| + 0x10a
		MOV r2, #0xf
		MVN r2, r2
		CMP r3, #1
		BEQ      |inc_0x331c0_0x341c0| + 0xf8
		CMP r3, #2
		BEQ      |loc_080332A6|
		CMP r3, #3
		BNE      |inc_0x331c0_0x341c0| + 0x11c
		CMP r1, #0x10
		BGE      |loc_080332A2|
		LDR r0, [sp, #0x38]
		CMP r0, #0x10
		BLE      |loc_080332A2|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x44
|loc_080332A2|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x44
|loc_080332A6|
		CMP r1, #0x10
		BGE      |loc_080332B4|
		LDR r0, [sp, #0x38]
|loc_080332AC|
|unk_080332AC|
		CMP r0, r2
		BGE      |loc_080332B4|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x44
|loc_080332B4|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x44
		CMP r0, #0x10
		BGE      |loc_080332C6|
		LDR r0, [sp, #0x3c]
		CMP r0, r2
		BGE      |loc_080332C6|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x44
|loc_080332C6|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x44
		CMP r0, #0x10
		BGE      |loc_080332D8|
		LDR r0, [sp, #0x3c]
		CMP r0, #0x10
		BLE      |loc_080332D8|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x44
|loc_080332D8|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x44
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x44
