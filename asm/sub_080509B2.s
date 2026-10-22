	CODE16
|sub_080509B2|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080509C2|
	BL       |GBARam_Free|
|loc_080509C2|
	POP      {r3, pc}
|sub_080509C4|
|unk_080509C4|
	INCBIN	baserom.gba_0x509c4_0x509c6.extracted
