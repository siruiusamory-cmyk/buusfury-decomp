	CODE16
|sub_08050AEA|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050AF6|
	BL       |GBARam_Free|
|loc_08050AF6|
	POP      {r3, pc}
|sub_08050AF8|
|unk_08050AF8|
	INCBIN	baserom.gba_0x50af8_0x50afa.extracted
|sub_08050AFA|
	DCW      0x0804
	DCW      0x4a03
