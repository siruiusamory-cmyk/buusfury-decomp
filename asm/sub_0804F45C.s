	CODE16
|sub_0804F45C|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F474|
|unk_0804F474|
		BX       lr
|sub_0804F476|
	DCW      0x0000
