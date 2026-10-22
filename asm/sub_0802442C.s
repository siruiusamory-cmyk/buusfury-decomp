	CODE16
|sub_0802442C|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	ADD      r5, #0xff
	ADD      r5, #1
	ADD      r4, r1, #0
	LDR      r1, [r5, #0x38]
	CMP      r1, #0
	BNE      |loc_08024484|
	ADD      r0, #0xff
	ADD      r0, #0x41
	LDR      r1, [r0]
	MOV      r6, #0
	CMP      r1, #0
	BEQ      |loc_08024462|
	CMP      r1, #1
	BEQ      |loc_08024462|
	MOV      r0, #1
	CMP      r1, #2
	BEQ      |loc_08024478|
	CMP      r1, #3
	BNE      |loc_08024484|
	STRB     r0, [r4]
	STRB     r0, [r4, #1]
	LDR      r0, [r5, #0x3c]
	STRB     r0, [r4, #3]
	MOV      r0, #4
	POP      {r4, r5, r6, pc}
|loc_08024462|
	MOV      r2, #0x20
	ADD      r0, r4, #4
	LDR      r1, [r5, #0x30]
	BL       |inc_0x049120_0x055620| + 0x18
	STRB     r6, [r4]
	STRB     r6, [r4, #1]
	LDR      r0, [r5, #0x3c]
	STRB     r0, [r4, #3]
	MOV      r0, #0x24
	POP      {r4, r5, r6, pc}
|loc_08024478|
	STRB     r0, [r4]
	STRB     r6, [r4, #1]
	LDR      r0, [r5, #0x3c]
	STRB     r0, [r4, #3]
	MOV      r0, #4
	POP      {r4, r5, r6, pc}
|loc_08024484|
	LDR      r0, [r5, #0x2c]
	STRB     r0, [r4]
	LDR      r0, [r5, #0x3c]
	STRB     r0, [r4, #1]
	MOV      r0, #2
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r1, #0
	SUB      r1, r2, #3
	CMP      r1, #5
	BCS      |loc_080244BC|
	ADD      r3, pc, #0x8
	LDRB     r3, [r3, r1]
	LSL      r3, r3, #1
	ADD      pc, r3
	LSL      r0, r0, #0
|loc_080244A4|
	LSR      r5, r1, #0x14
	LSL      r5, r1, #0xc
	LSL      r3, r3, #0
	MOV      r2, #0xff
	ADD      r2, #0x3d
	MOV      r1, #0
	STR      r1, [r2, r0]
	ADD      r0, #0xff
	ADD      r0, #0x41
	STR      r1, [r0]
	LDR      r0, [pc, #0xb0]
	STR      r1, [r0, #4]
|loc_080244BC|
	POP      {r4, r5, r6, pc}
	LDR      r0, [pc, #0xb0]
	LDR      r0, [r0]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BNE      |loc_080244BC|
	LDR      r1, [pc, #0x8c]
	MOV      r0, #1
	STR      r0, [r1]
	POP      {r4, r5, r6, pc}
|sub_080244DA|
|unk_080244DA|
	INCBIN	baserom.gba_0x244da_0x244ec.extracted
