	CODE16
|sub_0800D892|
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	BL       |sub_0800DB42|
	LDR      r0, [r4, #0x4c]
	CMP      r0, #0
	BEQ      |loc_0800D8D0|
	LDR      r4, [r0, #8]
	LDRH     r5, [r0, #2]
	LDR      r6, [r0, #4]
	LDRB     r0, [r4]
	ADD      r1, r0, #1
	STRB     r1, [r4]
	CMP      r0, #0
	BNE      |loc_0800D8D0|
	LDR      r0, [pc, #0x58]
	ADD      r1, r5, #0
	LDR      r0, [r0]
	BL       |loc_0801124C|
	LSL      r0, r0, #0x10
	ASR      r0, r0, #0x10
	STRH     r0, [r4, #2]
	LDR      r1, [pc, #0x4c]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0800D8D0|
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #0x4c]
	CMP      r0, #0
	BEQ      |loc_0800D904|
	LDR      r4, [r0, #8]
	LDRB     r0, [r4]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r4]
	BNE      |loc_0800D904|
	LDRH     r0, [r4, #2]
	LDR      r1, [pc, #0x24]
	CMP      r0, r1
	BEQ      |loc_0800D904|
	MOV      r3, #2
	LDR      r0, [pc, #0x14]
	LDRSH    r1, [r4, r3]
	LDR      r0, [r0]
	BL       |loc_0801142A|
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #2]
|loc_0800D904|
	ADD      r0, r5, #0
	BL       |Handle_Release1|
	POP      {r3, r4, r5, pc}
|loc_0800D90C|
	DCW      0x2588
	DCW      0x0807,0x0000,0x0601,0xffff
|loc_0800D916|
	LSL      r0, r0, #0
