	CODE16
|sub_08007C52|
	MOV      r3, #1
	LSL      r3, r3, #0xb
	ADD      r3, sp
	LDR      r2, [r3, #0x20]
	MOV      r6, lr
	LDR      r2, [r2]
	ADD      r6, r6, r0
	ADD      r2, r2, r0
	BMI      |loc_08007C74|
	LDR      r3, [r4, #8]
	LDRB     r7, [r3, #0x14]
	MOV      r3, #1
	LSL      r3, r3, #0xb
	ADD      r3, sp
	STR      r7, [r3, #0x18]
	CMP      r2, r7
	BLT      |sub_08007C7C|
|loc_08007C74|
	MOV      r2, #1
	LSL      r2, r6
	ORR      r5, r2
	B        |sub_08007C92|
