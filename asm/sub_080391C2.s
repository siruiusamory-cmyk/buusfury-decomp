	CODE16
|sub_080391C2|
	PUSH     {r3, lr}
	LSL      r1, r1, #2
	LDR      r1, [r2, r1]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r3, [pc, #0x3c]
	LSL      r2, r1, #2
	LDR      r2, [r3, r2]
	LDR      r3, [r0, #0x14]
	CMP      r3, r2
	BNE      |sub_080391E8|
	BL       |inc_0x0158_0x143f2| + 0xed58
	CMP      r0, #0
	BEQ      |sub_080391E8|
	MOV      r0, #1
	POP      {r3, pc}
