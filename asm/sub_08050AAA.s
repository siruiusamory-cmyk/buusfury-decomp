	CODE16
|sub_08050AAA|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050AB6|
	BL       |GBARam_Free|
|loc_08050AB6|
	POP      {r3, pc}
|sub_08050AB8|
|unk_08050AB8|
	INCBIN	baserom.gba_0x50ab8_0x50aba.extracted
|sub_08050ABA|
	DCW      0x0804
