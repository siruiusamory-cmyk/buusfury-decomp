	CODE16
|sub_080517BC|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1c]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r5, #0
	BEQ      |loc_080517DC|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080517DC|
	POP      {r3, r4, r5, pc}
|sub_080517DE|
|unk_080517DE|
	INCBIN	baserom.gba_0x517de_0x517e2.extracted
|sub_080517E2|
	DCW      0x0804
