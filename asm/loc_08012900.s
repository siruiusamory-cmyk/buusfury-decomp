	CODE16
|loc_08012900|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r4, [r0]
	ADD      r5, r0, #0
	SUB      r4, #1
	BMI      |loc_0801294C|
|loc_0801290A|
	LSL      r0, r4, #2
	ADD      r6, r0, r5
	LDR      r0, [r6, #4]
	ADD      r7, r6, #4
	STR      r0, [sp]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BNE      |loc_08012948|
	LDR      r0, [r5]
	SUB      r0, #1
	STR      r0, [r5]
	SUB      r0, r0, r4
	BEQ      |loc_08012936|
	LSL      r2, r0, #2
	ADD      r1, r7, #4
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08012936|
	LDR      r0, [sp]
	CMP      r0, #0
	BEQ      |loc_08012948|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08012948|
	SUB      r4, #1
	BPL      |loc_0801290A|
|loc_0801294C|
	ADD      r1, r5, #0
	ADD      r1, #0xc0
	MOV      r0, #1
	STR      r0, [r1, #4]
	MOV      r0, #0
	STR      r0, [r1, #0xc]
	LDR      r0, [r1, #8]
	ADD      r0, #1
	STR      r0, [r1, #8]
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	LDMIA    r1!, {r0}
	SUB      sp, #0x18
	STR      r1, [sp, #0x14]
	LDR      r1, [r1]
	ASR      r0, r0, #8
	ASR      r1, r1, #8
	STR      r0, [sp, #0xc]
	ADD      r2, r5, #0
	ADD      r2, #0xff
	LDR      r0, [pc, #0x394]
	STR      r1, [sp, #0x10]
	ADD      r2, #0x9d
	ADD      r7, r2, #0
	LDR      r0, [r0, #8]
	ADD      r1, sp, #0xc
	BL       |loc_080097C2|
	ADD      r6, r7, #4
	ADD      r5, r6, #4
	CMP      r0, #0
	BEQ      |sub_0801299E|
	LDR      r0, [r4]
	STR      r0, [r6]
	LDR      r1, [sp, #0x14]
	LDR      r0, [r1]
	STR      r0, [r5]
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
