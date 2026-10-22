	CODE16
|sub_08052266|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052276|
	BL       |GBARam_Free|
|loc_08052276|
	POP      {r3, pc}
|sub_08052278|
|unk_08052278|
	INCBIN	baserom.gba_0x52278_0x5227a.extracted
