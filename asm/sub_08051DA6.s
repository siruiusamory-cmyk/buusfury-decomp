	CODE16
|sub_08051DA6|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051DC2|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051DC2|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051DD0|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051DD0|
	POP      {r3, r4, r5, pc}
|loc_08051DD2|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x4974,0x0875,0xe454
|loc_08051DE2|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	MOV      r1, #0
	ADD      r4, r0, #0
	ADD      r0, #0x18
	BL       |inc_0x03d784_0x041118| + 0x1e08
	LDR      r0, [pc, #0x24]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051E06|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051E06|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051E14|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051E14|
	POP      {r3, r4, r5, pc}
|loc_08051E16|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x7ae4,0x0875,0xe454
|loc_08051E26|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051E42|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051E42|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051E50|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051E50|
	POP      {r3, r4, r5, pc}
|loc_08051E52|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xa73c,0x0875,0xe454
|loc_08051E62|
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x18]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x18]
	CMP      r1, r0
	BEQ      |loc_08051E7C|
	LDR      r0, [pc, #0x14]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051E7C|
	LDR      r0, [pc, #0x10]
	STR      r0, [r4]
	POP      {r4, pc}
|loc_08051E82|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x9c60,0x0871,0xe454
|loc_08051E92|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08051EAA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051EAA|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0xc]
	ADD      r5, r1, #0
	BL       |inc_0x0158_0x143f2| + 0x10c42
	LDR      r0, [pc, #0xc]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051EC6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051EC6|
	POP      {r3, r4, r5, pc}
|sub_08051EC8|
|unk_08051EC8|
	INCBIN	baserom.gba_0x51ec8_0x51eca.extracted
