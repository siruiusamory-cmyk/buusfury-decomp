	CODE16
|sub_08011A1E|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	MOV      r0, #0x61
	LSL      r0, r0, #4
	ADD      r6, r7, r0
	LDR      r4, [r6]
	SUB      r4, #1
	BMI      |loc_08011A6E|
|loc_08011A2E|
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	ADD      r1, r0, #0
	ADD      r0, #4
	LDR      r5, [r0]
	LDR      r2, [r5, #4]
	SUB      r2, #1
	STR      r2, [r5, #4]
	BNE      |loc_08011A6A|
	LDR      r2, [r6]
	SUB      r2, #1
	STR      r2, [r6]
	SUB      r2, r2, r4
	BEQ      |loc_08011A52|
	LSL      r2, r2, #2
	ADD      r1, #8
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08011A52|
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
|loc_08011A6A|
	SUB      r4, #1
	BPL      |loc_08011A2E|
|loc_08011A6E|
	LDR      r4, [r7, #4]
	SUB      r4, #1
	BMI      |loc_08011A8A|
	ADD      r5, r7, #4
|loc_08011A76|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	SUB      r4, #1
	BPL      |loc_08011A76|
|loc_08011A8A|
	POP      {r3, r4, r5, r6, r7, pc}
|loc_08011A8C|
	DCW      0x2824
	DCW      0x0807,0xffff
|loc_08011A92|
	LSL      r0, r0, #0
	ADD      r3, sp, #0x280
	LSR      r4, r0, #0x20
	CMP      r2, #0x4c
	LSL      r0, r0, #0xc
	LSL      r4, r1, #0x10
	LSL      r0, r0, #0
