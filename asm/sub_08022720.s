	CODE16
|sub_08022720|
	MOV      r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x11
	ADD      r3, sp, #0
	LDRH     r2, [r3, #4]
	LDRB     r1, [r6, #4]
	LSL      r0, r0, #0x1f
	LSR      r2, r2, #3
	LSL      r1, r1, #0x1d
	LSR      r1, r1, #0x1d
	LSL      r2, r2, #3
	ORR      r1, r2
	STRH     r1, [r3, #4]
	LDRH     r2, [r3, #4]
	MOV      r3, #0xff
	LDR      r1, [r4, #0x18]
	LSL      r3, r3, #3
	BIC      r2, r3
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x15
	ORR      r1, r2
	MOV      r2, #1
	ADD      r3, sp, #0
	STRH     r1, [r3, #4]
	LSL      r2, r2, #0xb
	BIC      r1, r2
	LSR      r0, r0, #0x14
	ORR      r0, r1
	STRH     r0, [r3, #4]
	STRH     r0, [r3, #8]
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x10]
	STR      r0, [r1]
	LDR      r0, [r4, #0x18]
	ADD      r0, #1
	STR      r0, [r4, #0x18]
	LDR      r0, [r4, #0x1c]
	LDR      r1, [r4, #0x20]
	CMP      r0, r1
	BNE      |loc_08022776|
	MOV      r0, #0
	STR      r0, [r4, #0x1c]
	STR      r0, [r4, #0x18]
|loc_08022776|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0x1c
	STR      r0, [sp, #8]
	ADD      r3, sp, #0
	LDRH     r0, [r3, #8]
	ADD      r1, r6, #0
	ADD      r1, #0xff
	STRH     r0, [r3, #0xc]
	ADD      r2, r6, #0
	ADD      r2, #0xff
	ADD      r1, #0x21
	STR      r1, [sp, #0x18]
	ADD      r2, #5
	LDRB     r1, [r1, #8]
	STR      r2, [sp, #0x14]
	SUB      r7, r2, #4
	SUB      r2, #0x80
	LSL      r0, r0, #0x1d
	LSR      r0, r0, #0x1d
	CMP      r0, r1
	STR      r2, [sp, #0x10]
	BEQ      |loc_080227D0|
	MOV      r2, #0x80
	MOV      r1, #0
	MVN      r1, r1
	LDR      r0, [sp, #0x10]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	LDR      r0, [sp, #0x14]
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0x13c]
	ADD      r3, sp, #0
	STR      r0, [r7, #0x24]
	LDRH     r0, [r3, #0xc]
	LDR      r1, [sp, #0x18]
	LSL      r0, r0, #0x1d
	LSR      r0, r0, #0x1d
	STRB     r0, [r1, #8]
|loc_080227D0|
	LDR      r5, [pc, #0x128]
	LDR      r0, [r5]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r3, sp, #0
	LDRH     r1, [r3, #0xc]
	SUB      r0, #2
	LSL      r1, r1, #0x15
	LSR      r1, r1, #0x18
	MUL      r0, r1
	ADD      r4, r0, #0
	LDR      r0, [r5]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r0, r0, r4
	CMP      r0, #0x80
	BLT      |sub_08022820|
	MOV      r2, #0x80
	MOV      r1, #0
	MVN      r1, r1
	LDR      r0, [sp, #0x10]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	LDR      r0, [sp, #0x14]
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0xe4]
	STR      r0, [r7, #0x24]
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
