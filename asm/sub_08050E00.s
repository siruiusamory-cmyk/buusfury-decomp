	CODE16
|sub_08050E00|
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
	BEQ      |loc_08050E20|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050E20|
	POP      {r3, r4, r5, pc}
|sub_08050E22|
|unk_08050E22|
	INCBIN	baserom.gba_0x50e22_0x50e26.extracted
|sub_08050E26|
	DCW      0x0804
