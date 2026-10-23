	CODE16
|sub_08051C70|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051C7E|
	BL       |GBARam_Free|
|loc_08051C7E|
	POP      {r3, pc}
|sub_08051C80|
|unk_08051C80|
	INCBIN	baserom.gba_0x51c80_0x51c82.extracted
|sub_08051C82|
	DCW      0x0804
