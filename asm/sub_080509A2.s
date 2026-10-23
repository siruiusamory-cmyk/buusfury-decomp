	CODE16
|sub_080509A2|
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
|sub_080509B2|
	DCW      0x0804
	DCW      0x4a03
