	CODE16
|sub_08050B8E|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050B9E|
	BL       |GBARam_Free|
|loc_08050B9E|
	POP      {r3, pc}
|sub_08050BA0|
|unk_08050BA0|
	INCBIN	baserom.gba_0x50ba0_0x50ba2.extracted
