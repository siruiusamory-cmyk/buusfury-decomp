	CODE16
|sub_0804ED12|
	LSL      r0, r0, #0
	MOV      r0, #0
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x20]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r0, #1
	BX       lr
|sub_0804ED2C|
|unk_0804ED2C|
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #0
		BX       lr
		MOV r0, #0
		BX       lr
		MOV r0, #0
		BX       lr
		MOV r0, #1
		BX       lr
		BX       lr
