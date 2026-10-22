	CODE16
|sub_08050C3A|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050C4A|
	BL       |GBARam_Free|
|loc_08050C4A|
	POP      {r3, pc}
|sub_08050C4C|
|unk_08050C4C|
	INCBIN	baserom.gba_0x50c4c_0x50c4e.extracted
