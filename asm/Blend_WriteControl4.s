	CODE16
|Blend_WriteControl4|
	PUSH     {r3, lr}
	LDRB     r1, [r0, #0xe]
	CMP      r1, #1
	BNE      |sub_080253FE|
	BL       |loc_08024BE6|
	LDR      r0, [pc, #0x2cc]
	LDR      r1, [pc, #0x2cc]
	STRH     r0, [r1, #0x10]
	POP      {r3, pc}
