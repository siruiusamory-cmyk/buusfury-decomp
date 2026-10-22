	CODE16
|sub_08008AA0|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	LDR      r5, [pc, #0x260]
	CMP      r1, #0
	LDR      r0, [r5, #0x10]
	BEQ      |loc_08008AB2|
	BL       |List_ReleaseAll3|
	B        |loc_08008AB6|
|loc_08008AB2|
	BL       |loc_08012900|
|loc_08008AB6|
	LDRB     r1, [r7, #2]
	LDR      r0, [r7, #4]
	BL       |sub_080089CC|
	ADD      r1, r0, #0
	LDR      r0, [r5, #0xc]
	BL       |loc_08009670|
	LDR      r0, [r7, #4]
	LDRB     r4, [r0, #3]
	SUB      r4, #1
	BMI      |loc_08008AFC|
|loc_08008ACE|
	LDR      r0, [r7, #4]
	LSL      r1, r4, #3
	LDR      r0, [r0, #0x10]
	ADD      r6, r0, r1
	LDR      r0, [r6]
	BL       |loc_08004784|
	CMP      r0, #0
	BEQ      |loc_08008AF8|
	LDR      r5, [pc, #0x224]
	LDR      r0, [r6, #4]
	LDR      r5, [r5, #0x10]
	LDR      r1, [r0]
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r5]
	ADD      r2, r1, #1
	LSL      r1, r1, #2
	ADD      r1, r1, r5
	STR      r2, [r5]
	STR      r0, [r1, #4]
|loc_08008AF8|
	SUB      r4, #1
	BPL      |loc_08008ACE|
|loc_08008AFC|
	POP      {r3, r4, r5, r6, r7, pc}
