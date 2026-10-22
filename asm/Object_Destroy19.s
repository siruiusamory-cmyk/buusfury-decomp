	CODE16
|Object_Destroy19|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1d0]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x1e4]
	CMP      r1, r0
	BEQ      |loc_0802A3C2|
	LDR      r0, [pc, #0x1c8]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0802A3C2|
	LDR      r0, [pc, #0x1dc]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0802A3D0|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0802A3D0|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0, #0x10]
	SUB      sp, #0x4c
	CMP      r0, #0
	BEQ      |sub_0802A412|
	CMP      r0, #1
	BNE      |loc_0802A4C8|
	LDR      r0, [r4, #0x38]
	LDR      r1, [r4, #0x3c]
	LSL      r0, r0, #2
	LSL      r1, r1, #2
	STR      r1, [sp, #0x48]
	STR      r0, [sp, #0x44]
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
	BGT      |loc_0802A4C8|
	LDR      r6, [pc, #0x17c]
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
