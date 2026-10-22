	CODE16
|sub_080246A2|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	ADD      r1, pc, #0x3D0
	LSR      r4, r0, #0x20
	STMIA    r3!, {r2, r3, r7}
	LSR      r2, r6, #1
|loc_080246B4|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080246CE|
	MOV      r0, #0x58
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080246CE|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
