	CODE16
|sub_080430E8|
	CMP      r3, #3
	BNE      |loc_080430E0|
	MOV      r0, #0
	STRB     r0, [r4, #6]
	MOV      r0, #0x28
	STRH     r0, [r4, #0x1a]
	MOV      r0, #4
	STRB     r0, [r4, #7]
	MOV      r0, #9
	STRB     r0, [r4, #4]
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r4, [pc, #0x250]
	MOV      r5, #0
	LDR      r1, [r4, #0x40]
	CMP      r1, #0
	BNE      |sub_08043114|
	LDRB     r1, [r4, #4]
	CMP      r1, #0
	BEQ      |sub_08043114|
	STRB     r5, [r4, #4]
	POP      {r3, r4, r5, r6, r7, pc}
