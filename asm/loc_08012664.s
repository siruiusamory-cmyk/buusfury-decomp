	CODE16
|loc_08012664|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r0, #0
	SUB      r4, r1, #1
	BMI      |loc_08012688|
|loc_0801266E|
	LSL      r0, r4, #2
	LDR      r0, [r6, r0]
	LDR      r1, [r0]
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r5]
	ADD      r2, r1, #1
	LSL      r1, r1, #2
	ADD      r1, r1, r5
	STR      r2, [r5]
	STR      r0, [r1, #4]
	SUB      r4, #1
	BPL      |loc_0801266E|
|loc_08012688|
	POP      {r4, r5, r6, pc}
