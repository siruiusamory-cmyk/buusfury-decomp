	CODE16
|sub_0803EB98|
	ADD      r1, r0, #0
	ADD      r1, #0x50
	LDRB     r2, [r1, #2]
	ADD      r2, #0xff
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x18
	STRB     r2, [r1, #2]
	BNE      |loc_0803EBC2|
	LDRB     r2, [r0, #0x10]
	MOV      r3, #5
	ORR      r2, r3
	STRB     r2, [r0, #0x10]
	ADD      r0, #0x40
	LDRB     r2, [r0, #0xe]
	LSL      r2, r2, #0x1c
	LSR      r2, r2, #0x1c
	STRB     r2, [r1, #2]
	LDRB     r1, [r0, #0xa]
	MOV      r2, #4
	ORR      r1, r2
	STRB     r1, [r0, #0xa]
|loc_0803EBC2|
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_0803E4E4|
	ADD      r2, r4, #0
	ADD      r2, #0x50
	LDRB     r1, [r2, #0xe]
	ADD      r0, r4, #0
	ADD      r0, #0x40
	CMP      r1, #0
	BEQ      |loc_0803EBDC|
	STRB     r1, [r0, #0xe]
|loc_0803EBDC|
	LDR      r1, [pc, #0x1c0]
	STR      r1, [r4, #0x54]
	LDRB     r1, [r0, #0xe]
	LSL      r1, r1, #0x1c
	LSR      r1, r1, #0x1c
	STRB     r1, [r2, #2]
	LDRB     r1, [r0, #0xa]
	LSR      r1, r1, #2
	LSL      r1, r1, #2
	ADD      r1, #2
	STRB     r1, [r0, #0xa]
	POP      {r4, pc}
|sub_0803EBF4|
|unk_0803EBF4|
	INCBIN	baserom.gba_0x3ebf4_0x3ebf8.extracted
|sub_0803EBF8|
	DCW      0x1c01
	DCW      0x3150
