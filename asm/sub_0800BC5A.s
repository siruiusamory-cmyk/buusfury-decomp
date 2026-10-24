	CODE16
|sub_0800BC5A|
	LSR      r4, r0, #0x20
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r0, [r0]
	STRH     r0, [r1]
	MOV      r0, #0
	AND      r0, r5
	STR      r0, [r0]
	STRH     r0, [r7]
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	ADD      r7, #0xd8
	LSR      r1, r6, #1
	SUB      r0, r0, #5
	LSR      r7, r0, #0x20
	SUB      r7, #0xd8
	LSR      r1, r6, #1
	SUB      r2, #0xd8
	LSR      r1, r6, #1
	MOV      r1, #0xd0
	LSR      r7, r0, #0x20
	BLT      |loc_0800BC34|
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	LDRB     r0, [r3, #5]
	LDR      r1, [pc, #0x1d8]
	LDRSB    r0, [r1, r0]
	CMP      r0, #0
	BEQ      |loc_0800BCAE|
	LDR      r1, [pc, #0x1d4]
	MOV      r2, #1
|loc_0800BCA2|
	SUB      r0, #1
	LSL      r3, r0, #2
	LDR      r3, [r1, r3]
	CMP      r0, #0
	STRB     r2, [r5, r3]
	BNE      |loc_0800BCA2|
|loc_0800BCAE|
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x1c4]
	MOV      r2, #5
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSL      r2, r2, #8
	ADD      r1, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      sp, #0x1fc
	ADD      sp, #0x1fc
	ADD      sp, #0x114
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x1a4]
	ADD      r5, r0, #0
	SUB      r6, #0x18
	LDR      r0, [r6, #0xc]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	SUB      sp, #4
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDR      r1, [r5, #0x18]
	CMP      r1, #0
	BNE      |loc_0800BD3C|
	ADD      r0, #0x2c
	LDRH     r0, [r0]
	CMP      r0, #0
	BEQ      |loc_0800BD3C|
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_0800BD32|
	LDR      r0, [pc, #0x180]
	MOV      r7, #0xff
	ADD      r7, #1
	STR      r0, [r4]
	STRH     r7, [r4, #0xe]
	LDR      r0, [r6, #8]
	ADD      r1, r7, #0
	BL       |loc_0801124C|
	ADD      r3, r0, #1
	BNE      |loc_0800BD20|
	ADD      r1, r7, #0
	LDR      r0, [r6, #8]
	BL       |sub_08011732|
	ADD      r1, r7, #0
	LDR      r0, [r6, #8]
	BL       |loc_0801124C|
|loc_0800BD20|
	STRH     r0, [r4, #0xc]
	LDR      r0, [pc, #0x15c]
	STR      r0, [r4]
	MOV      r0, #0
	MVN      r0, r0
	STR      r0, [r4, #0x10]
	MOV      r0, #0
	STR      r0, [r4, #0x14]
	STR      r5, [r4, #0x18]
|loc_0800BD32|
	STR      r4, [r5, #0x18]
	LDR      r0, [r6, #8]
	ADD      r1, r4, #0
	BL       |List_Append|
|loc_0800BD3C|
	LDR      r0, [r6, #0xc]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r2, r0, r1
	LDR      r1, [sp, #8]
	ADD      r0, r5, #0
	BL       |Gfx_BuildVitalBars|
	MOV      r0, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BEQ      |loc_0800BD7A|
	CMP      r1, #0xc
	BEQ      |sub_0800BD72|
	CMP      r1, #0x15
	BNE      |loc_0800BD82|
	MOV      r1, #0
	MVN      r1, r1
	STR      r1, [r0, #0x14]
	MOV      r0, #1
	POP      {r3, pc}
