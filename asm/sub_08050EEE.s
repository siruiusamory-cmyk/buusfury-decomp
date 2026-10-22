	CODE16
|sub_08050EEE|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08050F06|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050F06|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08050F1E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050F1E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08050F36|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050F36|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050F46|
	BL       |GBARam_Free|
|loc_08050F46|
	POP      {r3, pc}
|sub_08050F48|
|unk_08050F48|
	INCBIN	baserom.gba_0x50f48_0x50f4a.extracted
