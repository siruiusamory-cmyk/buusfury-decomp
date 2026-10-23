	CODE16
|sub_0804F3A0|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F3A8|
|unk_0804F3A8|
		BX       lr
	INCBIN  baserom.gba_0x4f3aa_0x4f3ac.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f3ae_0x4f3b0.extracted
		BX       lr
|sub_0804F3B2|
	DCW      0x0000
