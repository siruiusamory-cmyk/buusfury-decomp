	CODE16
|sub_0800DE94|
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	BL       |sub_0800EE78|
	POP      {r3, pc}
