	CODE16
|sub_080510F0|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051106|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051106|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051116|
	BL       |GBARam_Free|
|loc_08051116|
	POP      {r3, pc}
|sub_08051118|
|unk_08051118|
	INCBIN	baserom.gba_0x51118_0x5111a.extracted
