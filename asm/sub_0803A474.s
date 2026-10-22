	CODE16
|sub_0803A474|
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803A484|
	LDR      r1, [pc, #0x10]
	STR      r1, [r0]
|loc_0803A484|
	POP      {r3, pc}
	LSL      r0, r0, #0
	STMIA    r3!, {r3, r4, r5}
	LSR      r4, r0, #0x20
	ADD      sp, #0x120
	LSR      r7, r6, #1
	BLS      |loc_0803A3AC|
	LSR      r4, r0, #0x20
	STMIA    r6!, {r4, r5}
	LSR      r4, r0, #0x20
	LDR      r0, [r1, #0x50]
	LDR      r2, [r0]
	LSL      r2, r2, #3
	SUB      r2, #1
	STRH     r2, [r1, #0x12]
	MOV      r2, #0x38
	STRB     r2, [r1, #8]
	LDR      r0, [r0]
	ADD      r0, #0xff
	STRB     r0, [r1, #0x11]
	BX       lr
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDRH     r1, [r1, #0x12]
	CMP      r1, #0
	BNE      |sub_0803A4C6|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
