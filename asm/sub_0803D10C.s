	CODE16
|sub_0803D10C|
	ADD      r2, #0xfc
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x248]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x44
	CMP      r1, #0
	BNE      |sub_0803D126|
	MOV      r0, #0
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
