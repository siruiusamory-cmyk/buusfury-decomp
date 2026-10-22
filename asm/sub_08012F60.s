	CODE16
|sub_08012F60|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |sub_08012F8C|
	ADD      r0, r4, #0
	BL       |sub_08012A24|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
