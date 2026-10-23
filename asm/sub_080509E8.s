	CODE16
|sub_080509E8|
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
|sub_080509FA|
	DCW      0x0804
	DCW      0x4a03
