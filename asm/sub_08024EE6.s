	CODE16
|sub_08024EE6|
	ADD      r1, pc, #0x4C
	ADD      r2, r7, #0
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x512
	CMP      r5, #0
	BEQ      |loc_08024EFA|
	LDR      r0, [r5, #8]
	CMP      r0, #0
	BNE      |loc_08024F16|
|loc_08024EFA|
	MOV      r0, #0xc8
	STR      r0, [r4, #4]
	MOV      r0, #0x22
	STR      r0, [r4, #8]
	MOV      r1, #1
	STRB     r1, [r4]
	MOV      r0, #0x61
	LDR      r6, [pc, #0x18]
	LSL      r0, r0, #3
	LDR      r2, [r6, r0]
	MOV      r1, #0x38
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x5e2
|loc_08024F16|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	ASR      r0, r3, #0x17
	LSR      r3, r6, #1
	DCW      0xf5a5,0x0803
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	ASR      r4, r6, #9
	LSR      r1, r6, #1
|loc_08024F2C|
	LSL      r7, r7, #0
	LSL      r7, r7, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
|loc_08024F34|
	LSL      r5, r4, #0
	LSL      r4, r4, #1
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	BNE      |sub_08024F52|
	MOV      r0, #0x59
	LSL      r0, r0, #5
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08024F52|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
