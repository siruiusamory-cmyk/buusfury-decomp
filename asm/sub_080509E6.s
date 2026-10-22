	CODE16
|sub_080509E6|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080509F6|
	BL       |GBARam_Free|
|loc_080509F6|
	POP      {r3, pc}
|sub_080509F8|
|unk_080509F8|
	INCBIN	baserom.gba_0x509f8_0x509fa.extracted
