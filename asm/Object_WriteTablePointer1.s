	CODE16
|Object_WriteTablePointer1|
	LSL      r3, r1, #3
	SUB      r1, r3, r1
	LDR      r2, [pc, #0x2c8]
	LSL      r1, r1, #2
	ADD      r1, r1, r2
	MOV      r2, #1
	LSL      r2, r2, #9
	ADD      r0, r0, r2
	STR      r1, [r0, #0x24]
	BX       lr
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	MOV      r0, #0xa3
	LSL      r0, r0, #2
	ADD      r5, r4, r0
	LDR      r0, [r5]
	MOV      r7, #0
	ADD      r6, r1, #0
	CMP      r0, #0
	BNE      |sub_0800FA42|
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
