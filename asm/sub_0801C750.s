	CODE16
|sub_0801C750|
	PUSH     {r4, r5, r6, lr}
	ADD      r1, r0, #0
	ADD      r1, #0x28
	ADD      r2, r1, #0
	LDR      r3, [r0, #0x28]
	LDR      r5, [r0, #0x30]
	ADD      r2, #8
	LDR      r1, [r0, #0x2c]
	LDR      r2, [r2, #4]
	SUB      sp, #0x10
	ADD      r1, r1, r2
	ADD      r3, r3, r5
	STR      r1, [sp, #4]
	ASR      r1, r1, #1
	ASR      r2, r3, #1
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	STR      r3, [sp]
	LDR      r5, [pc, #0x174]
	STR      r2, [sp]
	ADD      r1, r0, #0
	STR      r2, [sp, #8]
	LDR      r0, [r5, #4]
	ADD      r4, sp, #8
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r6, [pc, #0x164]
	ADD      r6, #8
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xc2fc
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r2, r6, #0
	ADD      r2, #8
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xc2fc
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r2, r6, #0
	ADD      r2, #0x10
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xc2fc
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r2, r6, #0
	ADD      r2, #0x18
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xc2fc
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0801C7F6|
	MOV      r2, #0x38
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x413a
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0801C7F6|
	LDR      r4, [pc, #0xfc]
	LDR      r0, [r5]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r0, r4
	LDR      r1, [pc, #0xec]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r5, #0x50
	ADD      r4, r0, #0
	LDRB     r0, [r5, #4]
	ADD      r7, r1, #0
	MOV      r6, #0xb
	CMP      r0, #0
	SUB      sp, #0x34
	BEQ      |sub_0801C8A8|
	CMP      r0, #1
	BNE      |loc_0801C82C|
	LDR      r0, [r4, #0x5c]
	SUB      r0, #1
	STR      r0, [r4, #0x5c]
	BPL      |loc_0801C82C|
	STR      r6, [r4, #0x5c]
|loc_0801C82C|
	LDR      r0, [r4, #0x48]
	ADD      r0, #1
	STR      r0, [r4, #0x48]
	LSL      r0, r0, #0x1c
	LSR      r0, r0, #0x1e
	CMP      r0, #3
	BNE      |loc_0801C83C|
	MOV      r0, #1
|loc_0801C83C|
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0xa4]
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	STR      r0, [r4, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDRB     r1, [r5, #4]
	MOV      r0, #1
	CMP      r1, #0
	BEQ      |loc_0801C8C0|
	CMP      r1, #1
	BNE      |loc_0801C8A4|
	LDR      r0, [r4, #0x58]
	SUB      r0, #1
	STR      r0, [r4, #0x58]
	BPL      |loc_0801C8A4|
	CMP      r7, #0
	BEQ      |loc_0801C89E|
	LDR      r0, [r4, #0x1c]
	CMP      r0, #0
	BEQ      |loc_0801C89E|
	LDR      r0, [r4, #0x1c]
	ADD      r3, sp, #0
	STR      r0, [sp, #0x20]
	LDRB     r0, [r4, #0x10]
	ADD      r6, sp, #4
	MOV      r5, sp
	STRB     r0, [r3, #0x14]
	LDR      r0, [pc, #0x7c]
	STR      r0, [sp, #0x1c]
	LSL      r0, r1, #0xa
	STR      r0, [sp, #0x18]
	ADD      r0, r4, #0
	ADD      r0, #0x28
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r6!, {r0, r1, r2, r3}
	MOV      r0, #2
	ADD      r3, sp, #0
	STRB     r0, [r3]
	LDR      r0, [pc, #0x58]
	STR      r4, [sp, #0x30]
	ADD      r2, r5, #0
	MOV      r1, #0
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x11ab4
|loc_0801C89E|
	ADD      r0, r4, #0
	BL       |sub_0801C750|
|loc_0801C8A4|
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
