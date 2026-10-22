	CODE16
|sub_08015792|
	LSL      r0, r0, #0
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STRH     r0, [r1, #2]
	LSR      r3, r5, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r2, [pc, #0x178]
	LDR      r4, [pc, #0x178]
	LDR      r1, [r2]
	ADD      r5, r2, #0
	LDRH     r1, [r1, #4]
	LDR      r5, [r5, #4]
	SUB      sp, #0xc
	ADD      r4, r5, r4
	LSL      r3, r1, #0x1c
	LSR      r3, r3, #0x1f
	CMP      r3, #0
	STR      r4, [sp, #8]
	LDR      r6, [pc, #0x168]
	BEQ      |sub_080157D4|
	ADD      r1, r6, #0
	MOV      r3, #0
	MOV      r2, #0x40
	LDR      r0, [sp, #8]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
