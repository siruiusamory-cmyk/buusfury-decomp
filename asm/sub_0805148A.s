	CODE16
|sub_0805148A|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051496|
	BL       |GBARam_Free|
|loc_08051496|
	POP      {r3, pc}
|sub_08051498|
|unk_08051498|
	INCBIN	baserom.gba_0x51498_0x5149a.extracted
|sub_0805149A|
	DCW      0x0804
	DCW      0x4a03
