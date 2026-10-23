	CODE16
|sub_0801FF98|
	EXPORT |sub_0801FF98|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |inc_0x0158_0x143f2| + 0x55e8
	MOV      r2, #1
	LSL      r2, r2, #0x1a
	LDRH     r0, [r2]
	MOV      r1, #0x41
	LSL      r1, r1, #6
	ORR      r0, r1
	STRH     r0, [r2]
	MOV      r0, #0xb
	LSL      r0, r0, #6
	ADD      r0, r4, r0
	LDR      r0, [r0, #0x38]
	CMP      r0, #0
	BEQ      |loc_0801FFC4|
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7394
	BL       |inc_0x03d784_0x041118| + 0x29dc
|loc_0801FFC4|
	MOV      r0, #5
	ADD      r1, r4, #0
	LSL      r0, r0, #7
	ADD      r0, r4, r0
	ADD      r1, #0xff
	ADD      r1, #0x2d
	ADD      r4, #0xff
	ADD      r4, #1
	LDR      r2, [r4, #0xc]
	LDR      r0, [r0, #0x34]
	LSL      r2, r2, #7
	LDR      r1, [r1, r2]
	STR      r1, [r0, #8]
	POP      {r4, pc}
	PUSH     {r3, lr}
	BL       |inc_0x0158_0x143f2| + 0x570c
	MOV      r2, #1
	LSL      r2, r2, #0x1a
	LDRH     r0, [r2]
	MOV      r1, #0x41
	LSL      r1, r1, #6
	BIC      r0, r1
	STRH     r0, [r2]
	POP      {r3, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r6, r0, #0
	LDR      r3, [pc, #0x28c]
	LDR      r0, [pc, #0x288]
	LDR      r1, [r3, #4]
	ADD      r4, r5, #0
	ADD      r4, #0xff
	ADD      r6, #0xff
	ADD      r0, r1, r0
	ADD      r6, #0x2d
	ADD      r4, #1
	MOV      r7, #0
	CMP      r2, #0
	LDR      r1, [pc, #0x27c]
	BEQ      |sub_08020054|
	CMP      r2, #1
	BEQ      |loc_080200FE|
	MOV      r1, #5
	LSL      r1, r1, #7
	ADD      r5, r5, r1
	LDR      r1, [pc, #0x26c]
	SUB      r1, #0xc
	CMP      r2, #2
	BEQ      |loc_08020100|
	CMP      r2, #3
	BNE      |loc_08020050|
	LDR      r2, [r4, #0xc]
	CMP      r2, #2
	BGE      |loc_08020048|
	ADD      r3, r7, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0xc]
	ADD      r0, #1
	STR      r0, [r4, #0xc]
	LSL      r0, r0, #7
	LDR      r0, [r6, r0]
	LDR      r1, [r5, #0x34]
	STR      r0, [r1, #8]
|loc_08020048|
	MOV      r0, #0
	MVN      r0, r0
	STR      r0, [r4, #0x1c]
	STR      r7, [r4, #0x10]
|loc_08020050|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
