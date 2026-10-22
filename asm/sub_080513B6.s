	CODE16
|sub_080513B6|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080513C6|
	BL       |GBARam_Free|
|loc_080513C6|
	POP      {r3, pc}
|sub_080513C8|
|unk_080513C8|
	INCBIN	baserom.gba_0x513c8_0x513ca.extracted
