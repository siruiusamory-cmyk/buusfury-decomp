	CODE16
|sub_0804F2A0|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F2B8|
|unk_0804F2B8|
		BX       lr
	INCBIN  baserom.gba_0x4f2ba_0x4f2bc.extracted
		BX       lr
|sub_0804F2BE|
	DCW      0x0000
