	CODE16
|sub_08050BA4|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08050BBA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050BBA|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08050BD2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050BD2|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08050BEA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050BEA|
	POP      {r3, r4, r5, pc}
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
	BEQ      |loc_08050C0C|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050C0C|
	POP      {r3, r4, r5, pc}
|sub_08050C0E|
|unk_08050C0E|
	INCBIN	baserom.gba_0x50c0e_0x50c12.extracted
|sub_08050C12|
	DCW      0x0804
	DCW      0x4a03
