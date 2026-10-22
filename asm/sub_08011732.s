	CODE16
|sub_08011732|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	MOV      r0, #0
	SUB      sp, #0xc
	STR      r0, [sp, #4]
	ADD      r0, r6, #0
	BL       |loc_080116FC|
	LDR      r1, [sp, #0x10]
	CMP      r0, r1
	BGE      |loc_08011806|
	LDR      r0, [pc, #0xc8]
	ADD      r0, r6, r0
	STR      r0, [sp, #8]
	ADD      r7, r6, #4
|loc_08011750|
	LDR      r4, [r6, #4]
	SUB      r4, #1
	BMI      |loc_080117AA|
|loc_08011756|
	LSL      r0, r4, #2
	ADD      r0, r0, r7
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	ADD      r5, r0, #0
	LDR      r2, [r1, #0x18]
	ADD      r2, r2, r1
	LDR      r1, [sp, #4]
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #1
	BEQ      |sub_080117D8|
	CMP      r0, #2
	BNE      |loc_080117A6|
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [sp, #8]
	LDR      r1, [r0]
	ADD      r2, r1, #1
	STR      r2, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r5, [r0, #4]
	ADD      r1, r4, #0
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x6d34
	LDR      r0, [sp, #4]
	CMP      r0, #0xb
	BLT      |loc_080117A6|
	ADD      r0, r6, #0
	BL       |loc_080116FC|
	LDR      r1, [sp, #0x10]
	CMP      r0, r1
	BGE      |loc_080117AA|
|loc_080117A6|
	SUB      r4, #1
	BPL      |loc_08011756|
|loc_080117AA|
	LDR      r0, [sp, #4]
	ADD      r0, #1
	STR      r0, [sp, #4]
	ADD      r0, r6, #0
	BL       |loc_080116FC|
	LDR      r1, [sp, #0x10]
	CMP      r0, r1
	BLT      |loc_08011750|
	ADD      r0, r6, #0
	BL       |loc_080115B0|
	LDR      r0, [pc, #0x48]
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x2de
	MOV      r0, #0x41
	LSL      r0, r0, #3
	ADD      r5, r6, r0
	LDR      r4, [r5]
	SUB      r4, #1
	BMI      |loc_08011802|
	B        |sub_080117EE|
