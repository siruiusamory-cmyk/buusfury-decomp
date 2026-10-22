	CODE16
|sub_0801F882|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r5, #0xff
	ADD      r5, #1
	ADD      r4, r1, #0
	LDR      r1, [r5, #0x18]
	MOV      r7, #1
	STR      r7, [r1, #0x10]
	LDR      r1, [r5, #0x1c]
	ADD      r2, r5, #0
	STR      r7, [r1, #0x10]
	MOV      r1, #0xff
	ADD      r1, #0x15
	LDRB     r1, [r1, r0]
	ADD      r2, #0x2c
	STR      r2, [sp]
	MOV      r2, #0x5d
	LSL      r2, r2, #5
	ADD      r6, r0, r2
	CMP      r1, #0
	BEQ      |sub_0801F8CE|
	CMP      r1, #1
	BNE      |loc_0801F902|
	LDR      r1, [r5, #0x18]
	LDR      r2, [r5, #0x28]
	ADD      r0, r7, #0
	CMP      r2, #0
	BNE      |loc_0801F8BC|
	MOV      r0, #0
|loc_0801F8BC|
	STR      r0, [r1, #8]
	LDR      r0, [r5, #0x1c]
	LDR      r1, [r6]
	LDR      r2, [r5, #0x28]
	SUB      r1, #1
	CMP      r1, r2
	BLE      |loc_0801F8FC|
	MOV      r1, #1
	B        |sub_0801F8FE|
