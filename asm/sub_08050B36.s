	CODE16
|sub_08050B36|
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x18]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x18]
	CMP      r1, r0
	BEQ      |loc_08050B50|
	LDR      r0, [pc, #0x14]
	LDR      r0, [r0, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08050B50|
	LDR      r0, [pc, #0x10]
	STR      r0, [r4]
	POP      {r4, pc}
|loc_08050B56|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x4fbc,0x0805,0xe454
|loc_08050B66|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050B76|
	BL       |GBARam_Free|
|loc_08050B76|
	POP      {r3, pc}
|sub_08050B78|
|unk_08050B78|
	INCBIN	baserom.gba_0x50b78_0x50b7a.extracted
