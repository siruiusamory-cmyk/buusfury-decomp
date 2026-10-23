	CODE16
|sub_080378A0|
	PUSH     {r3, r4, r5, lr}
	STR      r1, [r0, #0x60]
	LDR      r1, [r0, #0x54]
	LDR      r2, [pc, #0x114]
	CMP      r1, #0x3c
	BGE      |sub_080378B6|
	ADD      r1, r0, #0
	LDR      r0, [r2, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	POP      {r3, r4, r5, pc}
