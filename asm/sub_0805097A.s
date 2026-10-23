	CODE16
|sub_0805097A|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050986|
	BL       |GBARam_Free|
|loc_08050986|
	POP      {r3, pc}
|sub_08050988|
|unk_08050988|
	INCBIN	baserom.gba_0x50988_0x5098a.extracted
|sub_0805098A|
	DCW      0x0804
	DCW      0x4a03
