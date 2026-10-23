	CODE16
|sub_08050E6C|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x31c6
	CMP      r5, #0
	BEQ      |loc_08050E82|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050E82|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08050E9A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050E9A|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050EAA|
	BL       |GBARam_Free|
|loc_08050EAA|
	POP      {r3, pc}
|sub_08050EAC|
|unk_08050EAC|
	INCBIN	baserom.gba_0x50eac_0x50eae.extracted
|sub_08050EAE|
	DCW      0x0804
