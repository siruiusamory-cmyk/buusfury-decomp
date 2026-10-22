	CODE16
|sub_0802A5A2|
	LSR      r4, r0, #0x20
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	BLS      |loc_0802A54C|
	LSR      r7, r5, #1
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4}
	LDR      r1, [pc, #0x1e8]
	LDR      r3, [r0, #0x20]
	LDR      r1, [r1, #8]
	ADD      r2, r0, #0
	ADD      r1, #0x18
	LDR      r4, [r1]
	LDR      r0, [r0, #0x24]
	LDR      r1, [r1, #4]
	SUB      r3, r3, r4
	ADD      r2, #0x30
	SUB      sp, #8
	SUB      r0, r0, r1
	STR      r0, [sp, #4]
	LDR      r1, [sp, #4]
	STR      r3, [sp]
	STR      r1, [r2, #4]
	STR      r3, [r2]
	ADD      sp, #8
	POP      {r4}
	MOV      r0, #1
	BX       lr
|loc_0802A5EC|
	PUSH     {r4, r5, r6, r7}
	MOV      ip, r3
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r5, [sp, #0x10]
	LDR      r4, [r0, #0x48]
	LSL      r1, r1, #2
	ADD      r1, r4, r1
	MOV      r3, #0
	LDRSB    r6, [r1, r3]
	LDR      r4, [r0, #0x30]
	ADD      r3, r4, r6
	LDR      r4, [r5]
	LDR      r6, [r0, #0x34]
	ADD      r4, r3, r4
	MOV      r3, #1
	LDRSB    r7, [r1, r3]
	LDR      r5, [r5, #4]
	ADD      r3, r6, r7
	ADD      r3, r3, r5
	LDR      r7, [pc, #0x194]
	LDRB     r5, [r1, #2]
	LDRB     r6, [r1, #3]
	ADD      r7, #0x14
	LDR      r7, [r7, #8]
	ADD      r5, r4, r5
	ADD      r6, r3, r6
	CMP      r4, r7
	BGE      |loc_0802A696|
	LDR      r7, [pc, #0x184]
	ADD      r7, #0x14
	LDR      r7, [r7]
	CMP      r7, r5
	BGE      |loc_0802A696|
	LDR      r5, [pc, #0x178]
	ADD      r5, #0x14
	LDR      r7, [r5, #0xc]
	CMP      r3, r7
	BGE      |loc_0802A696|
	LDR      r5, [r5, #4]
	CMP      r5, r6
	BGE      |loc_0802A696|
	LDR      r5, [r2]
	LDR      r1, [r1, #4]
	LDR      r6, [pc, #0x168]
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
|loc_0802A696|
	POP      {r4, r5, r6, r7}
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0x14
	STR      r0, [sp, #0x10]
	LDR      r0, [r4, #0x40]
	ADD      r6, r1, #0
	CMP      r0, #0x30
	ADD      r7, sp, #0x10
	BGE      |loc_0802A6C6|
	LDRB     r0, [r4, #0x10]
	CMP      r0, #0
	BNE      |loc_0802A6C6|
	LDR      r2, [pc, #0xf4]
	MOV      r3, #0
	ADD      r2, #0xc
	STR      r2, [sp]
	ADD      r2, r7, #0
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |loc_0802A5EC|
|loc_0802A6C6|
	LDR      r0, [r4, #0x40]
	MOV      r5, #0
	SUB      r0, #1
	CMP      r0, #0
	BLE      |loc_0802A6FA|
|loc_0802A6D0|
	LDR      r0, [r4, #0x38]
	LDR      r1, [r4, #0x3c]
	MUL      r0, r5
	MUL      r1, r5
	STR      r0, [sp]
	ADD      r2, sp, #8
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	MOV      r1, #2
	ADD      r2, r7, #0
	STR      r0, [sp, #8]
	MOV      r3, #2
	ADD      r0, r4, #0
	BL       |loc_0802A5EC|
	LDR      r0, [r4, #0x40]
	ADD      r5, #8
	SUB      r0, #1
	CMP      r0, r5
	BGT      |loc_0802A6D0|
|loc_0802A6FA|
	LDR      r0, [sp, #0x10]
	STR      r0, [r6]
	ADD      sp, #0x14
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	ADD      r3, r1, #0
	ADD      r1, r2, #0
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0xc
	CMP      r3, #0
	BEQ      |sub_0802A72A|
	CMP      r3, #0xb
	BEQ      |loc_0802A792|
	CMP      r3, #0xc
	BNE      |loc_0802A79C|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
