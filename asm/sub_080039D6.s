	CODE16
|sub_080039D6|
	LSR      r5, r0, #0x20
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	CMP      r3, #0x5c
	LSL      r0, r0, #0xc
	LSL      r5, r0, #0x11
	LSL      r0, r0, #0
	PUSH     {r4}
	LDR      r1, [r0]
	MOV      r3, #0x68
	SUB      r1, #1
	LSL      r2, r1, #2
	ADD      r2, r2, r0
	STR      r1, [r0]
	LDR      r4, [r2, #4]
	LDR      r2, [pc, #0x24c]
	MUL      r3, r4
	LDR      r2, [r2, #0x14]
	ADD      r2, r3, r2
	MOV      r3, #0x9f
	LSL      r3, r3, #3
	ADD      r2, r2, r3
	ADD      r2, #0x2c
	LDRH     r2, [r2]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	POP      {r4}
	BX       lr
	LDR      r2, [r0]
	MOV      r3, #0x68
	SUB      r2, #1
	LSL      r1, r2, #2
	STR      r2, [r0]
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r2, [r0, #4]
	LDR      r0, [pc, #0x214]
	MUL      r2, r3
	LDR      r0, [r0, #0x14]
	ADD      r0, r2, r0
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r0, r0, r2
	ADD      r0, #0x2c
	LDRH     r2, [r0]
	ADD      r1, r2, r1
	LSL      r1, r1, #0x10
	LSR      r1, r1, #0x10
|loc_08003A44|
	STRH     r1, [r0]
	LDRH     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08003A44|
	BX       lr
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	BL       |loc_080001C6|
	ADD      r0, #0xff
	ADD      r0, #0xa9
	LSL      r1, r4, #0xa
	STR      r1, [r0]
	POP      {r4, pc}
|sub_08003A74|
|unk_08003A74|
	INCBIN	baserom.gba_0x3a74_0x3b12.extracted
