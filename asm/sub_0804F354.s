	CODE16
|sub_0804F354|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F36C|
|unk_0804F36C|
		BX       lr
	INCBIN  baserom.gba_0x4f36e_0x4f370.extracted
		BX       lr
|sub_0804F372|
	DCW      0x0000
