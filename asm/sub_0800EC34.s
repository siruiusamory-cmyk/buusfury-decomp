	CODE16
|sub_0800EC34|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1a8]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |loc_0800EC4A|
	LDR      r0, [r0, #8]
	BL       |inc_0x049120_0x055620| + 0x6d00
|loc_0800EC4A|
	LDR      r0, [r4, #0x58]
	LDR      r0, [r0, #0x50]
	CMP      r0, #0
	BEQ      |loc_0800EC58|
	LDR      r0, [pc, #0x194]
	BL       |inc_0x049120_0x055620| + 0x6d00
|loc_0800EC58|
	LDR      r0, [r4, #0x24]
	CMP      r0, #0
	BEQ      |loc_0800EC6A|
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800EC6A|
	LDR      r0, [r4, #0x14]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #0x18]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #0x40]
	BL       |GBARam_Free|
	LDR      r0, [pc, #0x14c]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x158]
	CMP      r1, r0
	BEQ      |loc_0800ECA0|
	LDR      r0, [pc, #0x144]
	LDR      r0, [r0]
	BL       |loc_0801142A|
|loc_0800ECA0|
	LDR      r0, [pc, #0x14c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0800ECAE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0800ECAE|
	POP      {r3, r4, r5, pc}
|loc_0800ECB0|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x5c]
	ADD      r5, r1, #0
	CMP      r0, #0
	BEQ      |loc_0800ECC2|
	LDR      r0, [r0, #8]
	BL       |inc_0x049120_0x055620| + 0x6d00
|loc_0800ECC2|
	LDMIA    r5!, {r0, r1}
	BL       |loc_08013E38|
	STR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |loc_0800ECD8|
	LDRH     r2, [r0, #2]
	LDR      r1, [r0, #4]
	LDR      r0, [r0, #8]
	BL       |inc_0x049120_0x055620| + 0x5370
|loc_0800ECD8|
	POP      {r3, r4, r5, pc}
