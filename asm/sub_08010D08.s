	CODE16
|sub_08010D08|
	LDRH     r3, [r1]
	ADD      r2, r3, r2
	LSL      r2, r2, #0x10
	ASR      r2, r2, #0x10
|loc_08010D10|
	STRH     r2, [r1]
	MOV      r3, #0
	LDRSH    r4, [r1, r3]
	CMP      r4, r2
	BNE      |loc_08010D10|
	LDRB     r1, [r0, #0x13]
	LSL      r1, r1, #0x1f
	BPL      |loc_08010D24|
	BL       |loc_08013C66|
|loc_08010D24|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BNE      |loc_08010D5C|
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r0, [r0, #0x2c]
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r4, #0x14]
	CMP      r1, r0
	BNE      |sub_08010D58|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_0800EEB0|
	CMP      r0, #0
	BEQ      |sub_08010D58|
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
