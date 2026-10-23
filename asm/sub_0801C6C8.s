	CODE16
|sub_0801C6C8|
	EXPORT |sub_0801C6C8|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0801C700|
	MOV      r0, #0x60
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0801C700|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
