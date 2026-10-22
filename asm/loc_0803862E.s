	CODE16
|loc_0803862E|
	PUSH     {r4, r5, r6, r7}
	MOV      ip, r3
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r5, [sp, #0x10]
	LDR      r4, [r0, #0x44]
	LSL      r1, r1, #2
	ADD      r1, r4, r1
	MOV      r3, #0
	LDRSB    r6, [r1, r3]
	LDR      r4, [r0, #0x2c]
	ADD      r3, r4, r6
	LDR      r4, [r5]
	LDR      r6, [r0, #0x30]
	ADD      r4, r3, r4
	MOV      r3, #1
	LDRSB    r7, [r1, r3]
	LDR      r5, [r5, #4]
	ADD      r3, r6, r7
	ADD      r3, r3, r5
	LDR      r7, [pc, #0x88]
	LDRB     r5, [r1, #2]
	LDRB     r6, [r1, #3]
	ADD      r7, #0x14
	LDR      r7, [r7, #8]
	ADD      r5, r4, r5
	ADD      r6, r3, r6
	CMP      r4, r7
	BGE      |loc_080386D8|
	LDR      r7, [pc, #0x74]
	ADD      r7, #0x14
	LDR      r7, [r7]
	CMP      r7, r5
	BGE      |loc_080386D8|
	LDR      r5, [pc, #0x6c]
	ADD      r5, #0x14
	LDR      r7, [r5, #0xc]
	CMP      r3, r7
	BGE      |loc_080386D8|
	LDR      r5, [r5, #4]
	CMP      r5, r6
	BGE      |loc_080386D8|
	LDR      r5, [r2]
	LDR      r1, [r1, #4]
	LDR      r6, [pc, #0x80]
	STR      r1, [r5]
	LDR      r1, [r2]
	LSL      r4, r4, #0x17
	LDR      r5, [r1]
	LSR      r4, r4, #7
	AND      r5, r6
	ORR      r4, r5
	STR      r4, [r1]
	LSR      r4, r4, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r4, r4, #8
	LDR      r1, [r2]
	ORR      r3, r4
	STR      r3, [r1]
	LDRH     r1, [r0, #0xc]
	ADD      r3, r1, #0
	LDR      r1, [r2]
	ADD      r3, ip
	ADD      r1, #4
	LDR      r4, [r1]
	LSL      r3, r3, #0x16
	LSR      r4, r4, #0xa
	LSL      r4, r4, #0xa
	LSR      r3, r3, #0x16
	ORR      r3, r4
	STR      r3, [r1]
	LDRB     r0, [r0, #8]
	MOV      r4, #3
	LSL      r4, r4, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r3, r4
	LDR      r1, [r2]
	ORR      r0, r3
	STR      r0, [r1, #4]
	LDR      r0, [r2]
	ADD      r0, #8
	STR      r0, [r2]
|loc_080386D8|
	POP      {r4, r5, r6, r7}
	BX       lr
|loc_080386DC|
	DCW      0x9680
	DCW      0x0804,0xe0b8,0x0876,0xc55c,0x0804,0xe264,0x0876,0x268c
	DCW      0x0807,0x9440,0x0831,0x05c4,0x0000,0x0000,0x0601,0xffff
	DCW      0x0000,0xe454,0x0804,0x8108,0x086b,0xffff
|sub_0803870A|
|unk_0803870A|
	INCBIN  baserom.gba_0x3870a_0x3870c.extracted
		PUSH {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0x14
	LDR      r2, [pc, #0xbc]
	ADD      r7, sp, #0x10
	ADD      r6, r1, #0
	STR      r2, [sp]
	ADD      r2, r7, #0
	MOV      r1, #0
	STR      r0, [sp, #0x10]
	MOV      r3, #0
	ADD      r0, r4, #0
	BL       |loc_0803862E|
	LDR      r0, [r4, #0x3c]
	MOV      r5, #8
	SUB      r0, #9
	CMP      r0, #8
	BLE      |loc_0803875E|
|loc_08038734|
	LDR      r0, [r4, #0x34]
	LDR      r1, [r4, #0x38]
	MUL      r0, r5
	MUL      r1, r5
	STR      r0, [sp]
	ADD      r2, sp, #8
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	MOV      r1, #1
	ADD      r2, r7, #0
	STR      r0, [sp, #8]
	MOV      r3, #2
	ADD      r0, r4, #0
	BL       |loc_0803862E|
	LDR      r0, [r4, #0x3c]
	ADD      r5, #8
	SUB      r0, #9
	CMP      r0, r5
	BGT      |loc_08038734|
|loc_0803875E|
	LDR      r0, [r4, #0x3c]
	LDR      r1, [r4, #0x34]
	SUB      r0, #8
	LDR      r2, [r4, #0x38]
	MUL      r1, r0
	MUL      r2, r0
	STR      r2, [sp, #4]
	STR      r2, [sp, #0xc]
	STR      r1, [sp]
	ADD      r2, sp, #8
	ADD      r0, r1, #0
	STR      r2, [sp]
	ADD      r2, r7, #0
	STR      r0, [sp, #8]
	MOV      r1, #2
	MOV      r3, #4
	ADD      r0, r4, #0
	BL       |loc_0803862E|
	LDR      r0, [sp, #0x10]
	STR      r0, [r6]
	ADD      sp, #0x14
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	ADD      r2, r0, #0
	CMP      r1, #0xb
	PUSH     {r3, lr}
	BEQ      |sub_080387AC|
	CMP      r1, #0xc
	BNE      |loc_080387C2|
	LDR      r1, [r2]
	ADD      r0, r2, #0
	LDR      r2, [r1, #0x28]
	ADD      r3, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	MOV      r0, #0
	POP      {r3, pc}
