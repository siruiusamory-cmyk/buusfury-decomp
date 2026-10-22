	CODE16
|loc_08036780|
	PUSH     {r4, r5, r6}
	ADD      r5, r3, #0
	MOV      r3, #0
	LDRSH    r4, [r2, r3]
	MOV      r3, #2
	LDRSH    r6, [r2, r3]
	LDR      r2, [pc, #0x1d8]
	LDR      r2, [r2, #0xc]
	ADD      r3, r2, #0
	LDR      r2, [r2, #0x28]
	ADD      r3, #0x28
	LDR      r3, [r3, #4]
	SUB      r2, r4, r2
	MOV      r4, #7
	MVN      r4, r4
	SUB      r3, r6, r3
	CMP      r2, r4
	BLT      |loc_08036800|
	CMP      r2, #0xf0
	BGE      |loc_08036800|
	CMP      r3, r4
	BLT      |loc_08036800|
	CMP      r3, #0xa0
	BGE      |loc_08036800|
	LDR      r4, [r1]
	LDR      r6, [pc, #0x1b8]
	STR      r5, [r4]
	LDR      r4, [r1]
	LSL      r2, r2, #0x17
	LDR      r5, [r4]
	LSR      r2, r2, #7
	AND      r5, r6
	ORR      r2, r5
	STR      r2, [r4]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	LDR      r4, [r1]
	ORR      r2, r3
	STR      r2, [r4]
	LDRB     r2, [r0, #8]
	MOV      r5, #3
	LSL      r5, r5, #0xa
	LSL      r3, r2, #0x1a
	LDR      r2, [r1]
	LSR      r3, r3, #0x1e
	ADD      r2, #4
	LDR      r4, [r2]
	LSL      r3, r3, #0xa
	BIC      r4, r5
	ORR      r3, r4
	STR      r3, [r2]
	LDRH     r0, [r0, #0xc]
	LSR      r3, r3, #0xa
	LSL      r3, r3, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LDR      r2, [r1]
	ORR      r0, r3
	STR      r0, [r2, #4]
	LDR      r0, [r1]
	ADD      r0, #8
	STR      r0, [r1]
|loc_08036800|
	POP      {r4, r5, r6}
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0x1c
	STR      r0, [sp, #0x18]
	LDR      r0, [r4, #0x14]
	ADD      r6, r1, #0
	ADD      r0, #1
	STR      r0, [r4, #0x14]
	LSL      r0, r0, #0x1b
	BPL      |loc_08036892|
	LDR      r0, [r4, #0x10]
	MOV      r3, #4
	LDRSH    r1, [r0, r3]
	MOV      r3, #6
	LDRSH    r2, [r0, r3]
	MOV      r3, #8
	LDRSH    r5, [r0, r3]
	MOV      r3, #0xa
	LDRSH    r0, [r0, r3]
	ADD      r5, #0xf
	STR      r5, [sp, #8]
	ADD      r0, #7
	STR      r0, [sp, #0xc]
	ADD      r5, r2, #0
	STR      r1, [sp]
	STR      r2, [sp, #4]
	LDR      r2, [sp, #8]
	LDR      r1, [sp, #0xc]
	LDR      r0, [sp]
	STR      r2, [sp, #0x10]
	STR      r1, [sp, #0x14]
	ADD      r3, sp, #0
	STRH     r0, [r3, #0xc]
	STRH     r5, [r3, #0xe]
	MOV      r3, #1
	ADD      r7, sp, #0x18
	ADD      r1, r7, #0
	LSL      r3, r3, #0xd
	ADD      r0, r4, #0
	ADD      r2, sp, #0xc
	BL       |loc_08036780|
	LDR      r0, [sp, #0x14]
	ADD      r3, sp, #0
	SUB      r0, #8
	STRH     r0, [r3, #0xe]
	ADD      r1, r7, #0
	ADD      r0, r4, #0
	LDR      r3, [pc, #0x108]
	ADD      r2, sp, #0xc
	BL       |loc_08036780|
	LDR      r0, [sp, #0x10]
	ADD      r3, sp, #0
	SUB      r0, #8
	STRH     r0, [r3, #0xc]
	ADD      r1, r7, #0
	ADD      r0, r4, #0
	LDR      r3, [pc, #0xf8]
	ADD      r2, sp, #0xc
	BL       |loc_08036780|
	ADD      r3, sp, #0
	STRH     r5, [r3, #0xe]
	ADD      r1, r7, #0
	ADD      r0, r4, #0
	LDR      r3, [pc, #0xec]
	ADD      r2, sp, #0xc
	BL       |loc_08036780|
|loc_08036892|
	MOV      r0, #0x98
	LDR      r0, [r0, r4]
	ADD      r3, r0, #1
	BEQ      |loc_0803690A|
	MOV      r1, #0
	MOV      r5, #3
	LDR      r7, [pc, #0xdc]
	LSL      r5, r5, #0xa
|loc_080368A2|
	LSL      r2, r1, #0x1c
	LSR      r2, r2, #7
	ORR      r2, r7
	LSR      r2, r2, #8
	LSL      r2, r2, #8
	LDR      r0, [sp, #0x18]
	ADD      r2, #0x88
	STR      r2, [r0]
	LDRH     r2, [r4, #0xc]
	LSL      r3, r1, #4
	ADD      r1, #1
	ADD      r2, r2, r3
	LDR      r3, [r0, #4]
	ADD      r2, #2
	LSL      r2, r2, #0x16
	LSR      r3, r3, #0xa
	LSL      r3, r3, #0xa
	LSR      r2, r2, #0x16
	ORR      r2, r3
	STR      r2, [r0, #4]
	LDRB     r3, [r4, #8]
	BIC      r2, r5
	LSL      r3, r3, #0x1a
	LSR      r3, r3, #0x1e
	LSL      r3, r3, #0xa
	ORR      r2, r3
	STR      r2, [r0, #4]
	ADD      r0, #8
	STR      r0, [sp, #0x18]
	CMP      r1, #7
	BLT      |loc_080368A2|
	LDR      r1, [pc, #0x9c]
	LDR      r0, [sp, #0x18]
	STR      r1, [r0]
	LDRH     r1, [r4, #0xc]
	LDR      r2, [r0, #4]
	ADD      r1, #0x72
	LSL      r1, r1, #0x16
	LSR      r2, r2, #0xa
	LSL      r2, r2, #0xa
	LSR      r1, r1, #0x16
	ORR      r1, r2
	STR      r1, [r0, #4]
	LDRB     r2, [r4, #8]
	BIC      r1, r5
	LSL      r2, r2, #0x1a
	LSR      r2, r2, #0x1e
	LSL      r2, r2, #0xa
	ORR      r1, r2
	STR      r1, [r0, #4]
	ADD      r0, #8
	STR      r0, [sp, #0x18]
|loc_0803690A|
	LDR      r0, [sp, #0x18]
	STR      r0, [r6]
	ADD      sp, #0x1c
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	CMP      r1, #0xb
	BEQ      |loc_0803694E|
	CMP      r1, #0x23
	BNE      |sub_08036964|
	LDR      r3, [r2]
	LDR      r1, [r2, #4]
	LSL      r3, r3, #2
	ADD      r3, r3, r0
	STR      r1, [r3, #0x18]
	LDR      r3, [pc, #0x3c]
	LDR      r4, [r2]
	LDR      r1, [r3, #8]
	LDR      r3, [r1]
	SUB      r3, r3, r4
	SUB      r3, #1
	LSL      r3, r3, #2
	ADD      r1, r3, r1
	LDR      r1, [r1, #4]
	LDR      r3, [r0, #0x10]
	CMP      r1, r3
	BNE      |loc_0803694A|
	LDR      r1, [r2, #4]
	MOV      r2, #0x98
	STR      r1, [r2, r0]
	BL       |sub_080364C6|
|loc_0803694A|
	MOV      r0, #1
	POP      {r4, pc}
|loc_0803694E|
	LDRH     r0, [r0, #0xc]
	LDR      r1, [pc, #0x30]
	MOV      r2, #0x40
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LDR      r1, [pc, #0xc]
	ADD      r1, #0x14
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0
	POP      {r4, pc}
