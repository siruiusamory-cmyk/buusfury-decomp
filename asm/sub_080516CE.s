	CODE16
|sub_080516CE|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_080516EA|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080516EA|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080516F8|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080516F8|
	POP      {r3, r4, r5, pc}
|loc_080516FA|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xa7a4,0x0875,0xe454
|loc_0805170A|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051726|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051726|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051734|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051734|
	POP      {r3, r4, r5, pc}
|loc_08051736|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x81e4,0x0875,0xe454
|loc_08051746|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_0805175E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805175E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08051776|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051776|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_0805178E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805178E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_080517A6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080517A6|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080517B6|
	BL       |GBARam_Free|
|loc_080517B6|
	POP      {r3, pc}
|sub_080517B8|
|unk_080517B8|
	INCBIN	baserom.gba_0x517b8_0x517ba.extracted
