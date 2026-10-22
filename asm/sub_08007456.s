	CODE16
|sub_08007456|
	LSL      r0, r0, #0
	LDR      r3, [sp, #0x350]
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0x1f
	LSR      r7, r0, #0x20
	LDR      r5, [sp, #0x60]
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800747C|
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800747C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
