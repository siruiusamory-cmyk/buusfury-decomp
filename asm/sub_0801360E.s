	CODE16
|sub_0801360E|
	LSL      r0, r0, #0
	STRB     r4, [r0, #2]
	LSR      r3, r5, #1
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	BGE      |loc_0801360C|
	LSR      r1, r6, #1
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |Stats_GetLevel|
	CMP      r0, #0xc8
	BLT      |loc_0801362C|
	MOV      r0, #0
	POP      {r4, pc}
|loc_0801362C|
	LDR      r1, [r4, #0x24]
	LDR      r2, [pc, #0x2d8]
	LSL      r0, r0, #2
	ADD      r0, r0, r2
	SUB      r0, #0xff
	SUB      r0, #1
	LDR      r0, [r0, #0x3c]
	SUB      r0, r0, r1
	POP      {r4, pc}
