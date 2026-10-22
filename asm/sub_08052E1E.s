	CODE16
|sub_08052E1E|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052E2E|
	BL       |GBARam_Free|
|loc_08052E2E|
	POP      {r3, pc}
|sub_08052E30|
|unk_08052E30|
	INCBIN	baserom.gba_0x52e30_0x52e32.extracted
