	CODE16
|sub_0800B55C|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	ADD      r5, r1, #0
	ADD      r0, #1
	STR      r0, [r4, #0x14]
	LSL      r0, r0, #0x1b
	LSR      r1, r0, #0x1e
	LDR      r0, [r4, #0x10]
	CMP      r0, r1
	BEQ      |loc_0800B58A|
	STR      r1, [r4, #0x10]
	LDRH     r0, [r4, #0xc]
	LDR      r2, [pc, #0x284]
	LSL      r1, r1, #8
	LSL      r0, r0, #5
	ADD      r0, r0, r2
	LDR      r2, [pc, #0x280]
	ADD      r1, r1, r2
	MOV      r2, #0xff
	ADD      r2, #1
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0800B58A|
	LDR      r0, [r5]
	ADD      r1, r0, #0
	ADD      r1, #8
	STR      r1, [r5]
	LDR      r1, [pc, #0x270]
	STR      r1, [r0]
	LDR      r2, [r4, #0x18]
	LDR      r2, [r2, #0x28]
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x18
	ORR      r1, r2
	STR      r1, [r0]
	LDRH     r1, [r4, #0xc]
	LDR      r2, [r0, #4]
	LSR      r2, r2, #0xa
	LSL      r1, r1, #0x16
	LSR      r1, r1, #0x16
	LSL      r2, r2, #0xa
	ORR      r1, r2
	MOV      r2, #3
	LSL      r2, r2, #0xa
	BIC      r1, r2
	MOV      r2, #1
	LSL      r2, r2, #0xa
	ADD      r1, r1, r2
	STR      r1, [r0, #4]
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
	CMP      r1, #3
	BLT      |sub_0800B5CA|
	MOV      r0, #2
	BX       lr
