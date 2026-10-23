	CODE16
|sub_08050966|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050972|
	BL       |GBARam_Free|
|loc_08050972|
	POP      {r3, pc}
|sub_08050974|
|unk_08050974|
	INCBIN	baserom.gba_0x50974_0x50976.extracted
|sub_08050976|
	DCW      0x0804
	DCW      0x4a03
