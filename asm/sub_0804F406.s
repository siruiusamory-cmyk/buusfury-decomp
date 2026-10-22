	CODE16
|sub_0804F406|
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F410|
|unk_0804F410|
		BX       lr
	INCBIN  baserom.gba_0x4f412_0x4f414.extracted
		BX       lr
