	CODE16
|sub_080248DC|
	PUSH     {r4}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	LDR      r4, [pc, #0x90]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	LDR      r2, [r0, #0x18]
	LDR      r2, [r2, #4]
	STR      r2, [r1]
	LDR      r3, [r0, #0x38]
	AND      r2, r4
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x3c]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x18]
	LDR      r2, [pc, #0x34]
	LDR      r4, [pc, #0x40]
	LDR      r3, [r3, #8]
	LDRH     r2, [r2, #2]
	SUB      r3, r3, r4
	ASR      r3, r3, #5
	ADD      r2, r2, r3
	LDR      r3, [r1, #4]
	LSL      r2, r2, #0x16
	LSR      r3, r3, #0xa
	LSL      r3, r3, #0xa
	LSR      r2, r2, #0x16
	ORR      r2, r3
	STR      r2, [r1, #4]
	LDRB     r0, [r0, #8]
	MOV      r3, #3
	LSL      r3, r3, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r2, r3
	ORR      r0, r2
	STR      r0, [r1, #4]
	POP      {r4}
	MOV      r0, #0
	BX       lr
|sub_08024940|
	DCW      0xbfcc
	DCW      0x0804,0x2fb8,0x0300,0xc394,0x0872,0x0000,0x0601,0xc3b8
	DCW      0x0872,0xd6b8,0x0872,0xffff,0x0000,0x9680,0x0804,0xe454
	DCW      0x0804,0x1c34,0x0300,0x80a8,0x086b,0xcccd,0x424c,0x0f90
	DCW      0x0300,0xffff
|sub_08024976|
|unk_08024976|
	INCBIN  baserom.gba_0x24976_0x24978.extracted
		PUSH {r3, r4, r5, lr}
	LDR      r4, [pc, #0xa0]
	LDR      r5, [pc, #0x98]
	CMP      r1, #0xa
	LDRB     r3, [r4]
	BEQ      |sub_080249B4|
	CMP      r1, #0xb
	BNE      |loc_080249DA|
	ADD      r0, r3, #1
	STRB     r0, [r4]
	CMP      r3, #0
	BNE      |loc_080249B0|
	MOV      r1, #0x13
	LSL      r1, r1, #8
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x110f4
	LSL      r0, r0, #0x10
	ASR      r0, r0, #0x10
	STRH     r0, [r4, #2]
	LDR      r1, [pc, #0x7c]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	MOV      r2, #0x13
	LSL      r2, r2, #8
	LDR      r1, [pc, #0x78]
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080249B0|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
