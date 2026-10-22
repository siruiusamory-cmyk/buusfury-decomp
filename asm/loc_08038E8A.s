	CODE16
|loc_08038E8A|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x48]
	ADD      r5, r1, #0
	CMP      r0, #0
	BEQ      |loc_08038EA4|
	LDR      r0, [r5]
	MOV      r1, sp
	ADD      r0, #0x20
	STR      r0, [sp]
	LDR      r0, [r4, #0x48]
	BL       |loc_08038E8A|
|loc_08038EA4|
	LDRB     r0, [r4, #0x10]
	LDR      r3, [pc, #0x80]
	LDR      r2, [r5]
	LSL      r1, r0, #3
	LDR      r0, [r3, r1]
	MUL      r2, r0
	LDR      r0, [r4, #0x20]
	ADD      r0, r0, r2
	STR      r0, [r4, #0x20]
	ADD      r0, r1, r3
	LDR      r0, [r0, #4]
	LDR      r1, [r5]
	MUL      r1, r0
	LDR      r0, [r4, #0x24]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x24]
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	MOV      r1, #0
	STR      r1, [r0, #0x60]
	BL       |inc_0x153f2_0x1a3f2| + 0x4802
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x60]
	ADD      r5, r1, #0
	CMP      r0, #0
	BEQ      |sub_08038EE2|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
