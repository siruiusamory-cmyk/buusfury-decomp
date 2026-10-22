	CODE16
|loc_0800A95A|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r6, #0
|loc_0800A962|
	LDR      r0, [r4]
	CMP      r0, #0
	BEQ      |loc_0800A984|
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |sub_0800A9AE|
	LDR      r0, [r4]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_0800A984|
	LDRB     r0, [r4, #4]
	ADD      r0, #1
	LSL      r1, r0, #0x18
	ASR      r1, r1, #0x18
	STRB     r1, [r4, #4]
	LDR      r0, [r4, #8]
	LDR      r2, [r0]
	CMP      r1, r2
	BLT      |loc_0800A998|
	STRB     r6, [r4, #4]
|loc_0800A998|
	MOV      r3, #4
	LDRSB    r1, [r4, r3]
	LSL      r1, r1, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	ADD      r1, r5, #0
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	STR      r0, [r4]
	B        |loc_0800A962|
