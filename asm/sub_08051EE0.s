	CODE16
|sub_08051EE0|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051EEE|
	BL       |GBARam_Free|
|loc_08051EEE|
	POP      {r3, pc}
|sub_08051EF0|
|unk_08051EF0|
	INCBIN	baserom.gba_0x51ef0_0x51ef2.extracted
|sub_08051EF2|
	DCW      0x0804
