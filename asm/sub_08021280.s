	CODE16
|sub_08021280|
	EXPORT |sub_08021280|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r7, r3, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r6, [sp, #0x28]
	BNE      |sub_080212A0|
	MOV      r0, #0x60
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080212A0|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
