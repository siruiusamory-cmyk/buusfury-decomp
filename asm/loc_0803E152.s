	CODE16
|loc_0803E152|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0, #0x10]
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	LSL      r0, r0, #0x1f
	BPL      |loc_0803E18C|
	LDRB     r0, [r4, #0x11]
	LSL      r1, r0, #0x1f
	BPL      |loc_0803E230|
	LSL      r0, r0, #0x1e
	BPL      |loc_0803E232|
	LDMIA    r4!, {r0, r1}
	SUB      r4, #8
	MUL      r1, r5
	ADD      r7, r0, r1
	LDRB     r1, [r4, #0x11]
	LSL      r1, r1, #0x1d
	BPL      |loc_0803E1D0|
	LDR      r1, [r4, #0x20]
	CMP      r1, r7
	BGT      |Math_Divide6|
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	LDR      r3, [r4, #0x18]
	BL       |inc_0x046118_0x049114| + 0x98e
	STR      r7, [r4]
|loc_0803E18C|
	POP      {r3, r4, r5, r6, r7, pc}
