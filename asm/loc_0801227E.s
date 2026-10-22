	CODE16
|loc_0801227E|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_08012298|
	LDR      r0, [pc, #0x138]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08012298|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08012298|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |sub_08012230|
	ADD      r1, r0, #0
	ADD      r3, r6, #0
	ADD      r0, r4, #0
	LDRB     r2, [r5, #3]
	BL       |sub_08012012|
	LDR      r0, [pc, #0x120]
	STR      r0, [r4]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x11c]
	MOV      r0, #1
	ADD      r4, r1, #0
	LSL      r0, r0, #0x10
	ADD      sp, r3
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	LDR      r0, [r4, #4]
	LDR      r1, [pc, #0x100]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x18
	LDR      r0, [r1, r0]
	ADD      r1, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [r4, #4]
	ADD      r6, sp, #0x80
	LSR      r1, r0, #0x15
	LSL      r0, r0, #0xb
	LSR      r0, r0, #0x11
	LSL      r0, r0, #1
	LSL      r2, r1, #1
	ADD      r1, r0, r5
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x24
	LDR      r0, [r4, #4]
	MOV      r7, #0
	LSR      r0, r0, #0x15
	LSL      r0, r0, #1
	STRH     r7, [r6, r0]
	ADD      r0, r5, #0
	BL       |GBARam_Free|
	ADD      r1, r4, #0
	ADD      r1, #8
	MOV      r3, #0x21
	LSL      r3, r3, #7
	ADD      r3, sp
	STR      r7, [sp, #0x14]
	STR      r7, [sp, #0x58]
	LDR      r2, [r3, #8]
	ADD      r4, sp, #0x14
	ADD      r0, sp, #0x14
	BL       |loc_08004038|
	MOV      r3, #0x21
	LSL      r3, r3, #7
	ADD      r0, r4, #4
	STR      r0, [sp, #0x10]
	ADD      r3, sp
	LDR      r0, [r3]
	ADD      r1, r6, #0
	ADD      r0, #8
	ADD      r4, r0, #0
	ADD      r2, sp, #0x10
	BL       |inc_0x03d784_0x041118| + 0x3f8
	LDR      r3, [pc, #0xa8]
	ADD      r0, r4, #0
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
