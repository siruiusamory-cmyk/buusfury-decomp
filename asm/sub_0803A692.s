	CODE16
|sub_0803A692|
	LSL      r0, r0, #0
	SUB      sp, #0x140
	LSR      r7, r6, #1
	ASR      r4, r6, #9
	LSR      r1, r6, #1
	ADD      r2, #0xd4
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	LDRH     r0, [r1, #0x12]
	ADD      r4, r1, #0
	SUB      sp, #0x18
	ADD      r0, #1
	LSL      r1, r0, #0x10
	LSR      r1, r1, #0x10
	STRH     r1, [r4, #0x12]
	LDR      r2, [r4, #0x50]
	LSR      r0, r1, #3
	LDR      r2, [r2]
	LSL      r3, r2, #3
	CMP      r3, r1
	BNE      |loc_0803A71E|
	LDR      r5, [pc, #0xd0]
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #3
	LSL      r1, r1, #9
	CMP      r0, r1
	BGE      |sub_0803A6D8|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed20
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
