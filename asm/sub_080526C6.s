	CODE16
|sub_080526C6|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080526D6|
	BL       |GBARam_Free|
|loc_080526D6|
	POP      {r3, pc}
|sub_080526D8|
|unk_080526D8|
	INCBIN	baserom.gba_0x526d8_0x526da.extracted
