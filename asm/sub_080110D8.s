|sub_080110D8|
	EXPORT |sub_080110D8|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r7, r2, #0
	ADD      r6, r3, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r5, [sp, #0x28]
	BNE      |sub_080110FA|
	MOV      r0, #0xff
	ADD      r0, #0xbd
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080110FA|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
