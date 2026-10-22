	CODE16
|loc_0801183E|
	PUSH     {r3, r4, r5, lr}
	STRH     r1, [r0, #0xe]
	LDRH     r1, [r0, #0xc]
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x248]
	CMP      r1, r0
	BEQ      |loc_08011872|
	LDR      r5, [pc, #0x23c]
	LDR      r0, [r5, #8]
	BL       |loc_0801142A|
	LDRH     r1, [r4, #0xe]
	LDR      r0, [r5, #8]
	BL       |loc_0801124C|
	ADD      r3, r0, #1
	BNE      |loc_08011870|
	LDRH     r1, [r4, #0xe]
	LDR      r0, [r5, #8]
	BL       |sub_08011732|
	LDRH     r1, [r4, #0xe]
	LDR      r0, [r5, #8]
	BL       |loc_0801124C|
|loc_08011870|
	STRH     r0, [r4, #0xc]
|loc_08011872|
	POP      {r3, r4, r5, pc}
