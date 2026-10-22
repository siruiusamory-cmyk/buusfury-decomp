	CODE16
|sub_0805099E|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080509AE|
	BL       |GBARam_Free|
|loc_080509AE|
	POP      {r3, pc}
|sub_080509B0|
|unk_080509B0|
	INCBIN	baserom.gba_0x509b0_0x509b2.extracted
