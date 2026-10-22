	CODE16
|sub_0803B0A0|
	CMP      r0, r1
	BLT      |loc_0803B0FC|
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x2348
	LDR      r2, [r4, #0x14]
	LDR      r1, [r4, #0x18]
	SUB      r2, #0x32
	STR      r1, [sp, #0x30]
	ADD      r1, r2, #0
	STR      r2, [sp, #0x2c]
	LDR      r2, [sp, #0x30]
	STR      r1, [sp, #0x34]
	MOV      r1, #1
	LSL      r1, r1, #0xa
	STR      r2, [sp, #0x38]
	MOV      r2, #0x37
	ADD      r0, r0, r7
	STR      r0, [sp]
	ADD      r3, r6, #0
	STR      r2, [sp, #8]
	STR      r1, [sp, #4]
	ADD      r1, sp, #0x34
	LDR      r2, [pc, #0xfc]
	MOV      r0, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0xe42a
	ADD      r1, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	B        |loc_0803B0FC|
|sub_0803B0E0|
|unk_0803B0E0|
		MOV r0, #1
		LSL r0, r0, #0xe
		CMP r6, r0
		BGE      |loc_0803B0F4|
		LDR r0, [pc, #0xe4]
		BL       |sub_08054A64|
		ADD r0, r6, r0
		STR r0, [r4, #0x10]
		B        |loc_0803B0FC|
|loc_0803B0F4|
		LDR r0, [pc, #0xd0]
		ADD r6, #0x80
		STRB r1, [r0]
		STR r6, [r4, #0x10]
