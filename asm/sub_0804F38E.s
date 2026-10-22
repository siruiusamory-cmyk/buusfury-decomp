	CODE16
|sub_0804F38E|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F398|
|unk_0804F398|
		BX       lr
	INCBIN  baserom.gba_0x4f39a_0x4f39c.extracted
		BX       lr
