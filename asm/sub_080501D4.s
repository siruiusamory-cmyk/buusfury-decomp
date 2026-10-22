	CODE16
|sub_080501D4|
	PUSH     {r3, lr}
	MOV      r1, #1
	BL       |inc_0x351c0_0x3d4d0| + 0x361c
	POP      {r3, pc}
|sub_080501DE|
|unk_080501DE|
	INCBIN  baserom.gba_0x501de_0x501e0.extracted
		BX       lr
