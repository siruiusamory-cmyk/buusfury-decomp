	CODE16
|sub_0804F4B8|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F4C0|
|unk_0804F4C0|
		BX       lr
	INCBIN  baserom.gba_0x4f4c2_0x4f4c4.extracted
		BX       lr
|sub_0804F4C6|
	DCW      0x0000
