	CODE16
|sub_08027B18|
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BNE      |sub_08027B34|
	LDRH     r0, [r0, #0xc]
	LDR      r1, [pc, #0x20]
	MOV      r2, #0x40
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LDR      r1, [pc, #0x10]
	ADD      r1, #8
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0
	POP      {r3, pc}
