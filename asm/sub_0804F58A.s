	CODE16
|sub_0804F58A|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F594|
|unk_0804F594|
		BX       lr
	INCBIN  baserom.gba_0x4f596_0x4f598.extracted
		BX       lr
