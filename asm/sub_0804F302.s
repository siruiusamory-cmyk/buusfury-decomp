	CODE16
|sub_0804F302|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F30C|
|unk_0804F30C|
		BX       lr
	INCBIN  baserom.gba_0x4f30e_0x4f310.extracted
		BX       lr
