	CODE16
|sub_080524F8|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052506|
	BL       |GBARam_Free|
|loc_08052506|
	POP      {r3, pc}
|sub_08052508|
|unk_08052508|
	INCBIN	baserom.gba_0x52508_0x5250a.extracted
|sub_0805250A|
	DCW      0x0804
