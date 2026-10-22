	CODE16
|loc_08004038|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x11c]
	ADD      r4, r0, #0
	LDR      r0, [r3]
	ADD      r1, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r3
	STR      r1, [r3]
	STR      r4, [r0, #4]
	CMP      r2, #0
	BNE      |loc_08004052|
	ADD      r2, r4, #0
	ADD      r2, #0x5c
|loc_08004052|
	LDR      r5, [pc, #0x104]
	STR      r2, [r4, #0x58]
	SUB      r5, #4
	STR      r2, [r5]
	MOV      r0, #0
	STR      r0, [r4]
	LDR      r7, [pc, #0xfc]
	STR      r0, [r4, #0x44]
	ADD      r6, sp, #4
	LDR      r1, [sp, #4]
	LDRB     r0, [r1]
	ADD      r1, #1
	STR      r1, [sp, #4]
	LSL      r0, r0, #2
	LDR      r2, [r7, r0]
	CMP      r2, #0
	BNE      |sub_0800408E|
	LDR      r0, [pc, #0xe0]
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r0, r2, r0
	CMP      r1, #0
	BEQ      |loc_0800408A|
	LDR      r0, [r0]
	LDR      r0, [r0, #0x58]
	STR      r0, [r5]
|loc_0800408A|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
