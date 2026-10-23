	CODE16
|sub_08050C16|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050C22|
	BL       |GBARam_Free|
|loc_08050C22|
	POP      {r3, pc}
|sub_08050C24|
|unk_08050C24|
	INCBIN	baserom.gba_0x50c24_0x50c26.extracted
|sub_08050C26|
	DCW      0x0804
	DCW      0x4a03
