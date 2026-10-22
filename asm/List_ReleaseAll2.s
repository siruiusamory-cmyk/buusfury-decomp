	CODE16
|List_ReleaseAll2|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x288]
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x2de
	MOV      r0, #0x41
	LSL      r0, r0, #3
	ADD      r5, r4, r0
	LDR      r4, [r5]
	SUB      r4, #1
	BMI      |loc_080115AA|
|loc_08011596|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	SUB      r4, #1
	BPL      |loc_08011596|
|loc_080115AA|
	MOV      r0, #0
	STR      r0, [r5]
	POP      {r3, r4, r5, pc}
