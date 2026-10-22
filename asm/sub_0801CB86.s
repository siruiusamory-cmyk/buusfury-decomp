	CODE16
|sub_0801CB86|
	LSR      r1, r6, #1
	STR      r3, [sp, #0x3e0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	CMP      r7, #0xdc
	LSR      r1, r6, #1
	CMP      r2, #0xaa
	LSL      r0, r0, #0
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDR      r0, [pc, #0x210]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x4c
	CMP      r1, #0
	BNE      |sub_0801CBB6|
	MOV      r0, #1
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
