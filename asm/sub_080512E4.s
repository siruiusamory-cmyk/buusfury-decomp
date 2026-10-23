	CODE16
|sub_080512E4|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_080512FA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080512FA|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08051312|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051312|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_0805132A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805132A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051342|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051342|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_0805135A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805135A|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805136A|
	BL       |GBARam_Free|
|loc_0805136A|
	POP      {r3, pc}
|sub_0805136C|
|unk_0805136C|
	INCBIN	baserom.gba_0x5136c_0x5136e.extracted
|sub_0805136E|
	DCW      0x0804
	DCW      0x4a03
