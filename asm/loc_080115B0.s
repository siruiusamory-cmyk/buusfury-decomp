	CODE16
|loc_080115B0|
	PUSH     {r0, r4, r5, r6, r7, lr}
	SUB      sp, #0x1fc
	SUB      sp, #0x14
	MOV      r1, #0
	STR      r1, [sp, #0xc]
	LDR      r1, [sp, #0x210]
	ADD      r7, sp, #0xc
	LDR      r4, [r1, #4]
	SUB      r4, #1
	BMI      |loc_080115F2|
	LDR      r6, [sp, #0x210]
	ADD      r6, #4
|loc_080115C8|
	LSL      r0, r4, #2
	ADD      r5, r0, r6
	ADD      r5, #4
	LDR      r0, [r5]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_080115EE|
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0xc]
	ADD      r0, #1
	STR      r0, [sp, #0xc]
	LSL      r0, r1, #2
	LDR      r1, [r5]
	ADD      r0, r0, r7
	STR      r1, [r0, #4]
|loc_080115EE|
	SUB      r4, #1
	BPL      |loc_080115C8|
|loc_080115F2|
	LDR      r0, [sp, #0xc]
	ADD      r7, sp, #0xc
	ADD      r6, r7, #4
	LSL      r0, r0, #2
	ADD      r7, r0, r7
	CMP      r6, r7
	BCS      |loc_080116A2|
	SUB      r0, r7, r6
	ASR      r0, r0, #3
	LSL      r0, r0, #2
	ADD      r4, r0, r6
	CMP      r6, r4
	BEQ      |sub_0801163A|
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x9dc0
	CMP      r0, #0
	BEQ      |loc_08011620|
	LDR      r0, [sp, #0x10]
	LDR      r1, [r4]
	STR      r1, [sp, #0x10]
	STR      r0, [r4]
|loc_08011620|
	ADD      r1, r7, #0
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x9dc0
	CMP      r0, #0
	BEQ      |loc_08011634|
	LDR      r0, [sp, #0x10]
	LDR      r1, [r7]
	STR      r1, [sp, #0x10]
	STR      r0, [r7]
|loc_08011634|
	ADD      r5, r6, #0
	ADD      r4, r7, #0
	B        |sub_08011650|
