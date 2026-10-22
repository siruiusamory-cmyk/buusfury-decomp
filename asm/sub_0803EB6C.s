	CODE16
|sub_0803EB6C|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_0803E4E4|
	ADD      r0, r4, #0
	ADD      r0, #0x50
	LDRB     r1, [r0, #8]
	MOV      r2, #0x11
	AND      r1, r2
	BEQ      |loc_0803EB94|
	LDRB     r0, [r0, #0xe]
	MOV      r1, #4
	LSL      r0, r0, #0x16
	STR      r0, [r4]
	LDRB     r0, [r4, #0x10]
	BIC      r0, r1
	STRB     r0, [r4, #0x10]
	LDRB     r0, [r4, #0x11]
	BIC      r0, r1
	STRB     r0, [r4, #0x11]
|loc_0803EB94|
	POP      {r4, pc}
|sub_0803EB96|
|unk_0803EB96|
	INCBIN	baserom.gba_0x3eb96_0x3eb98.extracted
