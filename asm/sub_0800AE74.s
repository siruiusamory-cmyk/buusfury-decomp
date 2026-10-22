	CODE16
|sub_0800AE74|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r2, [r0, #0x20]
	ADD      r5, r4, #0
	ADD      r6, r4, #0
	ADD      r6, #0x60
	ADD      r5, #0x80
	LDR      r0, [r0, #0x18]
	LDR      r1, [r4, #0x14]
	CMP      r2, #0
	SUB      sp, #0x1c
	BEQ      |loc_0800AEF6|
	CMP      r1, r0
	BNE      |loc_0800AEF6|
	LDR      r0, [r4, #0x30]
	CMP      r0, #0
	BEQ      |loc_0800AF6C|
	LDR      r0, [r4, #0x48]
	CMP      r0, #0
	BEQ      |loc_0800AEAA|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x1fc]
	LDR      r0, [r0, #4]
	BL       |loc_08011944|
	MOV      r6, #0
	STR      r6, [r4, #0x48]
|loc_0800AEAA|
	MOV      r6, #0
	STR      r6, [r4, #0x30]
	LDR      r0, [r4, #0x18]
	LDRH     r0, [r0]
	CMP      r0, #0
	BEQ      |sub_0800AED0|
	LDR      r0, [r4, #0x4c]
	LDR      r1, [r5, #0x24]
	LDR      r0, [r0, #0x10]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	STR      r6, [r4, #0x20]
	STR      r6, [r4, #0x1c]
	LDR      r0, [r4, #0x18]
	STR      r0, [r4, #0x14]
	MOV      r0, #1
	STR      r0, [r4, #0x2c]
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
