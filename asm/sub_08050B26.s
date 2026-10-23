	CODE16
|sub_08050B26|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050B32|
	BL       |GBARam_Free|
|loc_08050B32|
	POP      {r3, pc}
|sub_08050B34|
|unk_08050B34|
	INCBIN	baserom.gba_0x50b34_0x50b36.extracted
|sub_08050B36|
	DCW      0x0804
