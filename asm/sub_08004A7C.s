	CODE16
|sub_08004A7C|
	PUSH     {r3, lr}
	LDRB     r1, [r0, #1]
	LDRB     r0, [r0]
	BL       |sub_080089FC|
	POP      {r3, pc}
