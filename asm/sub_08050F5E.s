	CODE16
|sub_08050F5E|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050F6E|
	BL       |GBARam_Free|
|loc_08050F6E|
	POP      {r3, pc}
|sub_08050F70|
|unk_08050F70|
	INCBIN	baserom.gba_0x50f70_0x50f72.extracted
