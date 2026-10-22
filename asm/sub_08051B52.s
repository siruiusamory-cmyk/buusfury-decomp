	CODE16
|sub_08051B52|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08051B6A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051B6A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051B82|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051B82|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051B9A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051B9A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051BB2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051BB2|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051BCA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051BCA|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051BDA|
	BL       |GBARam_Free|
|loc_08051BDA|
	POP      {r3, pc}
|sub_08051BDC|
|unk_08051BDC|
	INCBIN	baserom.gba_0x51bdc_0x51bde.extracted
