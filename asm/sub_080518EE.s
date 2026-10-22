	CODE16
|sub_080518EE|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080518FE|
	BL       |GBARam_Free|
|loc_080518FE|
	POP      {r3, pc}
|sub_08051900|
|unk_08051900|
	INCBIN	baserom.gba_0x51900_0x51902.extracted
