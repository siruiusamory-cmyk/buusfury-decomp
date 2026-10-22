	CODE16
|sub_0804FBE0|
	PUSH     {r3, lr}
	LDR      r0, [r0, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x10]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
|sub_0804FBF0|
|unk_0804FBF0|
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #0
		BX       lr
