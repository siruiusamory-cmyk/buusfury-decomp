	CODE16
|sub_0804F0D4|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F0DC|
|unk_0804F0DC|
		BX       lr
	INCBIN  baserom.gba_0x4f0de_0x4f0e0.extracted
		BX       lr
|sub_0804F0E2|
	DCW      0x0000
