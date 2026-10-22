	CODE16
|Object_Destroy21|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x168]
	LDR      r5, [pc, #0x164]
	STR      r0, [r4]
	LDR      r0, [r5]
	ADD      r6, r1, #0
	LDR      r2, [pc, #0x174]
	LDR      r1, [pc, #0x16c]
	ADD      r0, r0, r2
	BL       |inc_0x03d784_0x041118| + 0xb7e
	LDR      r0, [pc, #0x14c]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x168]
	CMP      r1, r0
	BEQ      |loc_080370F6|
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080370F6|
	LDR      r0, [pc, #0x160]
	CMP      r6, #0
	STR      r0, [r4]
	BEQ      |loc_08037104|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08037104|
	POP      {r4, r5, r6, pc}
|loc_08037106|
	MOV      r1, #2
	STRB     r1, [r0, #0x10]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0, #0x10]
	SUB      sp, #0x3c
	CMP      r0, #0
	BEQ      |sub_08037132|
	CMP      r0, #2
	BNE      |loc_08037140|
	LDR      r0, [r4, #0x18]
	SUB      r0, #0x20
	STR      r0, [r4, #0x18]
	BNE      |loc_0803712E|
	LDR      r6, [pc, #0x110]
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_0803712E|
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
