	CODE16
|sub_08051ECA|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051EDA|
	BL       |GBARam_Free|
|loc_08051EDA|
	POP      {r3, pc}
|sub_08051EDC|
|unk_08051EDC|
	INCBIN	baserom.gba_0x51edc_0x51ede.extracted
