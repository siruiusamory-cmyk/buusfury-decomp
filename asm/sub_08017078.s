	CODE16
|sub_08017078|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x84]
	LDR      r4, [pc, #0x7c]
	LDR      r1, [r3]
	ADD      r5, r3, #0
	LDRH     r1, [r1, #4]
	LDR      r5, [r5, #4]
	MOV      r7, #0
	ADD      r5, r5, r4
	LSL      r2, r1, #0x1c
	LSR      r2, r2, #0x1f
	CMP      r2, #0
	LDR      r4, [pc, #0x84]
	BEQ      |sub_080170A8|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0xe1
	ADD      r3, r7, #0
	MOV      r2, #0x40
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
