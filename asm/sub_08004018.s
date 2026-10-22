	CODE16
|sub_08004018|
	ASR      r3, r2, #1
	LDR      r2, [r0]
	ADD      r4, r2, #1
	LSL      r2, r2, #2
	ADD      r2, r2, r0
	STR      r4, [r0]
	STR      r3, [r2, #4]
	SUB      r5, #1
	BNE      |loc_08003FF8|
	POP      {r4, r5}
	BX       lr
	LSL      r0, r0, #0
	STR      r0, [r3, r2]
	LSR      r5, r0, #0x20
	STRB     r0, [r7, r1]
	LSR      r5, r0, #0x20
