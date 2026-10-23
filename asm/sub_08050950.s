	CODE16
|sub_08050950|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805095E|
	BL       |GBARam_Free|
|loc_0805095E|
	POP      {r3, pc}
|sub_08050960|
|unk_08050960|
	INCBIN	baserom.gba_0x50960_0x50962.extracted
|sub_08050962|
	DCW      0x0804
