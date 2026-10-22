	CODE16
|sub_0802084C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r2, [r4, #0x10]
	ADD      r0, r1, #0
	SUB      sp, #0x54
	LDR      r5, [pc, #0x230]
	CMP      r2, #0
	BEQ      |sub_08020896|
	CMP      r2, #1
	BEQ      |loc_080208CE|
	CMP      r2, #2
	BNE      |loc_08020948|
	LDR      r0, [r4, #0x30]
	LDR      r1, [r4, #0x34]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	STR      r1, [sp, #0x4c]
	STR      r0, [sp, #0x48]
	LDR      r2, [r4, #0x20]
	ADD      r0, r2, r0
	STR      r0, [r4, #0x20]
	LDR      r0, [r4, #0x24]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x38]
	SUB      r0, #3
	STR      r0, [r4, #0x38]
	BPL      |loc_08020948|
	LDR      r0, [pc, #0x1f0]
	ADD      r1, r4, #0
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x54
	POP      {r4, r5, r6, r7, pc}
