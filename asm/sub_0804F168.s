	CODE16
|sub_0804F168|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F170|
|unk_0804F170|
		BX       lr
	INCBIN  baserom.gba_0x4f172_0x4f174.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f176_0x4f178.extracted
		BX       lr
|sub_0804F17A|
	DCW      0x0000
