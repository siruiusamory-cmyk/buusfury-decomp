	CODE16
|sub_08052874|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052882|
	BL       |GBARam_Free|
|loc_08052882|
	POP      {r3, pc}
|sub_08052884|
|unk_08052884|
	INCBIN	baserom.gba_0x52884_0x52886.extracted
|sub_08052886|
	DCW      0x0804
