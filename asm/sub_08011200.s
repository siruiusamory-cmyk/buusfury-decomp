	CODE16
|sub_08011200|
	LSL      r2, r1, #2
	ADD      r2, r2, r1
	LDR      r3, [pc, #0x34c]
	LSL      r2, r2, #1
	ADD      r2, r2, r0
	PUSH     {r4, r5}
	ADD      r2, r2, r3
	SUB      r5, r3, #4
	LSL      r3, r1, #2
	ADD      r1, r3, r1
	LSL      r1, r1, #1
	ADD      r1, r1, r0
	ADD      r3, r5, #4
	LDRB     r4, [r2, #9]
	ADD      r1, r1, r3
	LDRB     r1, [r1, #8]
	CMP      r4, #0xff
	BNE      |loc_08011228|
	STRB     r1, [r0]
	B        |loc_08011234|
|loc_08011228|
	LSL      r3, r4, #2
	ADD      r3, r3, r4
	LSL      r3, r3, #1
	ADD      r3, r3, r0
	ADD      r3, r3, r5
	STRB     r1, [r3, #0xc]
|loc_08011234|
	LDRB     r1, [r2, #8]
	CMP      r1, #0xff
	BEQ      |loc_08011248|
	LSL      r3, r1, #2
	ADD      r1, r3, r1
	LSL      r1, r1, #1
	LDRB     r2, [r2, #9]
	ADD      r0, r1, r0
	ADD      r0, r0, r5
	STRB     r2, [r0, #0xd]
|loc_08011248|
	POP      {r4, r5}
	BX       lr
