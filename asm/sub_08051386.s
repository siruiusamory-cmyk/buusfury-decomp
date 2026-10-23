	CODE16
|sub_08051386|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051392|
	BL       |GBARam_Free|
|loc_08051392|
	POP      {r3, pc}
|sub_08051394|
|unk_08051394|
	INCBIN	baserom.gba_0x51394_0x51396.extracted
