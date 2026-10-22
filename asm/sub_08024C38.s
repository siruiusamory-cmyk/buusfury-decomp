	CODE16
|sub_08024C38|
	PUSH     {r4, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r4, [pc, #0x100]
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x118c6
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x11458
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0xf0]
	SUB      sp, #0x1fc
	ADD      r4, r0, #0
	LDR      r0, [r7, #4]
	SUB      sp, #8
	BL       |inc_0x0158_0x143f2| + 0x11426
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x40]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #8]
	CMP      r0, #0
	BEQ      |Blend_WriteControlAndAlpha3|
	LDRB     r0, [r4, #5]
	LDR      r1, [pc, #0x114]
	ADD      r0, #0xff
	STRB     r0, [r4, #5]
	STRB     r0, [r1, #2]
	LDRB     r0, [r4, #5]
	CMP      r0, #0
	BNE      |loc_08024D40|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      sp, #0x1fc
	ADD      sp, #8
	POP      {r4, r5, r6, r7, pc}
