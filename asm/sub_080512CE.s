	CODE16
|sub_080512CE|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080512DE|
	BL       |GBARam_Free|
|loc_080512DE|
	POP      {r3, pc}
|sub_080512E0|
|unk_080512E0|
	INCBIN	baserom.gba_0x512e0_0x512e2.extracted
