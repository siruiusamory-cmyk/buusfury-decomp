	CODE16
|sub_08050D5A|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050D6A|
	BL       |GBARam_Free|
|loc_08050D6A|
	POP      {r3, pc}
|sub_08050D6C|
|unk_08050D6C|
	INCBIN	baserom.gba_0x50d6c_0x50d6e.extracted
