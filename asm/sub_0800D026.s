	CODE16
|sub_0800D026|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x34]
	LDR      r0, [r0, #0x2c]
	LDR      r0, [r0, #4]
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x34]
	ADD      r1, r5, #0
	LDR      r0, [r0, #0x2c]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDRH     r0, [r4, #0x16]
	LDR      r1, [pc, #0x168]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LDR      r1, [r4, #0x34]
	LDR      r1, [r1, #0x2c]
	LDR      r2, [r1, #4]
	ADD      r1, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r0, r5, #0
	BL       |GBARam_Free|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x34]
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x13c]
	LDR      r0, [r0]
	BL       |loc_0801124C|
	STRH     r0, [r4, #0x16]
	ADD      r0, r4, #0
	BL       |sub_0800D026|
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDRH     r0, [r0, #0x16]
	LDR      r1, [pc, #0x130]
	CMP      r0, r1
	BNE      |loc_0800D09A|
	LDR      r0, [r4, #0x34]
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x118]
	LDR      r0, [r0]
	BL       |loc_0801124C|
	STRH     r0, [r4, #0x16]
	ADD      r0, r4, #0
	BL       |sub_0800D026|
|loc_0800D09A|
	LDRH     r0, [r4, #0x16]
	POP      {r4, pc}
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r6, r3, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_0800D0BC|
	MOV      r0, #0x38
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800D0BC|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
