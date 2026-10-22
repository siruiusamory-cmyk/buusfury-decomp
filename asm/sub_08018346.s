	CODE16
|sub_08018346|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	LSL      r0, r1, #2
	LDR      r1, [pc, #0x3c]
	ADD      r6, r2, #0
	ADD      r1, #0x14
	LDR      r5, [pc, #0x38]
	LDR      r4, [r1, r0]
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #3
	LSL      r1, r1, #0xc
	CMP      r0, r1
	BLT      |loc_08018384|
	LDR      r0, [r5, #0x10]
	MOV      r1, #0x30
	LDR      r0, [r0]
	SUB      r0, r1, r0
	CMP      r0, #8
	BLE      |loc_08018384|
	ADD      r3, r6, #0
	ADD      r2, r7, #0
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |loc_08017F5A|
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08018384|
	POP      {r3, r4, r5, r6, r7, pc}
|loc_08018386|
	DCW      0x0000
	DCW      0x0000,0x0601,0xc23c,0x086f,0xffff
|sub_08018392|
|unk_08018392|
	INCBIN  baserom.gba_0x18392_0x18394.extracted
		PUSH {r4, r5, r6, r7, lr}
	LDR      r4, [r1, #4]
	ADD      r6, r1, #0
	LDR      r1, [pc, #0x118]
	ADD      r7, r0, #0
	MOV      r0, #1
	LDR      r1, [r1]
	ADD      r5, r0, #0
	CMP      r4, r1
	SUB      sp, #0x14
	BEQ      |loc_080183AC|
	MOV      r5, #0
|loc_080183AC|
	CMP      r5, #0
	BEQ      |loc_080183B4|
	LDR      r1, [pc, #0x104]
	STR      r0, [r1]
|loc_080183B4|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #8]
	ADD      r0, r1, #0
	STR      r1, [sp, #4]
	LDR      r1, [sp, #8]
	STR      r0, [sp, #0xc]
	STR      r1, [sp, #0x10]
	LDRB     r0, [r4, #0x10]
	MOV      r1, #0
	STR      r0, [sp, #8]
	LDR      r7, [r7, #8]
	LDR      r0, [r6]
	STR      r1, [r6]
	ADD      r6, r0, #0
	ADD      r1, r4, #0
	LDR      r4, [pc, #0xd0]
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r1, [sp, #0xc]
	ADD      r3, sp, #0
	LDR      r0, [sp, #0x10]
	STRH     r1, [r3, #4]
	STRH     r0, [r3, #6]
	ADD      r0, r7, #0
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	MOV      r0, #0
	ADD      r2, sp, #4
	BL       |inc_0x0158_0x143f2| + 0x10fc4
	ADD      r7, r0, #0
	LDR      r0, [sp, #8]
	ADD      r1, r7, #0
	STRB     r0, [r7, #0x10]
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r1, r7, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
	ADD      r0, r6, #0
	BL       |loc_080192BA|
	CMP      r5, #0
	BEQ      |loc_0801842E|
	LDR      r1, [pc, #0x88]
	STR      r7, [r1]
|loc_0801842E|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LDR      r4, [r1, #4]
	ADD      r5, r1, #0
	LDR      r1, [pc, #0x78]
	MOV      r0, #1
	LDR      r1, [r1]
	ADD      r6, r0, #0
	CMP      r4, r1
	SUB      sp, #0x14
	BEQ      |loc_08018448|
	MOV      r6, #0
|loc_08018448|
	CMP      r6, #0
	BEQ      |loc_08018450|
	LDR      r1, [pc, #0x68]
	STR      r0, [r1]
|loc_08018450|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #8]
	ADD      r0, r1, #0
	STR      r1, [sp, #4]
	LDR      r1, [sp, #8]
	STR      r0, [sp, #0xc]
	STR      r1, [sp, #0x10]
	LDRB     r7, [r4, #0x10]
	LDR      r0, [r5]
	MOV      r1, #0
	STR      r1, [r5]
	ADD      r5, r0, #0
	ADD      r1, r4, #0
	LDR      r4, [pc, #0x38]
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r0, [sp, #0x14]
	ADD      r3, r7, #0
	LDR      r1, [r0, #8]
	LDR      r0, [r4, #4]
	ADD      r2, sp, #0xc
	BL       |inc_0x0158_0x143f2| + 0x8fcc
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080192BA|
	CMP      r6, #0
	BEQ      |loc_080184AE|
	LDR      r1, [pc, #8]
	STR      r4, [r1]
|loc_080184AE|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	SUB      r4, r5, r6
	LSL      r0, r0, #0xc
	CMP      r2, #0x58
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r6, r7}
	LSR      r7, r5, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x10]
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	CMP      r0, #0
	BEQ      |loc_080184F6|
	LDR      r5, [r0, #8]
	LDRB     r0, [r5]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r5]
	BNE      |loc_080184F6|
	LDRH     r0, [r5, #2]
	LDR      r1, [pc, #0x2a8]
	CMP      r0, r1
	BEQ      |loc_080184F6|
	MOV      r3, #2
	LDR      r0, [pc, #0x2a4]
	LDRSH    r1, [r5, r3]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r5, #2]
|loc_080184F6|
	ADD      r1, r7, #0
	ADD      r0, r6, #0
	BL       |inc_0x0158_0x143f2| + 0x13ce0
	STR      r0, [r4, #0x10]
	CMP      r0, #0
	BEQ      |sub_08018546|
	LDR      r5, [r0, #8]
	LDRH     r6, [r0, #2]
	LDR      r7, [r0, #4]
	LDRB     r0, [r5]
	ADD      r1, r0, #1
	STRB     r1, [r5]
	CMP      r0, #0
	BNE      |loc_08018532|
	LDR      r0, [pc, #0x274]
	ADD      r1, r6, #0
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x110f4
	LSL      r0, r0, #0x10
	ASR      r0, r0, #0x10
	STRH     r0, [r5, #2]
	LDR      r1, [pc, #0x268]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	ADD      r2, r6, #0
	ADD      r1, r7, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08018532|
	LDR      r1, [r4, #0x10]
	LDR      r2, [r4, #0x14]
	LDRB     r0, [r1]
	LDRB     r1, [r1, #1]
	ADD      r0, r2, r0
	STR      r0, [r4, #0x1c]
	LDR      r0, [r4, #0x18]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x20]
	POP      {r3, r4, r5, r6, r7, pc}
