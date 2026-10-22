	CODE16
|sub_08029A3A|
	LSL      r0, r0, #0
	ADD      r2, sp, #0x2f0
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [r2, #8]
	LDRB     r3, [r0, #0xc]
	LDRB     r5, [r4, #1]
	CMP      r3, r5
	BEQ      |loc_08029A52|
	LDRB     r4, [r4]
	CMP      r3, r4
	BNE      |sub_08029A5C|
|loc_08029A52|
	LDR      r0, [r0, #0x10]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, r4, r5, pc}
