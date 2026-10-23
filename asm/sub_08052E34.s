	CODE16
|sub_08052E34|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052E42|
	BL       |GBARam_Free|
|loc_08052E42|
	POP      {r3, pc}
|sub_08052E44|
|unk_08052E44|
	INCBIN	baserom.gba_0x52e44_0x52e46.extracted
|sub_08052E46|
	DCW      0x0804
