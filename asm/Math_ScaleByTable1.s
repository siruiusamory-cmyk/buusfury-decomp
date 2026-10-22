	CODE16
|Math_ScaleByTable1|
	ADD      r1, r0, #0
	ADD      r1, #0x50
	MOV      r3, #0x4f
	LDRB     r3, [r3, r0]
	LDRB     r2, [r1, #1]
	ADD      r2, r2, r3
	LSL      r2, r2, #0x1a
	LSR      r2, r2, #0x1a
	STRB     r2, [r1, #1]
	LDR      r3, [pc, #0x18c]
	LDRB     r1, [r1]
	LDRSB    r2, [r3, r2]
	MUL      r1, r2
	ASR      r1, r1, #6
	LDR      r2, [r0, #0x40]
	BPL      |loc_0803E8EC|
	LDR      r3, [pc, #0x168]
	LSL      r1, r1, #1
	SUB      r3, #0x80
	SUB      r1, r3, r1
	LDRH     r1, [r1]
	MUL      r2, r1
	LSR      r1, r2, #0x10
	B        |loc_0803E8F8|
|loc_0803E8EC|
	LDR      r3, [pc, #0x15c]
	LSL      r1, r1, #1
	SUB      r3, #0x80
	LDRH     r1, [r3, r1]
	MUL      r2, r1
	LSR      r1, r2, #0xf
|loc_0803E8F8|
	STR      r1, [r0, #0x30]
	LDRB     r1, [r0, #0x10]
	MOV      r2, #2
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
	BX       lr
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	BL       |loc_0803E4E4|
	ADD      r2, r4, #0
	ADD      r2, #0x40
	LDRB     r3, [r2, #0xa]
	LSL      r0, r3, #0x1d
	LSR      r0, r0, #0x1f
	BEQ      |loc_0803E94E|
	ADD      r0, r4, #0
	ADD      r0, #0x50
	LDRB     r1, [r0, #8]
	MOV      r5, #0x11
	AND      r1, r5
	BEQ      |loc_0803E928|
	MOV      r1, #0
	STRB     r1, [r0, #1]
|loc_0803E928|
	LDRB     r1, [r0, #0xe]
	LSL      r5, r1, #0x1c
	BEQ      |loc_0803E934|
	LSL      r5, r1, #0x1c
	LSR      r5, r5, #0x1a
	STRB     r5, [r0]
|loc_0803E934|
	LSL      r0, r1, #0x18
	LSR      r0, r0, #0x1c
	BEQ      |loc_0803E93E|
	LSR      r0, r1, #4
	STRB     r0, [r2, #0xf]
|loc_0803E93E|
	LDR      r0, [pc, #0x120]
	STR      r0, [r4, #0x54]
	MOV      r0, #1
	ORR      r0, r3
	STRB     r0, [r2, #0xa]
	ADD      r0, r4, #0
	BL       |Math_ScaleByTable1|
|loc_0803E94E|
	POP      {r4, r5, pc}
|sub_0803E950|
|unk_0803E950|
	INCBIN	baserom.gba_0x3e950_0x3e954.extracted
