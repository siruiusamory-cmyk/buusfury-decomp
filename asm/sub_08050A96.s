	CODE16
|sub_08050A96|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050AA2|
	BL       |GBARam_Free|
|loc_08050AA2|
	POP      {r3, pc}
|sub_08050AA4|
|unk_08050AA4|
	INCBIN	baserom.gba_0x50aa4_0x50aa6.extracted
|sub_08050AA6|
	DCW      0x0804
	DCW      0x4a03
