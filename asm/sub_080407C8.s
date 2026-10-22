	CODE16
|sub_080407C8|
	STRH     r0, [r7, r3]
	LSL      r0, r0, #0xc
	LDRB     r4, [r7, #5]
	LSR      r3, r7, #1
	LDR      r1, [pc, #0xc]
	LDR      r0, [pc, #0x10]
	STR      r0, [r1]
	MOV      r2, #1
|loc_080407D8|
	ADD      r0, r2, #0
	POP      {r1}
	BX       r1
	LSL      r0, r0, #0
	STRH     r0, [r7, r3]
	LSL      r0, r0, #0xc
	LDRB     r0, [r6, #5]
	LSR      r3, r7, #1
