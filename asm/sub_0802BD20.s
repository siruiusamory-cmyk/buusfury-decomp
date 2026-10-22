	CODE16
|sub_0802BD20|
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	POP      {r3, pc}
|sub_0802BD32|
|unk_0802BD32|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x1e4
