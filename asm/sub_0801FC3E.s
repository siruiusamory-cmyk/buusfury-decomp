	CODE16
|sub_0801FC3E|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r2, #0
	LSL      r2, r3, #3
	ADD      r4, r2, r5
	LDR      r6, [sp, #0x18]
	STR      r4, [sp]
	ADD      r7, r3, #0
	ADD      r3, r6, #0
	ADD      r4, #4
	ADD      r2, r4, #0
	BL       |sub_0801FBD0|
	CMP      r0, #0
	BEQ      |loc_0801FC78|
	LDR      r0, [r4]
	SUB      r0, r0, r6
	STR      r0, [r4]
	BNE      |loc_0801FC78|
	LDR      r0, [r5]
	SUB      r0, #1
	STR      r0, [r5]
	SUB      r0, r0, r7
	BEQ      |loc_0801FC78|
	LDR      r1, [sp]
	LSL      r2, r0, #3
	ADD      r1, #0xc
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0801FC78|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #1
	MOV      r7, #0
	ADD      r5, r0, #0
	CMP      r2, #0
	BEQ      |sub_0801FC9E|
	CMP      r2, #2
	BEQ      |loc_0801FD3E|
	CMP      r2, #3
	BNE      |loc_0801FD3C|
	LDR      r0, [r4, #0x24]
	CMP      r0, #5
	BGE      |sub_0801FD54|
	ADD      r0, #1
	STR      r0, [r4, #0x24]
	B        |loc_0801FD5A|
