	CODE16
|sub_080480AC|
	ADR      r5, |loc_0804815C|
|loc_080480AE|
	MOV      r0, #0xa
	BL       |loc_08048174|
	LDRB     r0, [r5]
	CMP      r0, #0
	BEQ      |loc_080480C8|
|loc_080480BA|
	LDRB     r0, [r5]
	ADD      r5, #1
	BL       |loc_08048174|
	LDRB     r0, [r5]
	CMP      r0, #0
	BNE      |loc_080480BA|
|loc_080480C8|
	LDRB     r0, [r4]
	CMP      r0, #0
	BEQ      |loc_080480DC|
|loc_080480CE|
	LDRB     r0, [r4]
	ADD      r4, #1
	BL       |loc_08048174|
	LDRB     r0, [r4]
	CMP      r0, #0
	BNE      |loc_080480CE|
|loc_080480DC|
	MOV      r0, #0xa
	BL       |loc_08048174|
	POP      {r3, r4, r5}
	POP      {r3}
	MOV      r0, #1
	BX       r3
|sub_080480EA|
|unk_080480EA|
	INCBIN	baserom.gba_0x480ea_0x480ec.extracted
|loc_080480EC|
	DCW      0x0000
	DCW      0x0000,0xf7d0
|sub_080480F2|
	LSL      r6, r6, #1
|loc_080480F4|
	LDR      r1, [r1, #0x64]
	STR      r6, [r6, #0x14]
	LDR      r4, [r5, #0x14]
	MOV      r0, #0x64
	STRB     r7, [r1, #1]
	STRB     r5, [r4, #9]
	STRB     r1, [r4, #0x11]
	LDR      r1, [r5, #0x74]
	LSL      r6, r5, #1
	LSL      r0, r0, #0
	LSL      r2, r0, #0
	LSR      r0, r0, #0x20
	LDR      r4, [r0, #0x14]
	LDR      r6, [r6, #0x14]
	STR      r4, [r4, #0x54]
	TST      r0, r4
	MOV      r0, #0x79
	STR      r2, [r3, #0x54]
	LDR      r2, [r6, #0x74]
	LSL      r0, r0, #0
	STRB     r7, [r1, #0x19]
	STRB     r5, [r4, #9]
	LDR      r6, [r4, #0x44]
	STRB     r7, [r5, #0x1d]
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LDR      r5, [r2, #0x64]
	STR      r4, [r4, #0x54]
	STR      r2, [r6, #0x64]
	LDR      r4, [r5, #0x74]
	LSL      r7, r6, #1
	LSL      r0, r0, #0
	LDR      r1, [r1, #0x64]
	LDRB     r5, [r4, #1]
	STR      r1, [r4, #0x34]
	MOV      r0, #0x74
	STR      r2, [r2, #0x54]
	STRB     r3, [r6, #0x15]
	STRB     r4, [r5, #0x11]
	LSL      r0, r0, #0
	MOV      r0, #0x3a
	STR      r0, [r1, #0x54]
	STRB     r1, [r4, #1]
	LDR      r0, [r4, #0x50]
	LDR      r5, [r4, #0x54]
	STRB     r7, [r5, #9]
	MOV      r0, #0x79
	LDR      r3, [r4, #0x74]
	STRB     r2, [r6, #9]
	STRB     r5, [r6, #1]
	STR      r4, [r6, #0x54]
	LSL      r4, r4, #1
|loc_0804815C|
	LDR      r5, [r2, #0x64]
	LDR      r3, [r5, #0x64]
	STRB     r7, [r5, #0x1d]
	MOV      r0, #0x6e
	LDR      r3, [r6, #0x14]
	LDR      r7, [r4, #0x64]
	LDR      r1, [r4, #0x44]
	LSL      r0, r0, #0
	BX       pc
	LSL      r0, r0, #0
|unk_08048170|
	DCW      0xff1e
	DCW      0xe12f
