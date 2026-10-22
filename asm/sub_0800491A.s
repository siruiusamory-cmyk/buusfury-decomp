	CODE16
|sub_0800491A|
	PUSH     {r4, r5, r6, lr}
	LDR      r3, [pc, #0x1dc]
	ADD      r6, r0, #0
	ADD      sp, r3
	ADD      r4, sp, #0xc
	ADD      r5, r1, #0
	ADD      r0, r4, #0
	BL       |loc_08004838|
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x719c
	LDR      r1, [pc, #0x1ac]
	ADD      r0, sp, #0xc
	BL       |inc_0x03d784_0x041118| + 0x24ca
	MOV      r1, #0x11
	LSL      r1, r1, #7
	ADD      r1, r4, r1
	STR      r0, [r1, #0x28]
	MOV      r1, #0x8b
	LSL      r1, r1, #4
	MUL      r1, r5
	LDR      r0, [pc, #0x1a8]
	MOV      r3, #0x8b
	LSL      r3, r3, #4
	ADD      r1, #0x10
	ADD      r2, r4, #0
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x245a
	MOV      r3, #0x23
	LSL      r3, r3, #6
	ADD      sp, r3
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r4, [pc, #0x188]
	LDR      r6, [pc, #0x18c]
	ADD      sp, r4
	ADD      r4, r0, #0
	LDR      r0, [r6, #8]
	ADD      r7, r1, #0
	LDRB     r1, [r0]
	MOV      r0, #0x45
	LSL      r0, r0, #5
	ADD      r0, r4, r0
	STRB     r1, [r0]
	LDR      r1, [r6, #8]
	ADD      r5, r3, #0
	LDRB     r1, [r1, #1]
	STRB     r1, [r0, #1]
	LDR      r1, [r6, #8]
	LDRB     r1, [r1, #2]
	STRB     r1, [r0, #2]
	LDR      r1, [r2]
	STRH     r1, [r0, #4]
	LDR      r1, [r2, #4]
	STRH     r1, [r0, #6]
	LDRB     r0, [r4, #1]
	MOV      r1, #1
	ORR      r0, r1
	MOV      r1, #8
	CMP      r5, #0
	STRB     r0, [r4, #1]
	BEQ      |loc_080049A4|
	ORR      r0, r1
	STRB     r0, [r4, #1]
	B        |loc_080049A8|
|loc_080049A4|
	BIC      r0, r1
	STRB     r0, [r4, #1]
|loc_080049A8|
	MOV      r5, sp
	MOV      r0, sp
	BL       |loc_08004838|
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x719c
	LDR      r0, [pc, #0x144]
	LDR      r1, [r0, #4]
	MOV      r0, #0x13
	LSL      r0, r0, #6
	ADD      r0, r5, r0
	LDR      r2, [r0, #0x10]
	ADD      r1, r1, r2
	STR      r1, [r0, #0x10]
	LDR      r1, [pc, #0x118]
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x24ca
	MOV      r1, #0x11
	LSL      r1, r1, #7
	ADD      r1, r5, r1
	STR      r0, [r1, #0x28]
	MOV      r1, #0x8b
	LSL      r1, r1, #4
	MUL      r1, r7
	MOV      r3, #0x8b
	LSL      r3, r3, #4
	ADD      r1, #0x10
	ADD      r2, r5, #0
	LDR      r0, [r6]
	BL       |inc_0x03d784_0x041118| + 0x245a
	LDR      r4, [pc, #0x108]
	ADD      sp, r4
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r3, [pc, #0x104]
	ADD      r6, r0, #0
	ADD      sp, r3
	ADD      r4, sp, #0xc
	ADD      r5, r1, #0
	ADD      r0, r4, #0
	BL       |loc_08004838|
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x719c
	LDR      r1, [pc, #0xd4]
	ADD      r0, sp, #0xc
	BL       |inc_0x03d784_0x041118| + 0x24ca
	MOV      r1, #0x11
	LSL      r1, r1, #7
	ADD      r1, r4, r1
	STR      r0, [r1, #0x28]
	MOV      r1, #0x8b
	LSL      r1, r1, #4
	MUL      r1, r5
	LDR      r0, [pc, #0xd0]
	MOV      r3, #0x8b
	LSL      r3, r3, #4
	ADD      r1, #0x10
	ADD      r2, r4, #0
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x245a
	MOV      r3, #0x23
	LSL      r3, r3, #6
	ADD      sp, r3
	POP      {r4, r5, r6, pc}
