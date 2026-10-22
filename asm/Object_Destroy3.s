	CODE16
|Object_Destroy3|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x8c]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0x16]
	LDR      r0, [pc, #0x7c]
	CMP      r1, r0
	BEQ      |loc_0800CE74|
	LDR      r0, [pc, #0x78]
	LDR      r0, [r0]
	BL       |loc_0801142A|
|loc_0800CE74|
	LDR      r0, [r4, #0xc]
	CMP      r0, #0
	BEQ      |loc_0800CE86|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800CE86|
	LDR      r0, [pc, #0x68]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0800CE94|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0800CE94|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	LDRH     r1, [r0, #0x16]
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x48]
	LDR      r0, [r0]
	BL       |loc_0801142A|
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #0x16]
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDRH     r0, [r0, #0x16]
	LDR      r1, [pc, #0x30]
	CMP      r0, r1
	BNE      |loc_0800CECE|
	LDR      r0, [r4, #0x5c]
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x28]
	LDR      r0, [r0]
	BL       |loc_0801124C|
	STRH     r0, [r4, #0x16]
	ADD      r0, r4, #0
	BL       |sub_0800CD00|
|loc_0800CECE|
	POP      {r4, pc}
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BNE      |sub_0800CEDE|
	BL       |sub_0800CD00|
	MOV      r0, #0
	POP      {r3, pc}
