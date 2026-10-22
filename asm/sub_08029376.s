	CODE16
|sub_08029376|
	LSL      r0, r0, #0
	DCW      0xf04c,0x0874
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
|loc_08029384|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r7, r3, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r6, [sp, #0x28]
	BNE      |sub_080293A4|
	MOV      r0, #0x58
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080293A4|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
