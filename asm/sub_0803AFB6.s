	CODE16
|sub_0803AFB6|
	LDR      r5, [pc, #0x20c]
	BGE      |sub_0803B09E|
	LDR      r1, [pc, #0x20c]
	MOV      r0, #1
	STRB     r0, [r1]
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	LSL      r7, r1, #2
	MOV      r6, #4
	CMP      r0, r1
	BLT      |loc_0803B006|
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x2348
	LDR      r1, [r4, #0x14]
	LDR      r2, [r4, #0x18]
	STR      r1, [sp, #0x2c]
	ADD      r2, #0x32
	STR      r1, [sp, #0x34]
	LSL      r1, r6, #8
	STR      r2, [sp, #0x30]
	STR      r2, [sp, #0x38]
	MOV      r2, #0x37
	ADD      r0, r0, r7
	STR      r0, [sp]
	ADD      r3, r6, #0
	STR      r2, [sp, #8]
	STR      r1, [sp, #4]
	ADD      r1, sp, #0x34
	LDR      r2, [pc, #0x1d4]
	MOV      r0, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0xe42a
	ADD      r1, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0803B006|
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0803B04A|
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x2348
	LDR      r1, [r4, #0x14]
	LDR      r2, [r4, #0x18]
	STR      r1, [sp, #0x2c]
	SUB      r2, #0x32
	STR      r1, [sp, #0x34]
	MOV      r1, #1
	LSL      r1, r1, #0xa
	STR      r2, [sp, #0x30]
	STR      r2, [sp, #0x38]
	MOV      r2, #0x37
	ADD      r0, r0, r7
	STR      r0, [sp]
	ADD      r3, r6, #0
	STR      r2, [sp, #8]
	STR      r1, [sp, #4]
	ADD      r1, sp, #0x34
	LDR      r2, [pc, #0x190]
	MOV      r0, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0xe42a
	ADD      r1, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0803B04A|
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0803B092|
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x2348
	LDR      r2, [r4, #0x14]
	LDR      r1, [r4, #0x18]
	ADD      r2, #0x32
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
	LDR      r2, [pc, #0x148]
	MOV      r0, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0xe42a
	ADD      r1, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0803B092|
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	B        |sub_0803B0A0|
