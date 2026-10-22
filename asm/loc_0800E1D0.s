	CODE16
|loc_0800E1D0|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BL       |sub_0800E0F4|
	LDR      r1, [r5]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r5, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r5, r0, #0
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x1b0]
	MOV      r6, #0x9f
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0]
	LSL      r6, r6, #3
	LDR      r7, [pc, #0x1a4]
	LSL      r1, r0, #0x1f
	LSR      r1, r1, #0x1f
	CMP      r1, #0
	BNE      |loc_0800E21C|
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1f
	BNE      |loc_0800E21C|
	LDR      r0, [r7, #4]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	ADD      r0, r0, r6
	BL       |loc_08013E06|
|loc_0800E21C|
	LDR      r0, [r4, #0xc]
	ADD      r0, #0x6e
	STR      r0, [r4, #0xc]
	LSR      r0, r0, #0x10
	BEQ      |loc_0800E2F0|
	ADD      r0, r5, #0
	ADD      r0, #0x1a
	ADD      r1, r0, #2
	MOV      r3, #0
	LDRSH    r1, [r1, r3]
	LDR      r3, [pc, #0x174]
	MUL      r1, r3
	ASR      r1, r1, #0x10
	MOV      r3, #0
	LDRSH    r2, [r0, r3]
	ADD      r2, r2, r1
	MOV      r3, #2
	LDRSH    r5, [r0, r3]
	CMP      r2, r5
	BLE      |sub_0800E24A|
	LDRH     r1, [r0, #2]
	STRH     r1, [r0]
	B        |sub_0800E25C|
