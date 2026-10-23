	CODE16
|sub_0805098C|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805099A|
	BL       |GBARam_Free|
|loc_0805099A|
	POP      {r3, pc}
|sub_0805099C|
|unk_0805099C|
	INCBIN	baserom.gba_0x5099c_0x5099e.extracted
|sub_0805099E|
	DCW      0x0804
