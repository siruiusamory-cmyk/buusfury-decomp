	CODE16
|loc_0803A8AC|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x3a0]
	ADD      r1, #0x18
	ADD      sp, r3
	LDR      r6, [r1]
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x20]
	MOV      r5, #1
	LSL      r5, r5, #0xb
	ADD      r7, r1, #0
	CMP      r6, r0
	MOV      ip, r0
	BGE      |loc_0803A8E8|
	LDR      r0, [r4, #0x18]
	ADD      r3, r5, #0
	LDR      r2, [r1, #8]
	ADD      r3, sp
	STR      r2, [r3, #0x30]
	MOV      lr, r0
	CMP      r0, r2
	BGE      |loc_0803A8E8|
	LDR      r0, [r1, #4]
	STR      r0, [r3, #0x2c]
	LDR      r2, [r4, #0x24]
	CMP      r0, r2
	BGE      |loc_0803A8E8|
	LDR      r0, [r4, #0x1c]
	LDR      r1, [r1, #0xc]
	CMP      r0, r1
	BLT      |sub_0803A908|
|loc_0803A8E8|
	LDRB     r0, [r4, #8]
	CMP      r0, #0
	BEQ      |loc_0803A902|
	MOV      r0, #0
	STRB     r0, [r4, #8]
	LDRB     r0, [r4, #4]
	LDR      r1, [pc, #0x35c]
	LSL      r0, r0, #0xb
	ADD      r0, r0, r1
	ADD      r2, r5, #0
	MOV      r1, #0
	BL       |inc_0x049120_0x055620| + 0xc
|loc_0803A902|
	LDR      r3, [pc, #0x354]
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
