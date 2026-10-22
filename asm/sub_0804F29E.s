	CODE16
|sub_0804F29E|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F2B8|
|unk_0804F2B8|
		BX       lr
	INCBIN  baserom.gba_0x4f2ba_0x4f2bc.extracted
		BX       lr
