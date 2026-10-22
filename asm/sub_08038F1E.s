	CODE16
|sub_08038F1E|
	LSL      r0, r0, #0
	ASR      r4, r1, #4
	LSR      r7, r6, #1
	STRH     r0, [r3, #8]
	LSR      r3, r5, #1
	MOV      r6, #0x8c
	LSR      r7, r0, #0x20
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x160]
	ADD      r5, r1, #0
	LDR      r0, [r7]
	SUB      sp, #0x34
	CMP      r0, #0
	BNE      |sub_08038F3E|
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
