	CODE16
|sub_0803A898|
	PUSH     {r3, lr}
	MOV      r2, #0
	STRB     r2, [r0, #0xc]
	STRB     r2, [r0, #0xd]
	LDR      r2, [r0]
	LDR      r3, [r2, #8]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
