	CODE16
|sub_0801C8DC|
	PUSH     {r3, lr}
	BL       |inc_0x153f2_0x1a3f2| + 0x48d2
	POP      {r3, pc}
|sub_0801C8E4|
	DCW      0xa2e8
	DCW      0x0804,0xe984,0x0871,0xe200
|sub_0801C8EE|
	LSR      r1, r6, #1
	STR      r3, [sp, #0x320]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	DCW      0xf400,0xffff
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0801C91C|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0801C91C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
