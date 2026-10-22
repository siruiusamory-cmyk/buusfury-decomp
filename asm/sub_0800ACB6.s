	CODE16
|sub_0800ACB6|
	PUSH     {r4, r5}
	LDR      r3, [r1]
	LDR      r2, [pc, #0xc0]
	ADD      r4, r3, #0
	ADD      r4, #8
	LDR      r2, [r2, #0xc]
	STR      r4, [r1]
	LDR      r4, [pc, #0xd4]
	ADD      r2, #0x28
	STR      r4, [r3]
	LDR      r1, [r0, #0x20]
	LDR      r5, [r2]
	ASR      r1, r1, #3
	SUB      r1, r1, r5
	LSL      r1, r1, #0x17
	LSR      r1, r1, #7
	ORR      r1, r4
	STR      r1, [r3]
	LDR      r4, [r0, #0x24]
	LDR      r2, [r2, #4]
	ASR      r4, r4, #3
	SUB      r2, r4, r2
	LSL      r2, r2, #0x18
	LSR      r1, r1, #8
	LSL      r1, r1, #8
	LSR      r2, r2, #0x18
	ORR      r1, r2
	STR      r1, [r3]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r3, #4]
	LSR      r1, r1, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r1, r1, #0xa
	ORR      r0, r1
	MOV      r1, #3
	LSL      r1, r1, #0xa
	BIC      r0, r1
	MOV      r1, #1
	LSL      r1, r1, #0xa
	ADD      r0, r0, r1
	STR      r0, [r3, #4]
	POP      {r4, r5}
	MOV      r0, #0
	BX       lr
|sub_0800AD10|
|unk_0800AD10|
		MOV r0, #1
		BX       lr
