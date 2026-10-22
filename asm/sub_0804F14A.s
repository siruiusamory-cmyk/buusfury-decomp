	CODE16
|sub_0804F14A|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F15C|
|unk_0804F15C|
		BX       lr
	INCBIN  baserom.gba_0x4f15e_0x4f160.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f162_0x4f164.extracted
		BX       lr
