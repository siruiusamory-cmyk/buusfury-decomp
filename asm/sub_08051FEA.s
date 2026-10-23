	CODE16
|sub_08051FEA|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051FF6|
	BL       |GBARam_Free|
|loc_08051FF6|
	POP      {r3, pc}
|sub_08051FF8|
|unk_08051FF8|
	INCBIN	baserom.gba_0x51ff8_0x51ffa.extracted
|sub_08051FFA|
	DCW      0x0804
