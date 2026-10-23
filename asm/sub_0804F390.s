	CODE16
|sub_0804F390|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F398|
|unk_0804F398|
		BX       lr
	INCBIN  baserom.gba_0x4f39a_0x4f39c.extracted
		BX       lr
|sub_0804F39E|
	DCW      0x0000
