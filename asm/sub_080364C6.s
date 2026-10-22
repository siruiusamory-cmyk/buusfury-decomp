	CODE16
|sub_080364C6|
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x44
	MOV      r7, sp
	MOV      r2, #0x10
	ADD      r7, r7, r2
	ADD      r5, r0, #0
	MOV      r1, #0xf0
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r0, [pc, #0x23c]
	LDR      r1, [sp, #0x34]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [pc, #0x228]
	ADD      r3, sp, #0
	LDR      r0, [r0, #0x10]
	LDR      r1, [pc, #0x230]
	STR      r0, [sp, #0x1c]
	MOV      r0, #0x78
	STR      r0, [sp, #0x14]
	MOV      r0, #0xb
	STR      r0, [sp, #0x18]
	MOV      r0, #2
	STRB     r0, [r3, #0x13]
	MOV      r0, #1
	STRB     r0, [r3, #0x12]
	STR      r1, [sp, #0x30]
	STRB     r0, [r3, #0x10]
	MOV      r0, #0x98
	LDR      r0, [r0, r5]
	LDR      r1, [pc, #0x218]
	LSL      r0, r0, #2
	LDR      r1, [r1, r0]
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	LDR      r0, [pc, #0x1f8]
	MOV      r6, sp
	ADD      r0, #0x54
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r6!, {r0, r1, r2, r3}
	SUB      r6, #0x10
|loc_0803651C|
	MOV      r4, #0
|loc_0803651E|
	LDRH     r0, [r5, #0xc]
	LDR      r1, [pc, #0x1f0]
	ADD      r2, r6, #0
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSL      r1, r4, #9
	ADD      r1, r0, r1
	ADD      r1, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x3c
	LDR      r0, [sp]
	ADD      r4, #1
	ADD      r0, #0x20
	STR      r0, [sp]
	LDR      r0, [sp, #8]
	ADD      r0, #0x20
	STR      r0, [sp, #8]
	CMP      r4, #7
	BLT      |loc_0803651E|
	MOV      r0, #0xf0
	STR      r0, [sp, #8]
	LDRH     r0, [r5, #0xc]
	LDR      r1, [pc, #0x1c4]
	ADD      r2, r6, #0
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	MOV      r1, #0x39
	LSL      r1, r1, #6
	ADD      r1, r0, r1
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x3c
	MOV      r1, #0
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
