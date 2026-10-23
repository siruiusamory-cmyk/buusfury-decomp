	CODE16
|sub_0804F490|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F498|
|unk_0804F498|
		BX       lr
	INCBIN  baserom.gba_0x4f49a_0x4f49c.extracted
		BX       lr
|sub_0804F49E|
	DCW      0x0000
