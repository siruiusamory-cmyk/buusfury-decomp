|sub_080187A8|
	EXPORT |sub_080187A8|
	PUSH     {r3, lr}
	LDR      r2, [r2, #4]
	CMP      r2, #0
	BNE      |sub_080187B4|
	MOV      r0, #0
	POP      {r3, pc}
