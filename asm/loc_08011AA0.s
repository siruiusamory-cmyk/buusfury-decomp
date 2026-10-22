	CODE16
|loc_08011AA0|
	PUSH     {r3, r4, r5, r6, r7, lr}
	MOV      r1, #0x61
	LSL      r1, r1, #4
	ADD      r6, r0, r1
	LDR      r4, [r6]
	SUB      r4, #1
	BMI      |loc_08011B02|
|loc_08011AAE|
	LSL      r0, r4, #2
	ADD      r7, r0, r6
	STR      r7, [sp]
	ADD      r7, #4
	LDR      r0, [r7]
	LDR      r1, [r0]
	ADD      r5, r0, #0
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_08011AFE|
	LDR      r0, [r5, #4]
	SUB      r0, #1
	STR      r0, [r5, #4]
	BNE      |loc_08011AFE|
	LDR      r0, [r6]
	SUB      r0, #1
	STR      r0, [r6]
	SUB      r0, r0, r4
	BEQ      |loc_08011AE6|
	LDR      r1, [sp]
	LSL      r2, r0, #2
	ADD      r1, #8
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08011AE6|
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_08011AFE|
	SUB      r4, #1
	BPL      |loc_08011AAE|
|loc_08011B02|
	POP      {r3, r4, r5, r6, r7, pc}
