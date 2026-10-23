	CODE16
|sub_0804F314|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F31C|
|unk_0804F31C|
		BX       lr
	INCBIN  baserom.gba_0x4f31e_0x4f320.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f322_0x4f324.extracted
		BX       lr
|sub_0804F326|
	DCW      0x0000
