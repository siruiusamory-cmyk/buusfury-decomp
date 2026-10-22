	CODE16
|sub_080512BA|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080512CA|
	BL       |GBARam_Free|
|loc_080512CA|
	POP      {r3, pc}
|sub_080512CC|
|unk_080512CC|
	INCBIN	baserom.gba_0x512cc_0x512ce.extracted
