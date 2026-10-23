	CODE16
|sub_080513BA|
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
|sub_080513CA|
	DCW      0x0804
