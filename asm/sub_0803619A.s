	CODE16
|sub_0803619A|
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	ADD      r2, #0x78
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	STRH     r0, [r3, #4]
	LSR      r3, r5, #1
	ADR      r7, |loc_08036240|
	LSR      r5, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	LDR      r0, [pc, #0x1b4]
	ADD      r4, r1, #0
	LDR      r5, [r0]
	SUB      sp, #0x74
	CMP      r5, #0
	BNE      |sub_080361CE|
	MOV      r0, #0
	ADD      sp, #0x74
	POP      {r4, r5, r6, r7, pc}
