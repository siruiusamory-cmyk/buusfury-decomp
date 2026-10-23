	CODE16
|sub_08052E22|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052E2E|
	BL       |GBARam_Free|
|loc_08052E2E|
	POP      {r3, pc}
|sub_08052E30|
|unk_08052E30|
	INCBIN	baserom.gba_0x52e30_0x52e32.extracted
|sub_08052E32|
	DCW      0x0804
