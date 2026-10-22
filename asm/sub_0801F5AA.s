	CODE16
|sub_0801F5AA|
	STR      r0, [r6]
	LDR      r1, [r6]
	CMP      r1, r0
	BNE      |sub_0801F5AA|
|loc_0801F5B2|
	LDR      r0, [r7]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_0801F570|
|loc_0801F5BA|
	LDR      r0, [pc, #0x214]
	MOV      r4, #0
	ADD      r5, r5, r0
	LDR      r0, [r5]
	CMP      r0, #0
	BLE      |loc_0801F61C|
	LDR      r7, [pc, #0x1f0]
|loc_0801F5C8|
	LSL      r0, r4, #3
	ADD      r0, r0, r5
	ADD      r0, #4
	LDRB     r1, [r0, #4]
	CMP      r1, #0
	BEQ      |sub_0801F5E4|
	CMP      r1, #1
	BEQ      |loc_0801F5EE|
	CMP      r1, #2
	BNE      |loc_0801F614|
	LDR      r0, [r0]
	LDR      r1, [r6]
	ADD      r0, r1, r0
	B        |sub_0801F60C|
