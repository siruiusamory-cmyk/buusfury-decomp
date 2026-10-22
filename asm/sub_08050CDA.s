	CODE16
|sub_08050CDA|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08050CF2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050CF2|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050D02|
	BL       |GBARam_Free|
|loc_08050D02|
	POP      {r3, pc}
|sub_08050D04|
|unk_08050D04|
	INCBIN	baserom.gba_0x50d04_0x50d06.extracted
