	CODE16
|sub_08010098|
|unk_08010098|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x44]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRB r1, [r4, #0x11]
		LDR r0, [r4, #0x50]
		ADD r2, r4, #0
		LSL r1, r1, #4
		ADD r0, r0, r1
		LDRB r1, [r4, #0x10]
		ADD r2, #0xff
		ADD r2, #0x95
		LSL r1, r1, #2
		ADD r0, r0, r1
		LDR r0, [r0, #4]
		ADD r7, r2, #0
		STR r0, [r4, #0x54]
		LDR r0, [r5, #0x20]
		ADD r1, sp, #0x18
		LSL r0, r0, #2
		STR r0, [sp, #0x18]
		LDR r0, [r5, #0x24]
		ADD r3, sp, #0x10
		LSL r0, r0, #2
		STR r0, [sp, #0x1c]
		MOV r0, #0xff
		ADD r0, #0xa9
		LDR r0, [r0, r4]
		STR r0, [sp, #0x20]
		LDR r0, [pc, #0x1f8]
		LDR r0, [r0]
		STR r2, [sp]
		ADD r2, r4, #0
		ADD r2, #0x60
		BL       |sub_0802f1c6|
		LDR r0, [r4, #0x60]
		CMP r0, #0
		BEQ      |loc_08010124|
		MOV r0, #0x3f
		LDR r1, [sp, #0x10]
		MVN r0, r0
		CMP r1, r0
		BLT      |loc_0801010A|
		MOV r2, #0xff
		LDR r1, [sp, #0x10]
		ADD r2, #0x31
		CMP r1, r2
		BGT      |loc_0801010A|
		LDR r1, [sp, #0x14]
		CMP r1, r0
		BLT      |loc_0801010A|
		LDR r0, [sp, #0x14]
		CMP r0, #0xe0
		BLE      |loc_0801010E|
|loc_0801010A|
		STR r6, [r4, #0x60]
		B        |loc_08010124|
|loc_0801010E|
		LDR r1, [sp, #0x10]
		LDR r0, [r4, #0x58]
		LDRB r2, [r0, #8]
		LSR r2, r2, #1
		SUB r1, r1, r2
		STR r1, [r4, #0x6c]
		LDRB r0, [r0, #9]
		LDR r1, [sp, #0x14]
		LSR r0, r0, #1
		SUB r0, r1, r0
		STR r0, [r4, #0x70]
|loc_08010124|
		LDR r1, [pc, #0x1ac]
		LDR r0, [r5, #0x14]
		MUL r1, r0
		ASR r1, r1, #0x11
		STR r1, [r4, #0x68]
		CMP r1, #0x80
		BGE      |loc_08010136|
		MOV r1, #0x80
		STR r1, [r4, #0x68]
|loc_08010136|
		NEG r0, r0
		STR r0, [r4, #4]
		LDR r0, [r4, #0x5c]
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0x10036
		ADD r1, sp, #0x18
		B        |inc_0x0158_0x143f2| + 0xffee
|loc_08010144|
|unk_08010144|
		B        |loc_08010192|
		LDR r0, [pc, #0x188]
		STR r6, [sp, #0x20]
		LDR r0, [r0]
		ADD r2, r4, #0
		ADD r2, #0x64
		STR r7, [sp]
		ADD r3, sp, #8
		BL       |sub_0802f1c6|
		LDR r0, [r4, #0x64]
		CMP r0, #0
		BEQ      |loc_0801022C|
		MOV r0, #0x1f
		LDR r1, [sp, #8]
		MVN r0, r0
		CMP r1, r0
		BLT      |loc_0801017E|
		MOV r2, #0xff
		LDR r1, [sp, #8]
		ADD r2, #0x11
		CMP r1, r2
		BGT      |loc_0801017E|
		LDR r1, [sp, #0xc]
		CMP r1, r0
		BLT      |loc_0801017E|
		LDR r0, [sp, #0xc]
		CMP r0, #0xc0
		BLE      |loc_08010182|
|loc_0801017E|
		STR r6, [r4, #0x64]
		B        |loc_0801022C|
|loc_08010182|
		STR r6, [r5, #4]
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		SUB r0, r0, r1
		STR r0, [r5, #8]
		B        |loc_0801022C|
		STR r6, [r4, #0x64]
		B        |loc_0801022C|
