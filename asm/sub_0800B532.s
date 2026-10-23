	CODE16
|sub_0800B532|
	PUSH     {r4, lr}
	LDR      r4, [r2, #0xc]
	MOV      r3, #0x68
	LDRB     r1, [r4]
	MUL      r1, r3
	MOV      r3, #0x9f
	LSL      r3, r3, #3
	ADD      r1, r1, r4
	ADD      r1, r1, r3
	ADD      r1, #0x2c
	LDRH     r1, [r1]
	CMP      r1, #0
	BNE      |sub_0800B558|
	ADD      r1, r0, #0
	LDR      r0, [r2, #8]
	BL       |loc_08011944|
	MOV      r0, #0
	POP      {r4, pc}
