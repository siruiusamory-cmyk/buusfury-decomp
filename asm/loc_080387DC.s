	CODE16
|loc_080387DC|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x3c]
	SUB      sp, #0x34
	ADD      r0, #1
	ASR      r1, r0, #2
	LSL      r2, r1, #0x1e
	LSR      r2, r2, #0x1e
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	STR      r0, [r4, #0x3c]
	LDR      r0, [r4, #0x2c]
	LDR      r3, [r4, #0x30]
	LSL      r2, r2, #2
	MOV      r6, #1
	LSL      r6, r6, #0xa
	ADD      r2, r0, r2
	CMP      r3, r2
	LDR      r5, [pc, #0x260]
	BEQ      |loc_0803884E|
	LDR      r7, [r4, #0x28]
	CMP      r7, #0
	BEQ      |sub_0803881A|
	CMP      r3, r0
	BNE      |sub_0803881A|
	ADD      r1, r4, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
