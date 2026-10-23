	CODE16
|sub_0805185A|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051866|
	BL       |GBARam_Free|
|loc_08051866|
	POP      {r3, pc}
|sub_08051868|
|unk_08051868|
	INCBIN	baserom.gba_0x51868_0x5186a.extracted
|sub_0805186A|
	DCW      0x0804
