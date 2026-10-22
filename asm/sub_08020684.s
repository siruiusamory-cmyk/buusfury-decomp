	CODE16
|sub_08020684|
	MOV      r0, #0
	MOV      r1, #1
	SUB      r0, r1, r0
	STRB     r0, [r5, #0x10]
|loc_0802068C|
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	ADD      r4, #0x20
	LDRB     r1, [r4, #4]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x30]
	ADD      r3, r2, r1
	LDRB     r1, [r4, #8]
	LDR      r2, [r4, #0xc]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r4, pc}
	LSL      r0, r0, #0
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r7, [sp, #0x28]
	BNE      |sub_080206D6|
	MOV      r0, #0x54
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080206D6|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
