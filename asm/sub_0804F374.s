	CODE16
|sub_0804F374|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F37C|
|unk_0804F37C|
		BX       lr
	INCBIN  baserom.gba_0x4f37e_0x4f380.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f382_0x4f384.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f386_0x4f388.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f38a_0x4f38c.extracted
		BX       lr
|sub_0804F38E|
	DCW      0x0000
