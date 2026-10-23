	CODE16
|sub_08050B24|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050B32|
	BL       |GBARam_Free|
|loc_08050B32|
	POP      {r3, pc}
|sub_08050B34|
|unk_08050B34|
	INCBIN	baserom.gba_0x50b34_0x50b36.extracted
|sub_08050B36|
	DCW      0x0804
