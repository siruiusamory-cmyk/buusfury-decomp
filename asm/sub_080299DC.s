	CODE16
|sub_080299DC|
	EXPORT |sub_080299DC|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080299FC|
	LDR      r1, [pc, #0x44]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_080299FC|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r6, [r0, #0xc]
	ADD      r5, r0, #0
	ADD      r0, r1, #0
	ADD      r4, r1, #0
	LDR      r1, [r1]
	ADD      r7, r2, #0
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r1, #0xa3
	LSL      r1, r1, #2
	ADD      r1, r4, r1
	MUL      r6, r0
	ASR      r0, r6, #0x10
	LDR      r1, [r1]
	LSL      r0, r0, #0xa
	CMP      r1, r0
	BGE      |sub_08029A36|
	LDR      r0, [r5, #0x10]
	ADD      r2, r7, #0
|loc_08029A2C|
	ADD      r1, r4, #0
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, r4, r5, r6, r7, pc}
