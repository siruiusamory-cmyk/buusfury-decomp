	CODE16
|sub_0800795C|
	BL       |loc_08009744|
	LDR      r0, [r4, #0xc]
	SUB      r0, #1
	STR      r0, [r4, #0xc]
	BNE      |loc_0800796E|
	LDR      r0, [r5]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4cc4
|loc_0800796E|
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
	LSL      r0, r0, #0
	ADD      r3, sp, #0x90
	LSR      r4, r0, #0x20
	LSL      r4, r5, #0x1f
	LSR      r7, r0, #0x20
