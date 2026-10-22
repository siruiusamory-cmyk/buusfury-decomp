	CODE16
|sub_0804F2BE|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F2C8|
|unk_0804F2C8|
		BX       lr
	INCBIN  baserom.gba_0x4f2ca_0x4f2cc.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f2ce_0x4f2d0.extracted
		BX       lr
