	CODE16
|sub_08050B7C|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050B8A|
	BL       |GBARam_Free|
|loc_08050B8A|
	POP      {r3, pc}
|sub_08050B8C|
|unk_08050B8C|
	INCBIN	baserom.gba_0x50b8c_0x50b8e.extracted
|sub_08050B8E|
	DCW      0x0804
