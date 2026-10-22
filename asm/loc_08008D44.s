	CODE16
|loc_08008D44|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r3, #0
	MOV      r3, #0
	ADD      r4, r0, #0
	LDRSH    r0, [r5, r3]
	SUB      sp, #0x14
	LDR      r7, [sp, #0x28]
	SUB      r0, #0x70
	STR      r0, [sp, #8]
	LDR      r6, [sp, #0x2c]
	MOV      r3, #2
	LDRSH    r0, [r5, r3]
	SUB      r0, #0x4c
	STR      r0, [sp, #0xc]
	LSL      r0, r1, #0x18
	LSR      r0, r0, #0x18
	LSL      r1, r2, #0x18
	LSR      r1, r1, #0x18
	STRB     r0, [r4]
	STRB     r1, [r4, #1]
	BL       |sub_080089FC|
	ADD      r1, r0, #0
	ADD      r3, r7, #0
	ADD      r0, r4, #0
	STR      r6, [sp]
	ADD      r2, sp, #8
	BL       |loc_08008B30|
	LDR      r0, [r4, #0x10]
	LDR      r7, [pc, #0x294]
	ADD      r0, #1
	STR      r0, [r4, #0x10]
	LDR      r0, [r7, #8]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x280]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	LDR      r1, [r7, #0xc]
	ADD      r1, #0x80
	STR      r1, [sp, #0x10]
	LDR      r1, [r1, #0x10]
	CMP      r1, #0
	BEQ      |sub_08008DE6|
	ADD      r2, r5, #0
	ADD      r1, r0, #0
	MOV      r0, #0
	BL       |sub_080104F2|
	ADD      r5, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08008DD4|
	LDR      r1, [pc, #0x254]
	STMIA    r0!, {r1, r5}
	SUB      r0, #8
	MOV      r1, #0
	MVN      r1, r1
	STR      r1, [r0, #8]
|loc_08008DD4|
	ADD      r1, r0, #0
	LDR      r0, [r7, #0x20]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4ca2
	ADD      r1, r5, #0
	LDR      r0, [r7, #0x14]
	BL       |List_Append|
	B        |sub_08008E2C|
