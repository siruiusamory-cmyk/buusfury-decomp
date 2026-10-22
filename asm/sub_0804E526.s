	CODE16
|sub_0804E526|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0x11
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	BL       |inc_0x0158_0x143f2| + 0xf7cc
	POP      {r3, pc}
|sub_0804E546|
|unk_0804E546|
	INCBIN  baserom.gba_0x4e546_0x4e548.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e54a_0x4e54c.extracted
		BX       lr
