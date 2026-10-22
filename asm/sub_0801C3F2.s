	IMPORT |GBARam_Free|
	IMPORT |GBARam_Malloc|
	CODE16
|sub_0801C3F2|
	ADD      r4, r0, #0
	ADD      r6, r1, #0
	STR      r3, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0xdd08
	LDR      r5, [pc, #0x2a0]
	MOV      r1, #0x51
	LDR      r2, [pc, #0x2a0]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r7, [pc, #0x2a0]
	LDR      r0, [r5]
	MOV      r2, #0x40
	MOV      r3, #0
	ADD      r0, r0, r7
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r3, #0
	LDR      r0, [pc, #0x294]
	STR      r3, [r4, #0xc]
	LDRB     r0, [r0]
	MOV      r7, #1
	LSL      r7, r7, #0xa
	CMP      r0, #0
	BEQ      |sub_0801C486|
	CMP      r0, #1
	BNE      |loc_0801C482|
	ADD      r1, r6, #0
	ADD      r4, sp, #0x1c
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xfca2
	ADD      r2, r4, #0
	ADD      r2, #8
	ADD      r6, sp, #0x2c
	ADD      r1, sp, #0x1c
	ADD      r0, sp, #0xc
	BL       |inc_0x049120_0x055620| + 0x9e94
	LDR      r0, [sp, #0xc]
	ADD      r4, sp, #0x34
	ASR      r1, r0, #1
	LDR      r0, [sp, #0x10]
	STR      r1, [sp, #4]
	ASR      r0, r0, #1
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x30]
	MOV      r0, #0
	STR      r0, [sp, #0x14]
	MOV      r0, #2
	STR      r1, [sp, #0x2c]
	ADD      r1, r6, #0
	STR      r0, [sp, #0x18]
	ADD      r0, r4, #0
	ADD      r2, sp, #0x14
	BL       |inc_0x049120_0x055620| + 0x9e94
	MOV      r2, #0x38
	LDR      r0, [pc, #0x248]
	STR      r2, [sp, #8]
	MOV      r3, #7
	ADD      r1, r4, #0
	STR      r0, [sp]
	MOV      r0, #0
	LDR      r2, [pc, #0x240]
	STR      r7, [sp, #4]
	BL       |loc_0802A81C|
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0801C482|
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
