	CODE16
|loc_08036656|
	CMP      r6, r1
	BLT      |loc_08036682|
	ADD      r2, r6, #0
	MUL      r2, r6
	ADD      r6, r1, #0
	MUL      r6, r1
	LSL      r1, r6, #3
	ADD      r1, r1, r6
	ADD      r1, r2, r1
	CMP      r1, lr
	BGE      |loc_08036682|
	MOV      lr, r1
	LDR      r1, [pc, #0x9c]
	STR      r4, [r0, #0x10]
	LDR      r1, [r1, #8]
	LDR      r1, [r1]
	SUB      r1, r1, r5
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #0x14]
	LDR      r2, [sp, #0x38]
	STR      r1, [r2, #0x18]
|loc_08036682|
	LDR      r1, [pc, #0x88]
	ADD      r5, #1
	LDR      r1, [r1, #8]
	LDR      r1, [r1]
	CMP      r1, r5
	BGT      |loc_080365D6|
|loc_0803668E|
	LDR      r2, [sp, #0x38]
	LDR      r1, [r2, #0x18]
	ADD      r3, r1, #1
	BEQ      |loc_0803669A|
	BL       |sub_080364C6|
|loc_0803669A|
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x68]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1f
	BEQ      |loc_080366B6|
	MOV      r1, #2
	ADD      r0, r4, #0
	BL       |loc_0803656C|
|loc_080366B6|
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1b
	LSR      r0, r0, #0x1f
	BEQ      |loc_080366C8|
	MOV      r1, #3
	ADD      r0, r4, #0
	BL       |loc_0803656C|
|loc_080366C8|
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x19
	LSR      r0, r0, #0x1f
	BEQ      |loc_080366DA|
	MOV      r1, #1
	ADD      r0, r4, #0
	BL       |loc_0803656C|
|loc_080366DA|
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1f
	BEQ      |loc_080366EC|
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |loc_0803656C|
|loc_080366EC|
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |loc_08036704|
	LDR      r0, [r4, #0x10]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	LDR      r1, [pc, #0x2c]
	LDR      r1, [r1]
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08036704|
	POP      {r3, r4, r5, pc}
|loc_08036706|
	DCW      0x0000
	DCW      0x9680,0x0804,0xa73c,0x0875,0xbaf4,0x0804,0x0000,0x0601
	DCW      0x248c,0x0807,0xf5a5,0x0803,0xbce8,0x0806,0x268c,0x0807
	DCW      0xffff
|loc_0803672A|
	LDRB     r7, [r7, #0x1f]
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	PUSH     {r4, r5}
	LDR      r1, [r0, #0x10]
	MOV      r3, #4
	LDRSH    r2, [r1, r3]
	MOV      r3, #6
	LDRSH    r4, [r1, r3]
	MOV      r3, #8
	LDRSH    r5, [r1, r3]
	MOV      r3, #0xa
	LDRSH    r1, [r1, r3]
	SUB      sp, #0x28
	ADD      r5, #0xf
	STR      r5, [sp, #8]
	STR      r4, [sp, #4]
	ADD      r1, #7
	STR      r1, [sp, #0xc]
	MOV      r4, sp
	STR      r2, [sp]
	LDMIA    r4!, {r1, r2, r3, r4}
	ADD      r5, sp, #0x10
	STMIA    r5!, {r1, r2, r3, r4}
	LDR      r1, [sp, #0x10]
	LDR      r2, [sp, #0x18]
	LDR      r3, [sp, #0x1c]
	ADD      r2, r1, r2
	LDR      r1, [sp, #0x14]
	STR      r2, [sp, #8]
	ASR      r2, r2, #1
	ADD      r1, r1, r3
	STR      r1, [sp, #0xc]
	ASR      r1, r1, #1
	STR      r1, [sp, #0xc]
	STR      r1, [sp, #0x24]
	STR      r2, [sp, #8]
	STR      r2, [sp, #0x20]
	STR      r1, [r0, #4]
	ADD      sp, #0x28
	POP      {r4, r5}
	MOV      r0, #1
	BX       lr
