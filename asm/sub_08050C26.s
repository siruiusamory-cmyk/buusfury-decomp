	CODE16
|sub_08050C26|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050C36|
	BL       |GBARam_Free|
|loc_08050C36|
	POP      {r3, pc}
|sub_08050C38|
|unk_08050C38|
	INCBIN	baserom.gba_0x50c38_0x50c3a.extracted
