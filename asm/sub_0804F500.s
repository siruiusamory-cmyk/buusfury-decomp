	CODE16
|sub_0804F500|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F518|
|unk_0804F518|
		BX       lr
	INCBIN  baserom.gba_0x4f51a_0x4f51c.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f51e_0x4f520.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f522_0x4f524.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f526_0x4f528.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f52a_0x4f52c.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f52e_0x4f530.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f532_0x4f534.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f536_0x4f538.extracted
		BX       lr
|sub_0804F53A|
	DCW      0x0000
