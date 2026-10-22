	CODE16
|sub_0804ECC2|
	LSL      r0, r0, #0
	MOV      r2, #0x45
	LSL      r2, r2, #3
	PUSH     {r3, lr}
	ADD      r0, r0, r2
	BL       |inc_0x0158_0x143f2| + 0xa8f2
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r1, #0x47
	LSL      r1, r1, #3
	PUSH     {r3, lr}
	ADD      r0, r0, r1
	BL       |inc_0x0158_0x143f2| + 0xa980
	POP      {r3, pc}
|sub_0804ECE2|
|unk_0804ECE2|
	INCBIN  baserom.gba_0x4ece2_0x4ece4.extracted
		BX       lr
