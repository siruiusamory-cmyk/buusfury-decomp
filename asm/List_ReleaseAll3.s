	CODE16
|List_ReleaseAll3|
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [r0]
	ADD      r5, r0, #0
	SUB      r4, #1
	BMI      |loc_0801264C|
|loc_08012632|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #4]
	CMP      r0, #0
	BEQ      |loc_08012648|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08012648|
	SUB      r4, #1
	BPL      |loc_08012632|
|loc_0801264C|
	MOV      r1, #0
	ADD      r2, r5, #0
	ADD      r2, #0xc0
	STR      r1, [r5]
	MOV      r0, #1
	STR      r0, [r2, #0x10]
	STR      r0, [r2, #4]
	STR      r1, [r2, #0xc]
	LDR      r0, [r2, #8]
	ADD      r0, #1
	STR      r0, [r2, #8]
	POP      {r3, r4, r5, pc}
