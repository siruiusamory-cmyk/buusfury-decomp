	CODE16
|sub_08052E72|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052E8E|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052E8E|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052E9C|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052E9C|
	POP      {r3, r4, r5, pc}
|loc_08052E9E|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xbf94,0x0872,0xe454
|loc_08052EAE|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x10]
	PUSH     {r3, lr}
	STR      r1, [r0]
	LDR      r0, [r0, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
|sub_08052EC4|
|unk_08052EC4|
	INCBIN	baserom.gba_0x52ec4_0x52ec6.extracted
