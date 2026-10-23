	CODE16
|sub_080509FC|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050A0A|
	BL       |GBARam_Free|
|loc_08050A0A|
	POP      {r3, pc}
|sub_08050A0C|
|unk_08050A0C|
	INCBIN	baserom.gba_0x50a0c_0x50a0e.extracted
|sub_08050A0E|
	DCW      0x0804
