	CODE16
|sub_0803E3A8|
	PUSH     {r3, lr}
	MOV      r2, #0
	LSL      r3, r2, #6
	ADD      r3, r3, r0
	LDRB     r3, [r3, #0x10]
	LSL      r3, r3, #0x1f
	BNE      |sub_0803E3C2|
	LSL      r2, r2, #6
	ADD      r0, r2, r0
	MOV      r2, #0x40
	BL       |inc_0x049120_0x055620| + 0x18
	POP      {r3, pc}
