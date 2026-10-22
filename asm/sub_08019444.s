	CODE16
|sub_08019444|
	PUSH     {r4, lr}
	LDR      r0, [r1, #4]
	ADD      r4, r2, #0
	STR      r0, [r2]
	MOV      r0, #0
	STR      r0, [r1, #4]
	ADD      r0, r1, #0
	BEQ      |loc_08019460|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08019460|
	MOV      r1, #0xd
	ADD      r0, r4, #0
	BL       |sub_080193AE|
	POP      {r4, pc}
	LSL      r0, r0, #0
	STMIA    r0!, {r2, r6, r7}
	LSR      r4, r0, #0x20
	BGE      |loc_08019504|
	LSR      r7, r5, #1
	LDR      r1, [r1, #4]
	LDR      r0, [r0, #8]
	STR      r0, [r1, #0x1c]
	BX       lr
	PUSH     {r4, r5, lr}
	LDR      r1, [r1, #4]
	SUB      sp, #0xc
	ADD      r1, #0x24
	LDR      r4, [r1, #8]
	LDR      r5, [r1]
	LDR      r2, [r1, #0xc]
	SUB      r4, r4, r5
	LDR      r5, [r1, #4]
	STR      r4, [sp, #4]
	SUB      r2, r2, r5
	STR      r2, [sp, #8]
	ADD      r2, r4, #0
	ADD      r3, r0, #0
	ADD      r3, #0x14
	LDR      r4, [sp, #8]
	STMIA    r3!, {r2, r4}
	ADD      r4, r1, #0
	LDR      r1, [r1]
	LSL      r3, r1, #8
	LDR      r1, [r4, #4]
	LSL      r1, r1, #8
	STR      r1, [r0, #0x28]
	STR      r3, [r0, #0x24]
	LDR      r2, [r0, #0x10]
	ADD      r3, r0, #0
	STR      r2, [sp]
	ADD      r2, r0, #0
	ADD      r1, r0, #0
	ADD      r1, #8
	ADD      r2, #0x2c
	ADD      r3, #0x1c
	ADD      r0, r4, #0
	BL       |loc_080192CE|
	ADD      sp, #0xc
	POP      {r4, r5, pc}
	PUSH     {r4, r5}
	LDR      r3, [r0, #0x24]
	LDR      r4, [r0, #0x1c]
	SUB      sp, #8
	ADD      r3, r3, r4
	STR      r3, [r0, #0x24]
	LDR      r2, [r0, #0x20]
	LDR      r3, [r0, #0x28]
	ADD      r2, r3, r2
	STR      r2, [r0, #0x28]
	LDR      r2, [r0, #0x2c]
	SUB      r2, #1
	STR      r2, [r0, #0x2c]
	BNE      |loc_080194F2|
	LDR      r3, [r0, #8]
	LDR      r4, [r0, #0xc]
	LSL      r3, r3, #8
	LSL      r4, r4, #8
	MOV      r2, #1
	STR      r2, [r0, #0x30]
	STR      r3, [r0, #0x24]
	STR      r4, [r0, #0x28]
|loc_080194F2|
	LDR      r1, [r1, #4]
	LDR      r3, [r0, #0x24]
	LDR      r4, [r0, #0x28]
	ASR      r3, r3, #8
	STR      r3, [r1, #0x24]
	ASR      r4, r4, #8
	STR      r4, [r1, #0x28]
	ADD      r2, r1, #0
	ADD      r2, #0x24
|loc_08019504|
	ADD      r3, r2, #0
	LDR      r2, [r2, #4]
	LDR      r4, [r1, #0x24]
	LDR      r5, [r0, #0x14]
	LDR      r0, [r0, #0x18]
	ADD      r4, r4, r5
	ADD      r0, r2, r0
	STR      r0, [sp, #4]
	LDR      r2, [sp, #4]
	STR      r4, [sp]
	ADD      r3, #8
	STR      r2, [r3, #4]
	STR      r4, [r3]
	LDR      r0, [r1, #0x30]
	LDR      r2, [r1, #0x18]
	ADD      r0, r0, r2
	STR      r0, [r1, #4]
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
