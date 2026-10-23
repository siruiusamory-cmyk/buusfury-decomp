	CODE16
|sub_0804F340|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F350|
|unk_0804F350|
		BX       lr
|sub_0804F352|
	DCW      0x0000
