	CODE16
|sub_0800DA92|
	PUSH     {r4}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	LDR      r4, [pc, #0x234]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	LDR      r2, [r0, #0x10]
	STR      r2, [r1]
	LDR      r3, [r0, #0x28]
	AND      r2, r4
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x2c]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRB     r2, [r0, #8]
	LDR      r3, [r1, #4]
	MOV      r4, #3
	LSL      r2, r2, #0x1a
	LSR      r2, r2, #0x1e
	LSL      r4, r4, #0xa
	BIC      r3, r4
	LSL      r2, r2, #0xa
	ORR      r2, r3
	STR      r2, [r1, #4]
	LDRH     r0, [r0, #0xc]
	LSR      r2, r2, #0xa
	LSL      r2, r2, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	ORR      r0, r2
	STR      r0, [r1, #4]
	POP      {r4}
	MOV      r0, #0
	BX       lr
	ADD      r3, r1, #0
	PUSH     {r4, r5}
	LDR      r4, [r3]
	LDR      r3, [r3, #4]
	SUB      sp, #8
	STR      r3, [r0, #0x1c]
	STR      r4, [r0, #0x18]
	ADD      r1, r0, #0
	ADD      r1, #0x18
	LDR      r2, [r0, #0x14]
	ADD      r3, r1, #0
	LDR      r1, [r0, #0x1c]
	LDR      r5, [r2]
	LDR      r2, [r2, #4]
	ADD      r3, #8
	ADD      r4, r4, r5
	ADD      r1, r1, r2
	STR      r1, [sp, #4]
	LDR      r2, [sp, #4]
	STR      r4, [sp]
	STR      r2, [r3, #4]
	STR      r4, [r3]
	LDR      r1, [r0, #0x24]
	STR      r1, [r0, #4]
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BNE      |loc_0800DB36|
	CMP      r4, #8
	BLT      |loc_0800DB36|
	MOV      r0, #2
	POP      {r4, pc}
|loc_0800DB36|
	CMP      r4, #9
	BLT      |sub_0800DB3E|
	MOV      r0, #2
	POP      {r4, pc}
