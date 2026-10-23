	CODE16
|sub_0804F59C|
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_0804F5AE|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0804F5AE|
	POP      {r3, pc}
|sub_0804F5B0|
|unk_0804F5B0|
		BX       lr
|sub_0804F5B2|
	DCW      0x0000
