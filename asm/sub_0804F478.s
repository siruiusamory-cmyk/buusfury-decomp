	CODE16
|sub_0804F478|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F488|
|unk_0804F488|
		BX       lr
	INCBIN  baserom.gba_0x4f48a_0x4f48c.extracted
		BX       lr
|sub_0804F48E|
	DCW      0x0000
