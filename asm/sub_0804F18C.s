	CODE16
|sub_0804F18C|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F19C|
|unk_0804F19C|
		BX       lr
	INCBIN  baserom.gba_0x4f19e_0x4f1a0.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f1a2_0x4f1a4.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f1a6_0x4f1a8.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f1aa_0x4f1ac.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f1ae_0x4f1b0.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f1b2_0x4f1b4.extracted
		BX       lr
|sub_0804F1B6|
	DCW      0x0000
