	CODE16
|sub_080518DE|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080518EA|
	BL       |GBARam_Free|
|loc_080518EA|
	POP      {r3, pc}
|sub_080518EC|
|unk_080518EC|
	INCBIN	baserom.gba_0x518ec_0x518ee.extracted
|sub_080518EE|
	DCW      0x0804
	DCW      0x4a03
