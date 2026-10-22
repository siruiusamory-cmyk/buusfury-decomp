	CODE16
|sub_08050D06|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050D16|
	BL       |GBARam_Free|
|loc_08050D16|
	POP      {r3, pc}
|sub_08050D18|
|unk_08050D18|
	INCBIN	baserom.gba_0x50d18_0x50d1a.extracted
