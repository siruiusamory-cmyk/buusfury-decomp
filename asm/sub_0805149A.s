	CODE16
|sub_0805149A|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080514AA|
	BL       |GBARam_Free|
|loc_080514AA|
	POP      {r3, pc}
|sub_080514AC|
|unk_080514AC|
	INCBIN	baserom.gba_0x514ac_0x514ae.extracted
