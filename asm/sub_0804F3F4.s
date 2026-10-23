	CODE16
|sub_0804F3F4|
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_0804F402|
	LDR      r1, [pc, #8]
	STR      r1, [r0]
	BL       |GBARam_Free|
|loc_0804F402|
	POP      {r3, pc}
|sub_0804F404|
|unk_0804F404|
	INCBIN	baserom.gba_0x4f404_0x4f406.extracted
|sub_0804F406|
	DCW      0x0804
