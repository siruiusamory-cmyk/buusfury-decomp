	CODE16
|sub_08051EF4|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08051F0A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051F0A|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051F1A|
	BL       |GBARam_Free|
|loc_08051F1A|
	POP      {r3, pc}
|sub_08051F1C|
|unk_08051F1C|
	INCBIN	baserom.gba_0x51f1c_0x51f1e.extracted
|sub_08051F1E|
	DCW      0x0804
