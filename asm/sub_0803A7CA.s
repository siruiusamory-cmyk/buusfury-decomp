	CODE16
|sub_0803A7CA|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	MOV      r0, #0xff
	ADD      r0, #0x2e
	BL       |inc_0x0158_0x143f2|
	ADD      r2, r0, #0
|loc_0803A7D8|
	LDR      r0, [pc, #0x18]
	MOV      r1, #5
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11b72
	CMP      r0, #0
	BNE      |sub_0803A7EA|
	MOV      r0, #1
	POP      {r3, pc}
