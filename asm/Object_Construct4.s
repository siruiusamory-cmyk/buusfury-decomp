	CODE16
|Object_Construct4|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	BNE      |loc_0800B868|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800B868|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800B868|
	LDR      r0, [pc, #0x3dc]
	MOV      r6, #5
	LSL      r6, r6, #8
	LDR      r5, [pc, #0x3dc]
	STR      r0, [r4]
	STRH     r6, [r4, #0xe]
	LDR      r0, [r5, #8]
	ADD      r1, r6, #0
	BL       |loc_0801124C|
	ADD      r3, r0, #1
	BNE      |loc_0800B890|
	ADD      r1, r6, #0
	LDR      r0, [r5, #8]
	BL       |sub_08011732|
	ADD      r1, r6, #0
	LDR      r0, [r5, #8]
	BL       |loc_0801124C|
|loc_0800B890|
	STRH     r0, [r4, #0xc]
	LDR      r0, [pc, #0x3bc]
	MOV      r1, #8
	STR      r0, [r4]
	MOV      r0, #0x10
	STRB     r0, [r4, #8]
	MOV      r0, #0
	STR      r0, [r4, #4]
	STR      r1, [r4, #0x28]
	STR      r0, [r4, #0x14]
	STR      r0, [r4, #0x18]
	STR      r0, [r4, #0x2c]
	STR      r0, [r4, #0x10]
	MOV      r0, #0xff
	STRB     r0, [r4, #0x1c]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800B8B2|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x398]
	ADD      r6, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0x18]
	LDR      r5, [pc, #0x38c]
	CMP      r0, #0
	BEQ      |loc_0800B8CC|
	ADD      r1, r0, #0
	LDR      r0, [r5, #8]
	BL       |loc_08011944|
|loc_0800B8CC|
	LDR      r0, [r4, #0x2c]
	CMP      r0, #0
	BEQ      |loc_0800B8DA|
	ADD      r1, r0, #0
	LDR      r0, [r5, #8]
	BL       |loc_08011944|
|loc_0800B8DA|
	LDR      r0, [pc, #0x36c]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x370]
	CMP      r1, r0
	BEQ      |loc_0800B8EC|
	LDR      r0, [r5, #8]
	BL       |loc_0801142A|
|loc_0800B8EC|
	LDR      r0, [pc, #0x368]
	CMP      r6, #0
	STR      r0, [r4]
	BEQ      |loc_0800B8FA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0800B8FA|
	POP      {r4, r5, r6, pc}
