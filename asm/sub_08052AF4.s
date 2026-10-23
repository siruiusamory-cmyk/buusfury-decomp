	CODE16
|sub_08052AF4|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08052B0A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052B0A|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052B1A|
	BL       |GBARam_Free|
|loc_08052B1A|
	POP      {r3, pc}
|sub_08052B1C|
|unk_08052B1C|
	INCBIN	baserom.gba_0x52b1c_0x52b1e.extracted
|sub_08052B1E|
	DCW      0x0804
