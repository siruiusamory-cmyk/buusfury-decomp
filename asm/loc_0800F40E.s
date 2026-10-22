	CODE16
|loc_0800F40E|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	MOV      r5, #0
	CMP      r1, #0xa
	LDR      r0, [pc, #0xa0]
	BEQ      |loc_0800F45C|
	BGT      |sub_0800F442|
	CMP      r1, #5
	BEQ      |loc_0800F49E|
	CMP      r1, #6
	BNE      |loc_0800F4AC|
	LDR      r0, [r4, #0x58]
	LDR      r1, [r2]
	CMP      r0, r1
	BNE      |loc_0800F43E|
	LDR      r0, [r2, #4]
	ADD      r1, r2, #4
	CMP      r0, #0x10
	BEQ      |loc_0800F43E|
	ADD      r2, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	STR      r2, [r1]
	STR      r4, [r0, #4]
|loc_0800F43E|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
