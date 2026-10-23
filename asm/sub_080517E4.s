	CODE16
|sub_080517E4|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_080517FA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080517FA|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051812|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051812|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_0805182A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805182A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08051842|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051842|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051852|
	BL       |GBARam_Free|
|loc_08051852|
	POP      {r3, pc}
|sub_08051854|
|unk_08051854|
	INCBIN	baserom.gba_0x51854_0x51856.extracted
|sub_08051856|
	DCW      0x0804
	DCW      0x4a03
