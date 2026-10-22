	CODE16
|loc_0803C8FC|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x228]
	MOV      r7, #0
	LDR      r5, [r0]
	ADD      r4, r1, #0
	CMP      r5, #0
	SUB      sp, #0x5c
	BEQ      |loc_0803C9F2|
	MOV      r0, #0xff
	ADD      r0, #0xcd
	LDR      r0, [r0, r5]
	CMP      r0, #0
	BEQ      |loc_0803C9F2|
	ADD      r1, r4, #0
	ADD      r0, sp, #0x4c
	BL       |inc_0x0158_0x143f2| + 0xfd20
	LDR      r0, [sp, #0x4c]
	LDR      r1, [sp, #0x54]
	LDR      r2, [sp, #0x58]
	ADD      r0, r0, r1
	LDR      r1, [sp, #0x50]
	STR      r0, [sp, #0x2c]
	ADD      r1, r1, r2
	ASR      r0, r0, #1
	ASR      r6, r1, #1
	STR      r1, [sp, #0x30]
	STR      r0, [sp, #0x2c]
	STR      r0, [sp, #0x44]
	ADD      r0, sp, #0x34
	STR      r6, [sp, #0x30]
	ADD      r1, r4, #0
	STR      r6, [sp, #0x48]
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDRB     r0, [r4, #0x10]
	MOV      r2, sp
	CMP      r0, #0
	BEQ      |sub_0803C960|
	CMP      r0, #1
	BEQ      |sub_0803C960|
	CMP      r0, #2
	BEQ      |loc_0803C956|
	CMP      r0, #3
	BNE      |sub_0803C968|
|loc_0803C956|
	LDR      r0, [sp, #0x58]
	STR      r6, [sp, #8]
	ADD      r0, #3
	STR      r0, [sp, #0x10]
	B        |sub_0803C968|
