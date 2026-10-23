	CODE16
|sub_0804ECEC|
	PUSH     {r3, lr}
	ADD      r0, r0, r1
	BL       |inc_0x0158_0x143f2| + 0xa980
	POP      {r3, pc}
|sub_0804ECF6|
|unk_0804ECF6|
	INCBIN  baserom.gba_0x4ecf6_0x4ecf8.extracted
		BX       lr
|sub_0804ECFA|
	DCW      0x0000
