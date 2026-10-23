	CODE16
|sub_08050B10|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050B1E|
	BL       |GBARam_Free|
|loc_08050B1E|
	POP      {r3, pc}
|sub_08050B20|
|unk_08050B20|
	INCBIN	baserom.gba_0x50b20_0x50b22.extracted
|sub_08050B22|
	DCW      0x0804
