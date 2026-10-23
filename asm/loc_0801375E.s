	CODE16
|loc_0801375E|
	PUSH     {r3, r4, r5, r6, r7}
	LDRB     r4, [r1, #0x14]
	ADD      r6, r3, #0
	LDRB     r7, [r2, #0x14]
	LSL      r3, r4, #1
	ADD      r3, r3, r4
	LDR      r4, [pc, #0x1a0]
	LSL      r3, r3, #3
	ADD      r3, r3, r4
	LDRB     r5, [r3, #0xc]
	LSL      r3, r7, #1
	ADD      r3, r3, r7
	LSL      r3, r3, #3
	ADD      r3, r3, r4
	LDRB     r3, [r3, #0xc]
	LSL      r3, r3, #4
	ADD      r3, r5, r3
	LSL      r5, r6, #8
	ADD      r3, r3, r5
	STRH     r3, [r0, #2]
	LDR      r3, [pc, #0x180]
	LDRB     r6, [r0, #0x14]
	SUB      r3, #4
	LDR      r5, [r3]
	LSL      r3, r6, #1
	ADD      r3, r3, r6
	LSL      r3, r3, #3
	ADD      r3, r3, r4
	LDRB     r4, [r3, #0xc]
	MOV      r3, #0x68
	MUL      r3, r4
	MOV      r4, #0x9f
	LSL      r4, r4, #3
	ADD      r3, r3, r5
	ADD      r3, r3, r4
	LDRB     r4, [r3]
	MOV      r5, #1
	ORR      r4, r5
	STRB     r4, [r3]
	ADD      r4, r1, #0
	ADD      r4, #0x18
	MOV      r3, #0
	LDRSH    r4, [r4, r3]
	ADD      r5, r2, #0
	ADD      r5, #0x18
	LDRSH    r5, [r5, r3]
	ADD      r4, r4, r5
	MOV      r3, #0x9a
	MUL      r3, r4
	ASR      r3, r3, #8
	LSL      r4, r3, #0x10
	ASR      r4, r4, #0x10
|loc_080137C6|
	STRH     r4, [r0, #0x18]
	MOV      r3, #0x18
	LDRSH    r5, [r0, r3]
	CMP      r5, r4
	BNE      |loc_080137C6|
	ADD      r4, r1, #0
	ADD      r4, #0x16
	MOV      r3, #0
	LDRSH    r4, [r4, r3]
	ADD      r5, r2, #0
	ADD      r5, #0x16
	LDRSH    r5, [r5, r3]
	ADD      r4, r4, r5
	MOV      r3, #0x9a
	MUL      r3, r4
	ASR      r3, r3, #8
	LSL      r4, r3, #0x10
	ASR      r4, r4, #0x10
|loc_080137EA|
	STRH     r4, [r0, #0x16]
	MOV      r3, #0x16
	LDRSH    r5, [r0, r3]
	CMP      r5, r4
	BNE      |loc_080137EA|
	ADD      r4, r1, #0
	ADD      r4, #0x1c
	MOV      r3, #0
	LDRSH    r4, [r4, r3]
	ADD      r5, r2, #0
	ADD      r5, #0x1c
	LDRSH    r5, [r5, r3]
	ADD      r4, r4, r5
	MOV      r3, #0x9a
	MUL      r3, r4
	ASR      r3, r3, #8
	LSL      r4, r3, #0x10
	ASR      r4, r4, #0x10
|loc_0801380E|
	STRH     r4, [r0, #0x1c]
	MOV      r3, #0x1c
	LDRSH    r5, [r0, r3]
	CMP      r5, r4
	BNE      |loc_0801380E|
	ADD      r4, r1, #0
	ADD      r4, #0x1a
	MOV      r3, #0
	LDRSH    r4, [r4, r3]
	ADD      r5, r2, #0
	ADD      r5, #0x1a
	LDRSH    r5, [r5, r3]
	ADD      r4, r4, r5
	MOV      r3, #0x9a
	MUL      r3, r4
	ASR      r3, r3, #8
	LSL      r4, r3, #0x10
	ASR      r4, r4, #0x10
|loc_08013832|
	STRH     r4, [r0, #0x1a]
	MOV      r3, #0x1a
	LDRSH    r5, [r0, r3]
	CMP      r5, r4
	BNE      |loc_08013832|
	ADD      r3, r1, #0
	ADD      r3, #0x24
	LDR      r3, [r3]
	ADD      r4, r2, #0
	ADD      r4, #0x24
	LDR      r4, [r4]
	ADD      r3, r3, r4
	LSR      r3, r3, #1
|loc_0801384C|
	STR      r3, [r0, #0x24]
	LDR      r4, [r0, #0x24]
	CMP      r4, r3
	BNE      |loc_0801384C|
	ADD      r3, r0, #0
	ADD      r3, #0x28
	ADD      r4, r1, #0
	ADD      r4, #0x28
	LDRB     r4, [r4]
	ADD      r5, r2, #0
	ADD      r5, #0x28
	LDRB     r5, [r5]
	ADD      r4, r4, r5
	LSR      r4, r4, #1
	ADD      r4, #0xa
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
|loc_0801386E|
	STRB     r4, [r3]
	LDRB     r5, [r3]
	CMP      r5, r4
	BNE      |loc_0801386E|
	ADD      r3, r0, #0
	ADD      r3, #0x29
	ADD      r4, r1, #0
	ADD      r4, #0x29
	LDRB     r4, [r4]
	ADD      r5, r2, #0
	ADD      r5, #0x29
	LDRB     r5, [r5]
	ADD      r4, r4, r5
	LSR      r4, r4, #1
	ADD      r4, #0xa
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
|loc_08013890|
	STRB     r4, [r3]
	LDRB     r5, [r3]
	CMP      r5, r4
	BNE      |loc_08013890|
	ADD      r3, r0, #0
	ADD      r3, #0x2a
	ADD      r4, r1, #0
	ADD      r4, #0x2a
	LDRB     r4, [r4]
	ADD      r5, r2, #0
	ADD      r5, #0x2a
	LDRB     r5, [r5]
	ADD      r4, r4, r5
	LSR      r4, r4, #1
	ADD      r4, #0xa
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
|loc_080138B2|
	STRB     r4, [r3]
	LDRB     r5, [r3]
	CMP      r5, r4
	BNE      |loc_080138B2|
	ADD      r3, r0, #0
	ADD      r3, #0x2b
	ADD      r4, r1, #0
	ADD      r4, #0x2b
	LDRB     r4, [r4]
	ADD      r5, r2, #0
	ADD      r5, #0x2b
	LDRB     r5, [r5]
	ADD      r4, r4, r5
	LSR      r4, r4, #1
	ADD      r4, #0x10
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
|loc_080138D4|
	STRB     r4, [r3]
	LDRB     r5, [r3]
	CMP      r5, r4
	BNE      |loc_080138D4|
	MOV      r3, #0
|loc_080138DE|
	LSL      r5, r3, #2
	ADD      r4, r5, r0
	ADD      r4, #0x3c
	STR      r4, [sp]
	ADD      r4, r5, r1
	ADD      r4, #0x3c
	LDR      r6, [r4]
	ADD      r5, r5, r2
	ADD      r5, #0x3c
	LDR      r7, [r5]
	CMP      r6, r7
	BGT      |loc_080138F8|
	ADD      r4, r5, #0
|loc_080138F8|
	LDR      r4, [r4]
	LDR      r5, [sp]
	STR      r4, [r5]
	ADD      r3, #1
	CMP      r3, #4
	BLT      |loc_080138DE|
	POP      {r3, r4, r5, r6, r7}
	BX       lr
|sub_08013908|
|unk_08013908|
	INCBIN	baserom.gba_0x13908_0x1390a.extracted
|sub_0801390A|
	DCW      0x086b
	DCW      0x82ec
	DCW      0x086b
	DCW      0x72e0
	DCW      0x086b
