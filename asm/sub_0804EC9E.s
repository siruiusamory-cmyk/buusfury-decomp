	CODE16
|sub_0804EC9E|
	LSL      r0, r0, #0
	MOV      r2, #0x45
	LSL      r2, r2, #3
	PUSH     {r3, lr}
	ADD      r0, r0, r2
	BL       |inc_0x0158_0x143f2| + 0xa944
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r2, #0x47
	LSL      r2, r2, #3
	PUSH     {r3, lr}
	ADD      r0, r0, r2
	BL       |inc_0x0158_0x143f2| + 0xa8f2
	POP      {r3, pc}
|sub_0804ECBE|
|unk_0804ECBE|
	INCBIN  baserom.gba_0x4ecbe_0x4ecc0.extracted
		BX       lr
