	CODE16
|sub_08052A12|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052A1E|
	BL       |GBARam_Free|
|loc_08052A1E|
	POP      {r3, pc}
|sub_08052A20|
|unk_08052A20|
	INCBIN	baserom.gba_0x52a20_0x52a22.extracted
|sub_08052A22|
	DCW      0x0804
