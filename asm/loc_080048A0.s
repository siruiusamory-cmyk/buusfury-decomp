	CODE16
|loc_080048A0|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x24c]
	ADD      r5, r0, #0
	ADD      sp, r3
	MOV      r4, sp
	MOV      r0, sp
	ADD      r6, r1, #0
	BL       |loc_08004838|
	MOV      r2, #0x8b
	LSL      r2, r2, #4
	MUL      r2, r6
	MOV      r3, #0x8b
	LDR      r0, [pc, #0x238]
	LSL      r3, r3, #4
	ADD      r2, #0x10
	ADD      r1, r4, #0
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x24b6
	LDR      r6, [pc, #0x218]
	MOV      r0, sp
	ADD      r1, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x24ca
	MOV      r1, #0x11
	LSL      r1, r1, #7
	ADD      r1, r4, r1
	LDR      r1, [r1, #0x28]
	CMP      r0, r1
	BNE      |sub_080048EC|
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x719c
	LDR      r3, [pc, #0x210]
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
