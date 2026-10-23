	CODE16
|sub_08051F20|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051F36|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051F36|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051F4E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051F4E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051F66|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051F66|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051F7E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051F7E|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051F8E|
	BL       |GBARam_Free|
|loc_08051F8E|
	POP      {r3, pc}
|sub_08051F90|
|unk_08051F90|
	INCBIN	baserom.gba_0x51f90_0x51f92.extracted
|sub_08051F92|
	DCW      0x0804
