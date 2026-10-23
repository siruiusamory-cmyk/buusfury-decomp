	CODE16
|sub_0804F5E8|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F5F8|
|unk_0804F5F8|
		BX       lr
|sub_0804F5FA|
	DCW      0x0000
