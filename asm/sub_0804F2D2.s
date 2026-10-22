	CODE16
|sub_0804F2D2|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F2DC|
|unk_0804F2DC|
		BX       lr
	INCBIN  baserom.gba_0x4f2de_0x4f2e0.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f2e2_0x4f2e4.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f2e6_0x4f2e8.extracted
		BX       lr
