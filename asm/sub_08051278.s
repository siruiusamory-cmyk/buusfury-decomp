	CODE16
|sub_08051278|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_0805128E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805128E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_080512A6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080512A6|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080512B6|
	BL       |GBARam_Free|
|loc_080512B6|
	POP      {r3, pc}
|sub_080512B8|
|unk_080512B8|
	INCBIN	baserom.gba_0x512b8_0x512ba.extracted
|sub_080512BA|
	DCW      0x0804
	DCW      0x4a03
