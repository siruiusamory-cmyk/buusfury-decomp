	CODE16
|sub_080518C8|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080518D6|
	BL       |GBARam_Free|
|loc_080518D6|
	POP      {r3, pc}
|sub_080518D8|
|unk_080518D8|
	INCBIN	baserom.gba_0x518d8_0x518da.extracted
|sub_080518DA|
	DCW      0x0804
