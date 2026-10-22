	CODE16
|sub_0804FB6C|
	PUSH     {r3, lr}
	LDR      r2, [r0]
	LDR      r3, [r2, #0x1c]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |sub_0804FB80|
	MOV      r0, #6
	POP      {r3, pc}
