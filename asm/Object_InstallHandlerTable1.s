	CODE16
|Object_InstallHandlerTable1|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x20]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #4]
	CMP      r0, #0
	BEQ      |loc_08050D4C|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08050D4C|
	CMP      r5, #0
	BEQ      |loc_08050D56|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050D56|
	POP      {r3, r4, r5, pc}
|sub_08050D58|
|unk_08050D58|
	INCBIN	baserom.gba_0x50d58_0x50d5a.extracted
|sub_08050D5A|
	DCW      0x0804
	DCW      0x4a03
