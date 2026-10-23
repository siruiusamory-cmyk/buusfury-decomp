	CODE16
|sub_08050A24|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08050A3A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050A3A|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050A4A|
	BL       |GBARam_Free|
|loc_08050A4A|
	POP      {r3, pc}
|sub_08050A4C|
|unk_08050A4C|
	INCBIN	baserom.gba_0x50a4c_0x50a4e.extracted
|sub_08050A4E|
	DCW      0x0804
