	CODE16
|sub_08050D0A|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050D16|
	BL       |GBARam_Free|
|loc_08050D16|
	POP      {r3, pc}
|sub_08050D18|
|unk_08050D18|
	INCBIN	baserom.gba_0x50d18_0x50d1a.extracted
|sub_08050D1A|
	DCW      0x0804
	DCW      0x4a03
