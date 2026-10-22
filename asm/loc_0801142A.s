	CODE16
|loc_0801142A|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ASR      r0, r1, #1
	MOV      r1, #3
	LSL      r1, r1, #0xa
	ADD      r0, r4, r0
	ADD      r0, r0, r1
	LDRB     r6, [r0]
	LSL      r0, r6, #2
	ADD      r0, r0, r6
	LSL      r0, r0, #1
	ADD      r1, r0, r4
	LDR      r0, [pc, #0x110]
	ADD      r5, r1, r0
	MOV      r1, #0
	STRB     r1, [r5]
	LDRB     r1, [r5, #6]
	CMP      r1, #0xff
	BEQ      |loc_08011514|
	LSL      r2, r1, #2
	ADD      r2, r2, r1
	LSL      r2, r2, #1
	ADD      r2, r2, r4
	ADD      r2, r2, r0
	STR      r2, [sp]
	LDRB     r2, [r5, #7]
	CMP      r2, #0xff
	BEQ      |loc_080114F6|
	LSL      r3, r2, #2
	ADD      r2, r3, r2
	LSL      r2, r2, #1
	ADD      r2, r2, r4
	ADD      r7, r2, r0
	LDR      r2, [sp]
	LDRB     r0, [r2]
	CMP      r0, #0
	LDRB     r0, [r7]
	BNE      |loc_080114CC|
	CMP      r0, #0
	BNE      |sub_080114C0|
	ADD      r0, r4, #0
	BL       |sub_08011200|
	LDRH     r0, [r5, #4]
	LDR      r2, [sp]
	LDRH     r1, [r2, #4]
	ADD      r0, r0, r1
	LDRH     r1, [r7, #4]
	ADD      r0, r0, r1
	STRH     r0, [r7, #4]
	LDR      r2, [sp]
	LDRB     r0, [r2, #6]
	STRB     r0, [r7, #6]
	LDR      r2, [sp]
	LDRB     r1, [r2, #6]
	CMP      r1, #0xff
	BEQ      |loc_080114AE|
	LSL      r3, r1, #2
	ADD      r1, r3, r1
	LSL      r1, r1, #1
	LDRB     r0, [r5, #7]
	MOV      r2, #0x69
	LSL      r2, r2, #4
	ADD      r1, r1, r4
	ADD      r1, r1, r2
	STRB     r0, [r1, #0xb]
|loc_080114AE|
	LDRB     r1, [r5, #6]
	ADD      r0, r4, #0
	BL       |loc_0801137C|
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |loc_0801137C|
	POP      {r3, r4, r5, r6, r7, pc}
