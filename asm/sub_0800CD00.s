	CODE16
|sub_0800CD00|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x5c]
	LDR      r0, [r0, #0x2c]
	LDR      r0, [r0, #4]
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x5c]
	ADD      r1, r5, #0
	LDR      r0, [r0, #0x2c]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDRH     r0, [r4, #0x16]
	LDR      r1, [pc, #0xbc]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LDR      r1, [r4, #0x5c]
	LDR      r1, [r1, #0x2c]
	LDR      r2, [r1, #4]
	ADD      r1, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r0, r5, #0
	BL       |GBARam_Free|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x5c]
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x90]
	LDR      r0, [r0]
	BL       |loc_0801124C|
	STRH     r0, [r4, #0x16]
	ADD      r0, r4, #0
	BL       |sub_0800CD00|
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDRH     r0, [r0, #0x16]
	LDR      r1, [pc, #0x84]
	CMP      r0, r1
	BNE      |loc_0800CD74|
	LDR      r0, [r4, #0x5c]
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x6c]
	LDR      r0, [r0]
	BL       |loc_0801124C|
	STRH     r0, [r4, #0x16]
	ADD      r0, r4, #0
	BL       |sub_0800CD00|
|loc_0800CD74|
	LDRH     r0, [r4, #0x16]
	POP      {r4, pc}
