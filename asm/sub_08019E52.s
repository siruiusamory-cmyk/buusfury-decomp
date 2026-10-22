	CODE16
|sub_08019E52|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0, #0x15]
	ADD      r5, r1, #0
	LSL      r0, r0, #1
	ADD      r0, r0, r4
	ADD      r0, #0x2e
	LDRB     r0, [r0]
	LDR      r1, [pc, #0x15c]
	LSL      r0, r0, #2
	ADD      r1, #0x24
	LDR      r1, [r1, r0]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x13440
	LDRB     r0, [r4, #0x15]
	LSL      r0, r0, #1
	ADD      r0, r0, r4
	ADD      r0, #0x2e
	LDRB     r4, [r0]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08019E8A|
	LDR      r1, [pc, #0x14c]
	STR      r1, [r0]
	STR      r4, [r0, #8]
|loc_08019E8A|
	ADD      r4, r0, #0
	MOV      r1, #3
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0x120]
	PUSH     {r3, lr}
	LDR      r1, [r1, #0x14]
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BNE      |sub_08019EAE|
	MOV      r0, #0
	POP      {r3, pc}
