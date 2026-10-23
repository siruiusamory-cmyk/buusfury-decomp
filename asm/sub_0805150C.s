	CODE16
|sub_0805150C|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08051522|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051522|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x20]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #4]
	CMP      r0, #0
	BEQ      |loc_08051540|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08051540|
	CMP      r5, #0
	BEQ      |loc_0805154A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805154A|
	POP      {r3, r4, r5, pc}
|sub_0805154C|
|unk_0805154C|
	INCBIN	baserom.gba_0x5154c_0x5154e.extracted
|sub_0805154E|
	DCW      0x0804
