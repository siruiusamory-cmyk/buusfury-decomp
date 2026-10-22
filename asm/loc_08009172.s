	CODE16
|loc_08009172|
	PUSH     {r4, lr}
	LDR      r0, [r0, #4]
	LSL      r1, r1, #3
	LDR      r0, [r0, #0x10]
	ADD      r0, r0, r1
	LDR      r1, [pc, #0x7c]
	LDR      r0, [r0, #4]
	LDR      r4, [r1, #0x10]
	LDR      r1, [r0]
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r4]
	ADD      r2, r1, #1
	LSL      r1, r1, #2
	ADD      r1, r1, r4
	STR      r2, [r4]
	STR      r0, [r1, #4]
	POP      {r4, pc}
