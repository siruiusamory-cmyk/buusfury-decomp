	CODE16
|Battle_SpawnDamageObject|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	ADD      r6, #0x10
	MOV      r0, #8
	SUB      sp, #0x18
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800E904|
	LDR      r1, [pc, #0x23c]
	STR      r1, [r0]
	MOV      r1, #0xc
	STRB     r1, [r0, #4]
|loc_0800E904|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800ED80|
	ADD      r1, r4, #0
	ADD      r0, sp, #8
	BL       |Object_GetPoints|
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x10]
	ADD      r4, #0xff
	ADD      r0, r0, r1
	ASR      r0, r0, #1
	STR      r0, [sp]
	LDR      r0, [sp, #0xc]
	ADD      r4, #0xc1
	STR      r0, [sp, #4]
	LDR      r0, [pc, #0x210]
	LDR      r0, [r0, #4]
	LDR      r1, [r4, #0x14]
	SUB      r2, r0, r1
	ADD      r1, r5, #0
	ADD      r1, #0x18
	CMP      r2, #8
	BGE      |sub_0800E94C|
	LDR      r2, [r4, #0x18]
	CMP      r2, #0
	BEQ      |sub_0800E94C|
	ADD      r0, r2, #0
	LDR      r2, [r2, #0x14]
	LDR      r1, [r1]
	ADD      r1, r2, r1
	STR      r1, [r0, #0x14]
	BL       |loc_0800AB54|
	B        |loc_0800E96A|
