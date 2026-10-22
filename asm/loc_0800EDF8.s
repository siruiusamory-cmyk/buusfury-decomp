	CODE16
|loc_0800EDF8|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x58]
	ADD      r5, r1, #0
	LDR      r0, [r0, #0x50]
	LDR      r6, [pc, #0x3e0]
	CMP      r0, #0
	BEQ      |loc_0800EE0E|
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x6d00
|loc_0800EE0E|
	LDR      r0, [r5, #4]
	MOV      r7, #0
	STR      r0, [r4, #0x3c]
	LDR      r1, [r4, #0x34]
	CMP      r1, r0
	BEQ      |loc_0800EE20|
	STR      r0, [r4, #0x34]
	STR      r7, [r4, #0x38]
	STR      r7, [r4, #0x30]
|loc_0800EE20|
	LDR      r0, [r4, #0x18]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [pc, #0x3b4]
	SUB      r0, #4
	STR      r0, [r4, #0x18]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #0x58]
	LDRH     r0, [r0, #2]
	LDRH     r1, [r5, #2]
	CMP      r0, r1
	BEQ      |loc_0800EE60|
	LDR      r0, [r4, #0x40]
	BL       |GBARam_Free|
	LDRH     r0, [r5, #2]
	BL       |GBARam_Malloc|
	STR      r0, [r4, #0x40]
	LDRH     r1, [r5, #2]
	ADD      r0, r4, #0
	BL       |loc_0801183E|
|loc_0800EE60|
	STR      r5, [r4, #0x58]
	LDR      r0, [r5, #0x50]
	CMP      r0, #0
	BEQ      |sub_0800EE74|
	MOV      r2, #0x80
	ADD      r0, r6, #0
	LDR      r1, [pc, #0x378]
	BL       |inc_0x049120_0x055620| + 0x5370
	POP      {r3, r4, r5, r6, r7, pc}
