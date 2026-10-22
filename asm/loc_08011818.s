	CODE16
|loc_08011818|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x270]
	LDRH     r1, [r0, #0xe]
	ADD      r4, r0, #0
	LDR      r0, [r5, #8]
	BL       |loc_0801124C|
	ADD      r3, r0, #1
	BNE      |loc_0801183A|
	LDRH     r1, [r4, #0xe]
	LDR      r0, [r5, #8]
	BL       |sub_08011732|
	LDRH     r1, [r4, #0xe]
	LDR      r0, [r5, #8]
	BL       |loc_0801124C|
|loc_0801183A|
	STRH     r0, [r4, #0xc]
	POP      {r3, r4, r5, pc}
