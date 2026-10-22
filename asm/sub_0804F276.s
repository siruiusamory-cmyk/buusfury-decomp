	CODE16
|sub_0804F276|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F280|
|unk_0804F280|
		BX       lr
	INCBIN  baserom.gba_0x4f282_0x4f284.extracted
		BX       lr
