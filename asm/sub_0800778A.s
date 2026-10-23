	CODE16
|sub_0800778A|
	MOV      r0, #0
	STR      r2, [r1, #4]
	BX       lr
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080077A4|
	LDR      r1, [pc, #0xc]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #4]
|loc_080077A4|
	POP      {r3, pc}
	LSL      r0, r0, #0
	LSL      r0, r4, #0x1f
	LSR      r7, r0, #0x20
	ADD      r4, sp, #0x380
	LSR      r4, r0, #0x20
	MOV      r0, #1
	BX       lr
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x2c]
	ADD      r4, r1, #0
	LDR      r6, [r7]
	ADD      r1, r2, #0
	LDR      r2, [r4]
	ADD      r6, #0xc0
	LDR      r5, [r6, #8]
	LDR      r3, [r2, #4]
	ADD      r0, r4, #0
	ADD      r3, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r0, [r6, #8]
	CMP      r0, r5
	BNE      |loc_080077DC|
	ADD      r1, r4, #0
	LDR      r0, [r7]
	BL       |List_Remove1|
|loc_080077DC|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_080077DE|
|unk_080077DE|
	INCBIN	baserom.gba_0x77de_0x77e2.extracted
|sub_080077E2|
	DCW      0x0000
	DCW      0x07e4
	DCW      0x0807
	DCW      0x1960
	DCW      0x0300
