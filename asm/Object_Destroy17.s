	CODE16
|Object_Destroy17|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x234]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x23c]
	CMP      r1, r0
	BEQ      |loc_0802879C|
	LDR      r0, [pc, #0x228]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0802879C|
	LDR      r0, [pc, #0x230]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080287AA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080287AA|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r2, [r4, #0x10]
	ADD      r0, r1, #0
	SUB      sp, #0x3c
	CMP      r2, #0
	BEQ      |sub_080287EE|
	CMP      r2, #1
	BNE      |loc_080288A4|
	LDR      r0, [r4, #0x38]
	LDR      r1, [r4, #0x3c]
	LSL      r0, r0, #2
	LSL      r1, r1, #2
	STR      r1, [sp, #0x38]
	STR      r0, [sp, #0x34]
	LDR      r2, [r4, #0x20]
	ADD      r0, r2, r0
	STR      r0, [r4, #0x20]
	LDR      r0, [r4, #0x24]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x40]
	SUB      r0, #4
	STR      r0, [r4, #0x40]
	CMP      r0, #0
	BGT      |loc_080288A4|
	LDR      r5, [pc, #0x1dc]
	ADD      r1, r4, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
