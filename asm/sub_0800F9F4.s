	CODE16
|sub_0800F9F4|
	PUSH     {r3, lr}
	LDRB     r2, [r2, #1]
	CMP      r2, #0
	BNE      |loc_0800FA0E|
	ADD      r2, r0, #0
	LDR      r0, [pc, #0x2e0]
	ADD      r2, #0xff
	ADD      r2, #0x9d
	LDR      r0, [r0, #8]
	BL       |loc_08009904|
	CMP      r0, #0
	BEQ      |sub_0800FA12|
|loc_0800FA0E|
	MOV      r0, #1
	POP      {r3, pc}
