	CODE16
|sub_0804ECFC|
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_0804ED0E|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0804ED0E|
	POP      {r3, pc}
|sub_0804ED10|
|unk_0804ED10|
		BX       lr
