	CODE16
|sub_08050C14|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050C22|
	BL       |GBARam_Free|
|loc_08050C22|
	POP      {r3, pc}
|sub_08050C24|
|unk_08050C24|
	INCBIN	baserom.gba_0x50c24_0x50c26.extracted
|sub_08050C26|
	DCW      0x0804
