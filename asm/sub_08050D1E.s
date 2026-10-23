	CODE16
|sub_08050D1E|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050D2A|
	BL       |GBARam_Free|
|loc_08050D2A|
	POP      {r3, pc}
|sub_08050D2C|
|unk_08050D2C|
	INCBIN	baserom.gba_0x50d2c_0x50d2e.extracted
|sub_08050D2E|
	DCW      0x0804
