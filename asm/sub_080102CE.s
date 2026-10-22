	CODE16
|sub_080102CE|
	LSL      r0, r0, #0
	MOV      r7, #0x14
	LSR      r7, r0, #0x20
	LSL      r2, r4, #8
	LSL      r0, r0, #0
	PUSH     {r4, r5, lr}
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r1, #7
	SUB      sp, #0x14
	BEQ      |sub_080102FC|
	CMP      r1, #0x16
	BNE      |loc_08010378|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BNE      |loc_0801030E|
	ADD      sp, #0x14
	POP      {r4, r5, pc}
