	CODE16
|List_Append|
	ADD      r0, #4
	ADD      r2, r1, #0
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r0, #4
	ADD      r5, r0, #0
	BL       |inc_0x049120_0x055620| + 0x6d34
	LDR      r1, [r4, #4]
	LSL      r1, r1, #2
	ADD      r0, r1, r5
	LDR      r1, [pc, #0x158]
	STR      r1, [r0, #4]
	POP      {r3, r4, r5, pc}
