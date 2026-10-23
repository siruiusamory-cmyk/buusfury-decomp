	CODE16
|sub_0804F304|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F30C|
|unk_0804F30C|
		BX       lr
	INCBIN  baserom.gba_0x4f30e_0x4f310.extracted
		BX       lr
|sub_0804F312|
	DCW      0x0000
