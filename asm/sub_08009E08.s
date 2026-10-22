	CODE16
|sub_08009E08|
	MOV      r0, #0
	STR      r0, [r5]
	STR      r0, [r6]
	MOV      r0, #1
	STRH     r0, [r4, #0x10]
	ADD      r0, r4, #0
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4}
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDR      r3, [r1]
	LDR      r4, [r0, #4]
	ADD      r3, r3, r4
	STR      r3, [r1]
	LDR      r3, [r1, #4]
	LDR      r2, [r0, #8]
	ADD      r2, r3, r2
	STR      r2, [r1, #4]
	LDRH     r2, [r0, #0x10]
	SUB      r2, #1
	LSL      r2, r2, #0x10
	LSR      r2, r2, #0x10
	STRH     r2, [r0, #0x10]
	BNE      |sub_08009E50|
	MOV      r3, #0xc
	LDRSH    r2, [r0, r3]
	MOV      r3, #0xe
	LDRSH    r0, [r0, r3]
	LSL      r2, r2, #8
	STMIA    r1!, {r2}
	LSL      r0, r0, #8
	STR      r0, [r1]
	MOV      r0, #1
	POP      {r4}
	BX       lr
