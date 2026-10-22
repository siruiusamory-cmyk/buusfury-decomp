	CODE16
|Bg_WriteControl0AndMosaic2|
	LDR      r1, [pc, #0x60]
	MOV      r0, #0
	STRB     r0, [r1, #0xc]
	STRB     r0, [r1, #0xd]
	MOV      r0, #0x37
	MVN      r0, r0
	LDRH     r1, [r0, r1]
	MOV      r0, #0x40
	LDR      r2, [pc, #0x54]
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r0, r1
	STRH     r0, [r2]
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r0, #5
	MOV      r1, #0
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	LDR      r0, [pc, #0x28]
	BL       |inc_0x049120_0x055620| + 0xc
	ADD      r0, r4, #0
	BEQ      |loc_0802CAA0|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802CAA0|
	POP      {r4, pc}
	LSL      r0, r0, #0
	LSL      r0, r0, #1
	LSL      r0, r0, #0x10
	LSL      r0, r1, #0
	LSL      r0, r0, #0x10
	STR      r4, [r5, #0x30]
	LSR      r5, r0, #0x20
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	LSL      r0, r0, #8
	LSL      r0, r0, #0x14
	PUSH     {r4, r5}
	LDR      r1, [r1, #4]
	LDR      r4, [r0, #8]
	LDR      r5, [r1, #0x24]
	SUB      sp, #8
	SUB      r4, r4, r5
	LDR      r5, [r0, #0xc]
	LDR      r3, [r1, #0x28]
	STR      r4, [sp]
	SUB      r3, r5, r3
	STR      r3, [sp, #4]
	ADD      r3, r4, #0
	ADD      r2, r1, #0
	ADD      r2, #0x2c
	LDR      r4, [sp, #4]
	LDR      r5, [r2]
	ADD      r3, r5, r3
	STR      r3, [r2]
	LDR      r3, [r2, #4]
	ADD      r3, r3, r4
	STR      r3, [r2, #4]
	LDR      r2, [r0, #8]
	LDR      r0, [r0, #0xc]
	STR      r0, [r1, #0x28]
	STR      r2, [r1, #0x24]
	LDR      r0, [r1, #0x30]
	LDR      r2, [r1, #0x18]
	ADD      r0, r0, r2
	STR      r0, [r1, #4]
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
|sub_0802CAF8|
|unk_0802CAF8|
		MOV r2, #0
