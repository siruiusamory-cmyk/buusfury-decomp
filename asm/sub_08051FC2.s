	CODE16
|sub_08051FC2|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051FCE|
	BL       |GBARam_Free|
|loc_08051FCE|
	POP      {r3, pc}
|sub_08051FD0|
|unk_08051FD0|
	INCBIN	baserom.gba_0x51fd0_0x51fd2.extracted
|sub_08051FD2|
	DCW      0x0804
	DCW      0x4a03
