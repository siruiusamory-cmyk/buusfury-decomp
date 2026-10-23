	CODE16
|sub_08051FD6|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051FE2|
	BL       |GBARam_Free|
|loc_08051FE2|
	POP      {r3, pc}
|sub_08051FE4|
|unk_08051FE4|
	INCBIN	baserom.gba_0x51fe4_0x51fe6.extracted
|sub_08051FE6|
	DCW      0x0804
	DCW      0x4a03
