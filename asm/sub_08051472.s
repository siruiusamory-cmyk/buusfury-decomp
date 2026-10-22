	CODE16
|sub_08051472|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051482|
	BL       |GBARam_Free|
|loc_08051482|
	POP      {r3, pc}
|sub_08051484|
|unk_08051484|
	INCBIN	baserom.gba_0x51484_0x51486.extracted
