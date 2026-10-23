	CODE16
|sub_080398A4|
	PUSH     {r3, lr}
	MOV      r0, #0x99
	BL       |inc_0x0158_0x143f2|
	ADD      r2, r0, #0
	LDR      r0, [pc, #0x18]
	MOV      r1, #5
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11b72
	CMP      r0, #0
	BNE      |sub_080398C0|
	MOV      r0, #1
	POP      {r3, pc}
