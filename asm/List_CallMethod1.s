	CODE16
|List_CallMethod1|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r4, [r0, #4]
	ADD      r7, r0, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	SUB      r4, #1
	BMI      |loc_08011CA0|
	ADD      r1, r7, #4
	STR      r1, [sp]
|loc_08011C82|
	LDR      r1, [sp]
	LSL      r0, r4, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r3, r2, r1
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	CMP      r0, #0
	BNE      |loc_08011CC8|
	SUB      r4, #1
	BPL      |loc_08011C82|
|loc_08011CA0|
	LDR      r0, [pc, #0x100]
	ADD      r7, r7, r0
	LDR      r4, [r7]
	SUB      r4, #1
	BMI      |loc_08011CC6|
|loc_08011CAA|
	LSL      r0, r4, #2
	ADD      r0, r0, r7
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r3, r2, r1
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	CMP      r0, #0
	BNE      |loc_08011CC8|
	SUB      r4, #1
	BPL      |loc_08011CAA|
|loc_08011CC6|
	MOV      r0, #0
|loc_08011CC8|
	POP      {r3, r4, r5, r6, r7, pc}
