	CODE16
|sub_08050AA6|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050AB6|
	BL       |GBARam_Free|
|loc_08050AB6|
	POP      {r3, pc}
|sub_08050AB8|
|unk_08050AB8|
	INCBIN	baserom.gba_0x50ab8_0x50aba.extracted
