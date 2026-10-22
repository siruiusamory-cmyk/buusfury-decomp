	CODE16
|loc_08010692|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r1, #0x14]
	LDR      r7, [pc, #0x14c]
	ADD      r5, r1, #0
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r7
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800EDF8|
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r6, r4, r0
	LDR      r0, [r6, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDRB     r0, [r5, #0x14]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r7
	BL       |inc_0x153f2_0x1a3f2| + 0x1d58
	STR      r0, [r6, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r0, r4, #0
	BL       |loc_0801064C|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, r4, r5, r6, r7, pc}
	MOV      r1, #1
	LSL      r1, r1, #9
	ADD      r0, r0, r1
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x2c]
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0xc4]
	LDR      r7, [pc, #0xbc]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1f
	BEQ      |loc_0801078E|
	LDR      r1, [r4]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #2]
	LSR      r5, r0, #8
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r6, r4, r0
	LDR      r0, [r6, #0x2c]
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r7, #8]
	MOV      r2, #0x13
	LSL      r2, r2, #6
	STRB     r5, [r0]
	ADD      r0, r0, r2
	MOV      r1, #0
	STR      r1, [r0, #0x1c]
	LDR      r0, [r7, #8]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	ADD      r1, r2, #0
	ADD      r1, #0x38
	ADD      r1, r0, r1
	ADD      r0, r4, #0
	BL       |loc_08010692|
	LDR      r0, [r6, #0x2c]
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_0801078E|
	MOV      r0, #0xff
	ADD      r0, #0xcd
	MOV      r1, #0
	STR      r1, [r0, r4]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080107A8|
	MOV      r1, #5
	STRB     r1, [r0, #4]
	LDR      r1, [pc, #0x4c]
	STR      r1, [r0]
|loc_080107A8|
	ADD      r5, r0, #0
	MOV      r1, #0x11
	ADD      r0, r4, #0
	BL       |Record_SelectIndexed|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_0800ED18|
	MOV      r0, #8
	LDR      r4, [r7, #4]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080107CE|
	MOV      r1, #0xc8
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x2c]
	STR      r1, [r0]
|loc_080107CE|
	ADD      r2, r0, #0
	MOV      r0, #0x61
	LSL      r0, r0, #4
	ADD      r0, r4, r0
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	POP      {r3, r4, r5, r6, r7, pc}
|sub_080107E4|
|unk_080107E4|
	INCBIN	baserom.gba_0x107e4_0x107e6.extracted
