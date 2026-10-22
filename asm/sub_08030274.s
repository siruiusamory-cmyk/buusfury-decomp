	CODE16
|sub_08030274|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x20]
	ADD      r5, r1, #0
	LDR      r1, [r4, #0x18]
	SUB      sp, #0x1fc
	SUB      sp, #0x108
	CMP      r0, r1
	BEQ      |loc_080302CC|
	LDR      r1, [pc, #0xe8]
	MOV      r2, #3
	LSL      r2, r2, #8
	ADD      r6, sp, #4
	STR      r0, [r4, #0x18]
	ADD      r1, #0x84
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [r4, #0x20]
	CMP      r0, #0x55
	BGE      |loc_080302BC|
	LDR      r7, [pc, #0xdc]
	MOV      r1, #1
|loc_080302A2|
	LSL      r2, r0, #3
	LDRH     r3, [r7, r2]
	ADD      r2, r2, r7
	ADD      r0, #1
	STRB     r1, [r6, r3]
	LDRH     r3, [r2, #2]
	CMP      r0, #0x55
	STRB     r1, [r6, r3]
	LDRH     r3, [r2, #4]
	STRB     r1, [r6, r3]
	LDRH     r2, [r2, #6]
	STRB     r1, [r6, r2]
	BLT      |loc_080302A2|
|loc_080302BC|
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0xb8]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSR      r2, r1, #0x11
	ADD      r1, r6, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080302CC|
	LDR      r0, [r5]
	LDR      r1, [r4, #0x1c]
	MOV      r2, #1
	MOV      r6, #3
	LSL      r6, r6, #0xa
	LSL      r2, r2, #0xa
	ADD      r3, r1, #1
	BEQ      |loc_0803031C|
	MOV      r7, #5
	LSL      r7, r7, #0xd
	STR      r7, [r0]
	LDR      r1, [r4, #0x10]
	LDR      r3, [r4, #0x1c]
	ADD      r1, r1, r3
	ADD      r1, #1
	LSL      r1, r1, #0x17
	LSR      r1, r1, #7
	ORR      r1, r7
	STR      r1, [r0]
	LDR      r3, [r4, #0x14]
	LSR      r1, r1, #8
	ADD      r3, #0xfd
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r1, r1, #8
	ORR      r1, r3
	STR      r1, [r0]
	LDR      r1, [r0, #4]
	BIC      r1, r6
	ADD      r1, r1, r2
	STR      r1, [r0, #4]
	LDRH     r3, [r4, #0xc]
	LSR      r1, r1, #0xa
	LSL      r1, r1, #0xa
	ADD      r3, #0x18
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	ORR      r1, r3
	STR      r1, [r0, #4]
	ADD      r0, #8
|loc_0803031C|
	MOV      r1, #0
|loc_0803031E|
	LDR      r7, [pc, #0x60]
	LSL      r3, r1, #5
	STR      r7, [r0]
	LDR      r2, [r4, #0x10]
	ADD      r2, r2, r3
	LSL      r2, r2, #0x17
	LSR      r2, r2, #7
	ORR      r2, r7
	STR      r2, [r0]
	LDR      r3, [r4, #0x14]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r0]
	LDR      r2, [r0, #4]
	LSR      r3, r7, #0x14
	BIC      r2, r6
	ADD      r2, r2, r3
	STR      r2, [r0, #4]
	LDRH     r3, [r4, #0xc]
	LSL      r7, r1, #3
	LSR      r2, r2, #0xa
	ADD      r3, r3, r7
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	LSL      r2, r2, #0xa
	ORR      r2, r3
	STR      r2, [r0, #4]
	ADD      r0, #8
	ADD      r1, #1
	CMP      r1, #3
	BLT      |loc_0803031E|
	STR      r0, [r5]
	ADD      sp, #0x1fc
	ADD      sp, #0x108
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	LDRB     r4, [r4, #0xd]
	LSR      r5, r6, #1
	STMIA    r0!, {r5}
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	LDRB     r0, [r5, #0x1b]
	LSR      r5, r6, #1
	STR      r0, [r0]
	AND      r0, r0
	PUSH     {r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0xc
	BNE      |sub_080303A0|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080303A0|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, pc}
