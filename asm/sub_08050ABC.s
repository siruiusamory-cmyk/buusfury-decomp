	CODE16
|sub_08050ABC|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08050AD2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050AD2|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050AE2|
	BL       |GBARam_Free|
|loc_08050AE2|
	POP      {r3, pc}
|sub_08050AE4|
|unk_08050AE4|
	INCBIN	baserom.gba_0x50ae4_0x50ae6.extracted
|sub_08050AE6|
	DCW      0x0804
	DCW      0x4a03
