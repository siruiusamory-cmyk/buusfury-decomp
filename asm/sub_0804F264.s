	CODE16
|sub_0804F264|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F274|
|unk_0804F274|
		BX       lr
|sub_0804F276|
	DCW      0x0000
