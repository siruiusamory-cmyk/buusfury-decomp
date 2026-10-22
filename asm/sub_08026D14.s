	CODE16
|sub_08026D14|
	PUSH     {r4, r5}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	SUB      sp, #0x10
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	LDR      r2, [r0, #0x10]
	LDR      r4, [pc, #0xa8]
	LDR      r3, [r0, #0x1c]
	ADD      r2, r2, r4
	LDR      r4, [r3]
	LDR      r5, [r2]
	LDR      r3, [r3, #4]
	LDR      r2, [r2, #4]
	SUB      r4, r4, r5
	SUB      r2, r3, r2
	STR      r2, [sp, #4]
	LDR      r3, [sp, #4]
	STR      r4, [sp]
	STR      r3, [sp, #0xc]
	STR      r4, [sp, #8]
	LDR      r2, [r0, #0x1c]
	ADD      r3, r4, #0
	LDR      r4, [pc, #0x8c]
	LDR      r2, [r2, #0x10]
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	AND      r2, r4
	ORR      r3, r2
	LDR      r2, [sp, #0xc]
	LSR      r3, r3, #8
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x18
	LSL      r3, r3, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRH     r0, [r0, #0x14]
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
	ADD      sp, #0x10
	POP      {r4, r5}
	MOV      r0, #0
	BX       lr
	CMP      r1, #4
	BNE      |sub_08026D96|
	LDRH     r3, [r0, #0xc]
	ASR      r1, r2, #1
	CMP      r1, r3
	BNE      |sub_08026D92|
	LSL      r1, r2, #0x1f
	LSR      r1, r1, #0x1f
	STR      r1, [r0, #0x18]
	MOV      r0, #1
	BX       lr
