	CODE16
|sub_08052860|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805286E|
	BL       |GBARam_Free|
|loc_0805286E|
	POP      {r3, pc}
|sub_08052870|
|unk_08052870|
	INCBIN	baserom.gba_0x52870_0x52872.extracted
|sub_08052872|
	DCW      0x0804
