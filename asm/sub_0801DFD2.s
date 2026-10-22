	CODE16
|sub_0801DFD2|
	LSL      r0, r0, #0
	DCW      0xe9d8,0x0871
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	PUSH     {r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x24
	BNE      |sub_0801DFFC|
	MOV      r0, #0x48
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0801DFFC|
	ADD      r0, r4, #0
	ADD      sp, #0x24
	POP      {r4, r5, pc}
