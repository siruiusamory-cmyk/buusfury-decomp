	CODE16
|sub_08042C80|
	MOV      r0, #0xb
	STRB     r0, [r5, #4]
	STRB     r1, [r5, #5]
	STRH     r4, [r5, #0x1e]
	STRH     r6, [r5, #0x1a]
	LDRB     r0, [r5, #7]
	CMP      r0, #0
	BEQ      |loc_08042C94|
	MOV      r0, #7
	STRB     r0, [r5, #7]
|loc_08042C94|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r7, lr}
	LDR      r5, [pc, #0x310]
	ADD      r1, r5, #0
	ADD      r1, #0x30
	LDRB     r2, [r1]
	ADD      r3, r2, #0
	AND      r3, r0
	BEQ      |loc_08042CE4|
	BIC      r2, r0
	STRB     r2, [r1]
	MOV      r1, #0
	MOV      r3, #1
	MOV      r4, #0
|loc_08042CB2|
	ADD      r2, r3, #0
	LSL      r2, r1
	AND      r2, r0
	BEQ      |loc_08042CC0|
	LSL      r2, r1, #1
	ADD      r2, r2, r5
	STRH     r4, [r2, #0x34]
|loc_08042CC0|
	ADD      r1, #1
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	CMP      r1, #4
	BCC      |loc_08042CB2|
	LDR      r1, [pc, #0x2e4]
	LDR      r1, [r1]
	LDRB     r4, [r1, #3]
	AND      r4, r0
	BEQ      |loc_08042CDA|
	ADD      r0, r4, #0
	BL       |inc_0x042118_0x049114| + 0x1264
|loc_08042CDA|
	ADD      r1, r4, #0
	MOV      r0, #0x33
	STRH     r4, [r5, #0x14]
	BL       |loc_0804333c|
|loc_08042CE4|
	POP      {r4, r5, r7, pc}
	PUSH     {r4, r5, r7, lr}
	LDR      r4, [pc, #0x2c0]
	ADD      r2, r0, #0
	MOV      r1, #0
	MOV      r0, #0
	CMP      r2, #0
	STRB     r1, [r4, #7]
	BEQ      |sub_08042D00|
	BL       |sub_08042ADA|
	MOV      r0, #0x17
	STRB     r0, [r4, #4]
|loc_08042CFE|
	POP      {r4, r5, r7, pc}
