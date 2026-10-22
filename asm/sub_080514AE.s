	CODE16
|sub_080514AE|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_080514C6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080514C6|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_080514DE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080514DE|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_080514F6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080514F6|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051506|
	BL       |GBARam_Free|
|loc_08051506|
	POP      {r3, pc}
|sub_08051508|
|unk_08051508|
	INCBIN	baserom.gba_0x51508_0x5150a.extracted
