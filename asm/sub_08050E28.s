	CODE16
|sub_08050E28|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08050E3E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050E3E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08050E56|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050E56|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050E66|
	BL       |GBARam_Free|
|loc_08050E66|
	POP      {r3, pc}
|sub_08050E68|
|unk_08050E68|
	INCBIN	baserom.gba_0x50e68_0x50e6a.extracted
|sub_08050E6A|
	DCW      0x0804
