	CODE16
|sub_08050C2A|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050C36|
	BL       |GBARam_Free|
|loc_08050C36|
	POP      {r3, pc}
|sub_08050C38|
|unk_08050C38|
	INCBIN	baserom.gba_0x50c38_0x50c3a.extracted
|sub_08050C3A|
	DCW      0x0804
	DCW      0x4a03
