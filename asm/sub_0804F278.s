	CODE16
|sub_0804F278|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F280|
|unk_0804F280|
		BX       lr
	INCBIN  baserom.gba_0x4f282_0x4f284.extracted
		BX       lr
|sub_0804F286|
	DCW      0x0000
