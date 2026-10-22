	CODE16
|Ram_WriteSlotPair1|
	LDR      r1, [pc, #0xd8]
	PUSH     {r4}
	LDR      r1, [r1, #0x14]
	MOV      r3, #0x68
	LDRB     r2, [r1]
	LSL      r0, r0, #0x10
	ASR      r0, r0, #0x10
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	ADD      r1, #0x1a
	ADD      r4, r0, #0
|loc_080005AA|
	STRH     r0, [r1]
	MOV      r3, #0
	LDRSH    r2, [r1, r3]
	CMP      r2, r0
	BNE      |loc_080005AA|
	ADD      r0, r4, #0
|loc_080005B6|
	STRH     r0, [r1, #2]
	MOV      r3, #2
	LDRSH    r2, [r1, r3]
	CMP      r2, r0
	BNE      |loc_080005B6|
	POP      {r4}
	BX       lr
	CMP      r0, #0
	BGE      |loc_080005CA|
	MOV      r0, #0
|loc_080005CA|
	LDR      r1, [pc, #0x9c]
	LDR      r2, [pc, #0xa0]
	LDR      r1, [r1, #0x14]
	ADD      r1, r1, r2
|loc_080005D2|
	STR      r0, [r1]
	LDR      r2, [r1]
	CMP      r2, r0
	BNE      |loc_080005D2|
	BX       lr
	LDR      r1, [pc, #0x88]
	LDR      r1, [r1, #0xc]
	LDRB     r2, [r1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x74]
	LDR      r1, [r1, #0xc]
	LDRB     r2, [r1, #1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x60]
	LDR      r1, [r1, #0xc]
	LDRB     r2, [r1, #2]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x4c]
	LDR      r1, [r1, #0x14]
	LDRB     r2, [r1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x38]
	MOV      r3, #0x68
	LDR      r1, [r1, #0x14]
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1, #0x14]
	LDR      r2, [pc, #0x28]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDRH     r1, [r1, #2]
	LDR      r2, [pc, #0x24]
	LSL      r1, r1, #2
	LDR      r2, [r2, r1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
|sub_08000660|
|unk_08000660|
	INCBIN	baserom.gba_0x660_0x662.extracted
