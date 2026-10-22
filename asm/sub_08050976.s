	CODE16
|sub_08050976|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050986|
	BL       |GBARam_Free|
|loc_08050986|
	POP      {r3, pc}
|sub_08050988|
|unk_08050988|
	INCBIN	baserom.gba_0x50988_0x5098a.extracted
