	CODE16
|sub_0800C65E|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x1dc]
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	ADD      sp, r3
	BNE      |sub_0800C680|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800C680|
	ADD      r0, r4, #0
	LDR      r3, [pc, #0x1c8]
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
