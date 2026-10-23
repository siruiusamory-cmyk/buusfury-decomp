	CODE16
|sub_0804F288|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F290|
|unk_0804F290|
		BX       lr
	INCBIN  baserom.gba_0x4f292_0x4f294.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f296_0x4f298.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f29a_0x4f29c.extracted
		BX       lr
|sub_0804F29E|
	DCW      0x0000
