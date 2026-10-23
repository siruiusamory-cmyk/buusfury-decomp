	CODE16
|sub_08050AFE|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050B0A|
	BL       |GBARam_Free|
|loc_08050B0A|
	POP      {r3, pc}
|sub_08050B0C|
|unk_08050B0C|
	INCBIN	baserom.gba_0x50b0c_0x50b0e.extracted
|sub_08050B0E|
	DCW      0x0804
