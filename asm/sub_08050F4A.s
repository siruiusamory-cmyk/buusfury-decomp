	CODE16
|sub_08050F4A|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050F5A|
	BL       |GBARam_Free|
|loc_08050F5A|
	POP      {r3, pc}
|sub_08050F5C|
|unk_08050F5C|
	INCBIN	baserom.gba_0x50f5c_0x50f5e.extracted
