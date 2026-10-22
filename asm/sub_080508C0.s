	CODE16
|sub_080508C0|
	BHI      |loc_0805091C|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080508D2|
	BL       |GBARam_Free|
|loc_080508D2|
	POP      {r3, pc}
|sub_080508D4|
|unk_080508D4|
	INCBIN	baserom.gba_0x508d4_0x508d6.extracted
