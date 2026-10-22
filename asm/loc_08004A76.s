	CODE16
|loc_08004A76|
	MOV      r1, #0x45
	LSL      r1, r1, #5
	ADD      r0, r0, r1
	PUSH     {r3, lr}
	LDRB     r1, [r0, #1]
	LDRB     r0, [r0]
	BL       |sub_080089FC|
	POP      {r3, pc}
