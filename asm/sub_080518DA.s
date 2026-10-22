	CODE16
|sub_080518DA|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
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
