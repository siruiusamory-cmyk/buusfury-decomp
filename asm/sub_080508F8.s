	CODE16
|sub_080508F8|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050906|
	BL       |GBARam_Free|
|loc_08050906|
	POP      {r3, pc}
|sub_08050908|
|unk_08050908|
	INCBIN	baserom.gba_0x50908_0x5090a.extracted
