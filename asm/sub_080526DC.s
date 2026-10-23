	CODE16
|sub_080526DC|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r0, #0xff
	ADD      r0, #0x8d
	LDR      r0, [r0]
	ADD      r5, r1, #0
	CMP      r0, #0
	BEQ      |loc_080526F8|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080526F8|
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeadc
	CMP      r5, #0
	BEQ      |loc_0805270A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805270A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052726|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052726|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052734|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052734|
	POP      {r3, r4, r5, pc}
|loc_08052736|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x81ec,0x0875,0xe454
|loc_08052746|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052762|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052762|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052770|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052770|
	POP      {r3, r4, r5, pc}
|loc_08052772|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xea48,0x0874,0xe454
|loc_08052782|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052792|
	BL       |GBARam_Free|
|loc_08052792|
	POP      {r3, pc}
|sub_08052794|
|unk_08052794|
	INCBIN	baserom.gba_0x52794_0x52796.extracted
|sub_08052796|
	DCW      0x0804
