	CODE16
|sub_08019DA8|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	LDRB     r1, [r0, #0x15]
	LSL      r1, r1, #1
	ADD      r0, r1, r0
	ADD      r0, #0x2e
	LDRB     r5, [r0]
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08019DCC|
	LDR      r1, [pc, #0x208]
	STR      r1, [r0]
	STR      r5, [r0, #8]
	MOV      r1, #0
	STR      r1, [r0, #0xc]
	STR      r1, [r0, #0x10]
|loc_08019DCC|
	ADD      r5, r0, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0x1dc]
	PUSH     {r3, lr}
	LDR      r1, [r1, #0x14]
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BNE      |sub_08019DF0|
	MOV      r0, #0
	POP      {r3, pc}
