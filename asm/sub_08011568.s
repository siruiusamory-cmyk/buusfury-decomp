	CODE16
|sub_08011568|
	PUSH     {r4, lr}
	LDRH     r1, [r0, #0xc]
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x29c]
	LDR      r0, [r0, #8]
	BL       |loc_0801142A|
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #0xc]
	POP      {r4, pc}
