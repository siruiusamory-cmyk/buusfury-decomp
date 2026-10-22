	CODE16
|sub_0802724A|
	MOV      r2, #0
	STR      r2, [r1, #0x14]
	LDR      r0, [r1, #0x18]
	CMP      r0, r2
	BEQ      |loc_0802726A|
	STR      r2, [r1, #0x18]
	LDRH     r0, [r1, #0xc]
	LDR      r3, [pc, #0x4c]
	LDR      r1, [r1, #0x10]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	LSL      r2, r2, #6
	ADD      r1, r1, r2
	MOV      r2, #0x40
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0802726A|
	POP      {r3, pc}
	LDR      r2, [r1]
	ADD      r3, r2, #0
	ADD      r3, #8
	STR      r3, [r1]
	LDRB     r1, [r0, #0x1c]
	LDR      r3, [pc, #0x28]
	ADD      r3, #4
	LSL      r1, r1, #2
	LDR      r1, [r3, r1]
	STR      r1, [r2]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r2, #4]
	LSR      r1, r1, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r1, r1, #0xa
	ORR      r0, r1
	MOV      r1, #3
	LSL      r1, r1, #0xa
	BIC      r0, r1
	STR      r0, [r2, #4]
	MOV      r0, #0
	BX       lr
	LSL      r0, r0, #0
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	BCS      |loc_08027334|
	LSR      r4, r6, #1
	BVS      |loc_080272C0|
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
|loc_080272AC|
	PUSH     {r4, r5}
	LDRB     r2, [r0, #0x11]
	LDR      r1, [r0, #0x50]
	MOV      r3, #4
	LSL      r2, r2, #4
	ADD      r1, r1, r2
	LDRB     r2, [r0, #0x10]
	MOV      r4, #0x38
	LSL      r2, r2, #2
	ADD      r1, r1, r2
|loc_080272C0|
	LDR      r1, [r1, #4]
	STR      r1, [r0, #0x54]
	LDRB     r2, [r1, #6]
	LDRSB    r5, [r1, r3]
	LSR      r2, r2, #1
	SUB      r2, r4, r2
	SUB      r2, r2, r5
	STR      r2, [r0, #0x6c]
	LDRB     r2, [r1, #7]
	CMP      r2, #0x20
	BLS      |sub_080272E6|
	MOV      r3, #5
	LDRSB    r1, [r1, r3]
	LSR      r2, r2, #1
	SUB      r2, r4, r2
	SUB      r1, r2, r1
	STR      r1, [r0, #0x70]
	POP      {r4, r5}
	BX       lr
