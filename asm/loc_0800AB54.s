	CODE16
|loc_0800AB54|
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r4, r0, #0
	MOV      r2, #8
	MOV      r1, #0x20
	MOV      r0, sp
	MOV      r5, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r1, [pc, #0x214]
	LDR      r0, [r1, #4]
	LDR      r2, [r4, #0x1c]
	CMP      r2, #0
	BNE      |loc_0800AB72|
	LDR      r0, [r1, #8]
|loc_0800AB72|
	STR      r0, [sp, #0xc]
	LDR      r0, [r4, #0x18]
	ADD      r3, sp, #0
	STRB     r0, [r3, #3]
	MOV      r0, #1
	LDR      r1, [pc, #0x200]
	STRB     r0, [r3, #2]
	STR      r1, [sp, #0x20]
	STRB     r0, [r3]
	MOV      r0, #0x10
	MOV      r1, #7
	STR      r1, [sp, #8]
	STR      r0, [sp, #4]
	STRB     r0, [r4, #8]
	STR      r0, [r4, #0x10]
	LDR      r0, [sp, #0x24]
	LDR      r2, [sp, #0x30]
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r1, [pc, #0x1e8]
	LDR      r0, [r4, #0x14]
	ADD      r0, r0, r1
	ASR      r2, r0, #0xa
	ADD      r0, r5, #0
	ADR      r1, |loc_0800AD88|
	BL       |inc_0x03d784_0x041118| + 0x512
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x1e0]
	LDR      r2, [pc, #0x1cc]
	LSL      r0, r0, #5
	ADD      r1, r0, r1
	ADD      r2, #0x10
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x3c
	MOV      r1, #0
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r6, [sp, #0x28]
	BNE      |sub_0800ABE6|
	MOV      r0, #0x28
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800ABE6|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
