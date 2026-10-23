	CODE16
|sub_0805141E|
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805142A|
	BL       |GBARam_Free|
|loc_0805142A|
	POP      {r3, pc}
|sub_0805142C|
|unk_0805142C|
	INCBIN	baserom.gba_0x5142c_0x5142e.extracted
|sub_0805142E|
	DCW      0x0804
