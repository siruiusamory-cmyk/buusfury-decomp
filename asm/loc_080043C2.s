	CODE16
|loc_080043C2|
	PUSH     {r3, lr}
	LDRB     r1, [r0]
	MOV      r3, #0x68
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	BL       |sub_08013B34|
	POP      {r3, pc}
