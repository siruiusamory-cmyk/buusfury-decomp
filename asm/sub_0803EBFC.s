	CODE16
|sub_0803EBFC|
	PUSH     {lr}
	LDRB     r2, [r1, #2]
	ADD      r2, #0xff
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x18
	STRB     r2, [r1, #2]
	BNE      |loc_0803EC0E|
	BL       |loc_0803E4E4|
|loc_0803EC0E|
	POP      {pc}
	ADD      r1, r0, #0
	ADD      r1, #0x50
	LDRB     r2, [r1, #0xe]
	STRB     r2, [r1, #2]
	LDR      r1, [pc, #0x188]
	STR      r1, [r0, #0x54]
	ADD      r0, #0x40
	LDRB     r1, [r0, #0xa]
	LSR      r1, r1, #2
	LSL      r1, r1, #2
	ADD      r1, #2
	STRB     r1, [r0, #0xa]
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	STRB     r1, [r4, #4]
	ADD      r0, r1, #0
	LDR      r1, [pc, #0x174]
	BL       |inc_0x046118_0x049114| + 0xd40
	STRH     r0, [r4, #6]
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	BL       |loc_0803E4E4|
	LDR      r0, [pc, #0x148]
	LDR      r1, [pc, #0x160]
	SUB      r0, #4
	LDR      r4, [r0]
	ADD      r5, #0x50
	LDRB     r0, [r5, #0xe]
	STRB     r0, [r4, #4]
	BL       |inc_0x046118_0x049114| + 0xd40
	STRH     r0, [r4, #6]
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_0803E4E4|
	ADD      r0, r4, #0
	ADD      r0, #0x50
	LDRB     r1, [r0, #8]
	MOV      r2, #0x11
	AND      r1, r2
	BEQ      |loc_0803EC72|
	MOV      r1, #0
	STRB     r1, [r0, #1]
|loc_0803EC72|
	LDRB     r1, [r0, #0xe]
	LSL      r2, r1, #0x1c
	BEQ      |loc_0803EC7E|
	LSL      r2, r1, #0x1c
	LSR      r2, r2, #0x1c
	STRB     r2, [r0]
|loc_0803EC7E|
	LSL      r0, r1, #0x18
	LSR      r2, r0, #0x1c
	ADD      r0, r4, #0
	ADD      r0, #0x40
	CMP      r2, #0
	BEQ      |loc_0803EC8E|
	LSR      r1, r1, #4
	STRB     r1, [r0, #0xf]
|loc_0803EC8E|
	LDR      r1, [pc, #0x11c]
	MOV      r2, #1
	STR      r1, [r4, #0x54]
	LDRB     r1, [r0, #0xa]
	ORR      r1, r2
	STRB     r1, [r0, #0xa]
	ADD      r0, r4, #0
	BL       |Math_ScaleByTable1|
	POP      {r4, pc}
|sub_0803ECA2|
|unk_0803ECA2|
	INCBIN	baserom.gba_0x3eca2_0x3eca6.extracted
