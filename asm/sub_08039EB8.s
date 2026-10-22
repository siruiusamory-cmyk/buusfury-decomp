	CODE16
|sub_08039EB8|
	PUSH     {r4, r5}
	ADD      r2, r1, #0
	LDR      r3, [r0, #0x18]
	ADD      r2, #0xff
	ADD      r1, #0xff
	SUB      r3, #1
	ADD      r1, #0xa1
	ADD      r2, #0xa9
	CMP      r3, #0
	STR      r3, [r0, #0x18]
	BNE      |sub_08039EEC|
	MOV      r3, #4
	LDRSH    r4, [r0, r3]
	MOV      r3, #6
	LDRSH    r5, [r0, r3]
	LSL      r4, r4, #8
	STMIA    r1!, {r4}
	LSL      r3, r5, #8
	STR      r3, [r1]
	MOV      r3, #8
	LDRSH    r0, [r0, r3]
	LSL      r0, r0, #0xa
	STR      r0, [r2]
	MOV      r0, #1
	POP      {r4, r5}
	BX       lr
