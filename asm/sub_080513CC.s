	CODE16
|sub_080513CC|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_080513E6|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080513E6|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080513F4|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080513F4|
	POP      {r3, r4, r5, pc}
|loc_080513F6|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x6b64,0x0875,0xe454
|loc_08051406|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051416|
	BL       |GBARam_Free|
|loc_08051416|
	POP      {r3, pc}
|sub_08051418|
|unk_08051418|
	INCBIN	baserom.gba_0x51418_0x5141a.extracted
|sub_0805141A|
	DCW      0x0804
	DCW      0x4a03
