	CODE16
|sub_0800E25C|
	MOV      r0, #0
|loc_0800E25E|
	LDR      r7, [pc, #0x144]
	LDR      r1, [r7, #4]
	LDRB     r1, [r1]
	CMP      r1, r0
	BEQ      |loc_0800E2E2|
	MOV      r2, #0x68
	LDR      r1, [r7, #4]
	MUL      r2, r0
	MOV      r6, #0x9f
	LSL      r6, r6, #3
	ADD      r1, r2, r1
	ADD      r2, r1, r6
	ADD      r1, r2, #0
	ADD      r1, #0x1a
	ADD      r5, r1, #2
	MOV      r3, #0
	LDRSH    r5, [r5, r3]
	LDR      r3, [pc, #0x128]
	MUL      r3, r5
	ASR      r5, r3, #0x10
	MOV      r3, #0
	LDRSH    r6, [r1, r3]
	ADD      r6, r6, r5
	MOV      r3, #2
	LDRSH    r7, [r1, r3]
	CMP      r6, r7
	BLE      |sub_0800E29A|
	LDRH     r3, [r1, #2]
	STRH     r3, [r1]
	B        |loc_0800E2AC|
