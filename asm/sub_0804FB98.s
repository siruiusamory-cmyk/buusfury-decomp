	CODE16
|sub_0804FB98|
	PUSH     {r3, lr}
	LDR      r2, [r0]
	LDR      r3, [r2, #0x1c]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	LDR      r0, [r0, #0x20]
	BX       lr
|sub_0804FBAC|
|unk_0804FBAC|
		LDR r0, [r0, #0x30]
		BX       lr
