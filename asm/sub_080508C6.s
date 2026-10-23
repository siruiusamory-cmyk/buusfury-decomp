	CODE16
|sub_080508C6|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080508D2|
	BL       |GBARam_Free|
|loc_080508D2|
	POP      {r3, pc}
|sub_080508D4|
|unk_080508D4|
	INCBIN	baserom.gba_0x508d4_0x508d6.extracted
