	CODE16
|sub_08026E6A|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x10]
	CMP      r1, #0
	BEQ      |loc_08026EA2|
	LDR      r1, [r0, #0x14]
	ADD      r1, #1
	STR      r1, [r0, #0x14]
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x1d
	CMP      r1, #4
	BLT      |loc_08026E84|
	MOV      r2, #7
	SUB      r1, r2, r1
|loc_08026E84|
	LDR      r2, [r0, #0x18]
	CMP      r2, r1
	BEQ      |loc_08026EA2|
	STR      r1, [r0, #0x18]
	LDRH     r0, [r0, #0xc]
	LDR      r2, [pc, #0xf4]
	LSL      r1, r1, #6
	LSL      r0, r0, #5
	ADD      r0, r0, r2
	LDR      r2, [pc, #0xe4]
	ADD      r2, #4
	ADD      r1, r1, r2
	MOV      r2, #0x40
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08026EA2|
	POP      {r3, pc}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	MOV      r2, #1
	LSL      r2, r2, #0xd
	STR      r2, [r1]
|loc_08026EB4|
	LDR      r3, [r0, #0x1c]
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x20]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRH     r0, [r0, #0xc]
	LDR      r2, [r1, #4]
	LSR      r2, r2, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r2, r2, #0xa
	ORR      r0, r2
	MOV      r2, #3
	LSL      r2, r2, #0xa
	ORR      r0, r2
	STR      r0, [r1, #4]
	MOV      r0, #0
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #8
	BNE      |sub_08026F04|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08026F04|
	ADD      r0, r4, #0
	ADD      sp, #8
	POP      {r4, r5, r6, pc}
