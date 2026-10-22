	CODE16
|sub_08007564|
	STMIA    r1!, {r2, r3, r4}
	LSR      r4, r0, #0x20
	STR      r6, [sp, #0x330]
	LSR      r4, r0, #0x20
	LSL      r0, r1, #0x1f
	LSR      r7, r0, #0x20
	STR      r5, [sp, #0x2d0]
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800758C|
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800758C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
