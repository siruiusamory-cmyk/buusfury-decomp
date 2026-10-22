	CODE16
|sub_0800C1D2|
	ADD      r1, r0, #0
	LDRB     r1, [r1, #0x10]
	MOV      r0, #1
	CMP      r1, #0
	BNE      |loc_0800C1DE|
	MOV      r0, #0
|loc_0800C1DE|
	BX       lr
	PUSH     {r4, r5, r6, r7}
	MOV      r6, #3
	LDR      r2, [r1]
	LDR      r7, [pc, #0xa8]
	MOV      r3, #0
	LSL      r6, r6, #0xa
|loc_0800C1EC|
	LSL      r4, r3, #0x1c
	LSR      r4, r4, #7
	ORR      r4, r7
	LSR      r4, r4, #8
	LSL      r4, r4, #8
	ADD      r4, #0x88
	STR      r4, [r2]
	LDRH     r4, [r0, #0xc]
	LSL      r5, r3, #4
	ADD      r3, #1
	ADD      r4, r4, r5
	LDR      r5, [r2, #4]
	LSL      r4, r4, #0x16
	LSR      r5, r5, #0xa
	LSL      r5, r5, #0xa
	LSR      r4, r4, #0x16
	ORR      r4, r5
	STR      r4, [r2, #4]
|loc_0800C210|
	LDRB     r5, [r0, #8]
	BIC      r4, r6
	LSL      r5, r5, #0x1a
	LSR      r5, r5, #0x1e
	LSL      r5, r5, #0xa
	ORR      r4, r5
	STR      r4, [r2, #4]
	ADD      r2, #8
	CMP      r3, #7
	BLT      |loc_0800C1EC|
	LDR      r3, [pc, #0x6c]
	STR      r3, [r2]
	LDRH     r3, [r0, #0xc]
	LDR      r4, [r2, #4]
	ADD      r3, #0x70
	LSL      r3, r3, #0x16
	LSR      r4, r4, #0xa
	LSL      r4, r4, #0xa
	LSR      r3, r3, #0x16
	ORR      r3, r4
	STR      r3, [r2, #4]
	LDRB     r0, [r0, #8]
	BIC      r3, r6
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	ORR      r0, r3
	STR      r0, [r2, #4]
	ADD      r0, r2, #0
	ADD      r0, #0x10
	STR      r0, [r1]
	POP      {r4, r5, r6, r7}
	MOV      r0, #0
	BX       lr
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BEQ      |sub_0800C268|
	CMP      r1, #0x17
	BNE      |loc_0800C270|
	MOV      r1, #2
	STRB     r1, [r0, #0x10]
	STR      r2, [r0, #0x18]
	MOV      r0, #1
	POP      {r3, pc}
