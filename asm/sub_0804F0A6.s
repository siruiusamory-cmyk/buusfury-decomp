	CODE16
|sub_0804F0A6|
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
|sub_0804F0C0|
|unk_0804F0C0|
		BX       lr
	INCBIN  baserom.gba_0x4f0c2_0x4f0c4.extracted
		BX       lr
