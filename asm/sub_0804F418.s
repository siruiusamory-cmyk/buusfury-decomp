	CODE16
|sub_0804F418|
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_0804F42A|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x10]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0804F42A|
	POP      {r3, pc}
|sub_0804F42C|
|unk_0804F42C|
		BX       lr
|sub_0804F42E|
	DCW      0x0000
