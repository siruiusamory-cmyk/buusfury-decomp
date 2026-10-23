	CODE16
|sub_0804F17C|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F184|
|unk_0804F184|
		BX       lr
	INCBIN  baserom.gba_0x4f186_0x4f188.extracted
		BX       lr
|sub_0804F18A|
	DCW      0x0000
