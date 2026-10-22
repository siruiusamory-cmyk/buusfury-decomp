	CODE16
|sub_08038498|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x23c]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x254]
	CMP      r1, r0
	BEQ      |loc_080384B2|
	LDR      r0, [pc, #0x234]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080384B2|
	LDR      r0, [pc, #0x24c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080384C0|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080384C0|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0, #0x10]
	SUB      sp, #0x44
	CMP      r0, #0
	BEQ      |sub_08038502|
	CMP      r0, #1
	BNE      |loc_080384FE|
	LDR      r0, [r4, #0x34]
	LDR      r1, [r4, #0x38]
	LSL      r0, r0, #2
	LSL      r1, r1, #2
	STR      r1, [sp, #0x40]
	STR      r0, [sp, #0x3c]
	LDR      r2, [r4, #0x1c]
	ADD      r0, r2, r0
	STR      r0, [r4, #0x1c]
	LDR      r0, [r4, #0x20]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x20]
	LDR      r0, [r4, #0x3c]
	SUB      r0, #4
	STR      r0, [r4, #0x3c]
	CMP      r0, #0
	BGT      |loc_080384FE|
	LDR      r6, [pc, #0x1e8]
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_080384FE|
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
