	CODE16
|sub_080527AA|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_080527C2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080527C2|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080527D2|
	BL       |GBARam_Free|
|loc_080527D2|
	POP      {r3, pc}
|sub_080527D4|
|unk_080527D4|
	INCBIN	baserom.gba_0x527d4_0x527d6.extracted
