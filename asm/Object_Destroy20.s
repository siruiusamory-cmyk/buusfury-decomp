	CODE16
|Object_Destroy20|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1c8]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x1d4]
	CMP      r1, r0
	BEQ      |loc_080356CC|
	LDR      r0, [pc, #0x1bc]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080356CC|
	LDR      r0, [pc, #0x1c8]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080356DA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080356DA|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0, #0x10]
	SUB      sp, #0x38
	LDR      r6, [pc, #0x19c]
	CMP      r0, #0
	BEQ      |sub_08035704|
	CMP      r0, #1
	BNE      |loc_08035700|
	LDR      r0, [r4, #0x34]
	SUB      r0, #4
	STR      r0, [r4, #0x34]
	CMP      r0, #0
	BGT      |loc_08035700|
	ADD      r1, r4, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08035700|
	ADD      sp, #0x38
	POP      {r4, r5, r6, pc}
