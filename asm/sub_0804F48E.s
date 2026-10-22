	CODE16
|sub_0804F48E|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F498|
|unk_0804F498|
		BX       lr
	INCBIN  baserom.gba_0x4f49a_0x4f49c.extracted
		BX       lr
