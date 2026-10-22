	CODE16
|sub_08012230|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	MOV      r0, #1
	ADD      r5, r1, #0
	LSL      r0, r0, #0x10
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	LDR      r0, [r5, #4]
	LDR      r1, [pc, #0x188]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x18
	LDR      r0, [r1, r0]
	ADD      r1, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [r5, #4]
	LSR      r1, r0, #0x15
	LSL      r0, r0, #0xb
	LSR      r0, r0, #0x11
	LSL      r0, r0, #1
	LSL      r2, r1, #1
	ADD      r1, r0, r4
	ADD      r0, r6, #0
	ADD      r0, #8
	ADD      r7, r0, #0
	BL       |inc_0x049120_0x055620| + 0x24
	LDR      r1, [r5, #4]
	MOV      r0, #0
	LSR      r1, r1, #0x15
	LSL      r1, r1, #1
	ADD      r1, r1, r6
	STRH     r0, [r1, #8]
	ADD      r0, r4, #0
	BL       |GBARam_Free|
	ADD      r0, r7, #0
	POP      {r3, r4, r5, r6, r7, pc}
