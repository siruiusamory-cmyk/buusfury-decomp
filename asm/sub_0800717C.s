	CODE16
|sub_0800717C|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x3c]
	ADD      r4, r1, #0
	LDR      r6, [r7, #4]
	ADD      r1, r2, #0
	LDR      r2, [r4]
	ADD      r6, #0xc0
	LDR      r5, [r6, #8]
	LDR      r3, [r2, #4]
	ADD      r0, r4, #0
	ADD      r3, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r0, [r6, #8]
	CMP      r0, r5
	BNE      |loc_080071A4|
	ADD      r1, r4, #0
	LDR      r0, [r7, #4]
	BL       |List_Remove1|
|loc_080071A4|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_080071A6|
|unk_080071A6|
	INCBIN	baserom.gba_0x71a6_0x71aa.extracted
