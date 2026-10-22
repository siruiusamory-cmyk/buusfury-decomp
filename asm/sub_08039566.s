	CODE16
|sub_08039566|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	DCW      0xf5a5,0x0803
	ADD      r7, sp, #0xc0
	LSR      r7, r6, #1
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1bc]
	SUB      sp, #0x14
	LDR      r5, [r0, #0x64]
	LDR      r6, [r0, #0x68]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x3c
	STR      r2, [sp]
	MOV      r0, #0
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r2, #0
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r0, [pc, #0x198]
	MOV      r1, #0
	LDR      r2, [r0, #8]
	MOV      r7, #0x48
	ADD      r3, r7, #0
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r0, #0
	STR      r5, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r0, [pc, #0x170]
	ADD      r1, r5, #0
	LDR      r0, [r0, #8]
	BL       |inc_0x03d784_0x041118| + 0x2864
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	ADD      r5, r0, #0
	MOV      r1, #1
	ADD      r5, #0x1e
	MOV      r2, #0x3c
	STR      r2, [sp]
	ADD      r3, r5, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r0, [pc, #0x140]
	MOV      r1, #0
	LDR      r2, [r0, #8]
	STR      r1, [sp, #8]
	STR      r2, [sp, #0xc]
	ADD      r2, r5, #0
	ADD      r2, #0x10
	MOV      r0, #5
	ADD      r3, r7, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	MOV      r0, #0
	STR      r6, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x118]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x37
	LSL      r2, r2, #8
	MOV      r1, #0
	LDR      r0, [pc, #0x110]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #5
	STR      r0, [sp, #4]
	STR      r0, [sp, #8]
	MOV      r0, #0x19
	STR      r0, [sp, #0xc]
	MOV      r0, #0x10
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	LDR      r2, [pc, #0x100]
	LDR      r1, [pc, #0xf4]
	BL       |inc_0x03d784_0x041118| + 0x28c
	MOV      r1, #0x3f
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	LSL      r1, r1, #7
	STRH     r1, [r0, #8]
	LDRH     r1, [r0]
	LSR      r2, r0, #0x12
	ORR      r1, r2
	STRH     r1, [r0]
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	MOV      r3, #1
	LSL      r3, r3, #0x1a
	LDRH     r1, [r3]
	LSR      r2, r3, #0x12
	BIC      r1, r2
	STRH     r1, [r3]
	CMP      r0, #0
	BEQ      |loc_0803968A|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0803968A|
	POP      {r3, pc}
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x34
	ADD      r7, r0, #0
	MOV      r2, #0x58
	MOV      r1, #0xa0
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x4f3e
	MOV      r0, #1
	ADD      r3, sp, #0
	STRB     r0, [r3]
	STRB     r0, [r3, #2]
	LDR      r0, [pc, #0xa4]
	LDR      r5, [pc, #0x94]
	STR      r0, [sp, #0x20]
	MOV      r0, #0x50
	STR      r0, [sp, #4]
	MOV      r0, #0x14
	STR      r0, [sp, #8]
	LDR      r0, [r5, #4]
	LDR      r6, [pc, #0x80]
	STR      r0, [sp, #0xc]
	MOV      r0, #3
	STRB     r0, [r3, #3]
	LDR      r1, [r6, #0x2c]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	LDR      r0, [r5, #8]
	ADD      r3, sp, #0
	STR      r0, [sp, #0xc]
	MOV      r0, #0x50
	STR      r0, [sp, #4]
	MOV      r0, #0x2c
	STR      r0, [sp, #8]
	MOV      r0, #0xc
	STRB     r0, [r3, #1]
	MOV      r0, #2
	STRB     r0, [r3, #3]
	MOV      r1, #0x84
	ADD      r0, r4, #0
	LDR      r2, [r6, #0x6c]
	BL       |inc_0x03d784_0x041118| + 0x5e2
	ADD      r1, r4, #0
	ADD      r0, r7, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x54]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
	LDR      r1, [pc, #0x38]
	PUSH     {r3, lr}
	LDR      r1, [r1]
	LDR      r0, [pc, #0x48]
	MOV      r3, #0
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x44]
	CMP      r2, #0
	BEQ      |sub_0803972E|
	CMP      r2, #1
	BNE      |loc_0803973A|
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r3, pc}
