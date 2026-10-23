	CODE16
|sub_08051C86|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051C92|
	BL       |GBARam_Free|
|loc_08051C92|
	POP      {r3, pc}
|sub_08051C94|
|unk_08051C94|
	INCBIN	baserom.gba_0x51c94_0x51c96.extracted
|sub_08051C96|
	DCW      0x0804
