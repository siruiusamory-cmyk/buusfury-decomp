	CODE16
|sub_0804F42E|
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
|sub_0804F448|
|unk_0804F448|
		BX       lr
	INCBIN  baserom.gba_0x4f44a_0x4f44c.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f44e_0x4f450.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f452_0x4f454.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f456_0x4f458.extracted
		BX       lr
