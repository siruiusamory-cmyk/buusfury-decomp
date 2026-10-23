	CODE16
|sub_0804F094|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F09C|
|unk_0804F09C|
		BX       lr
	INCBIN  baserom.gba_0x4f09e_0x4f0a0.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f0a2_0x4f0a4.extracted
		BX       lr
|sub_0804F0A6|
	DCW      0x0000
