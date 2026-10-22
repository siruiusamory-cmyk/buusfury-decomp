	CODE16
|sub_0801D15C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x2a4]
	SUB      sp, #0x14
	LDR      r5, [r0, #0x5c]
	LDR      r7, [r0, #0x68]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x44
	STR      r2, [sp]
	MOV      r0, #0
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r2, #0
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	MOV      r1, #0xff
	ADD      r1, #0x1d
	STR      r0, [r1, r4]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r6, [pc, #0x268]
	MOV      r1, #0
	LDR      r2, [r6, #8]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x50
	MOV      r0, #0
	STR      r5, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r5, #0
	LDR      r0, [r6, #8]
	BL       |inc_0x03d784_0x041118| + 0x2864
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	ADD      r5, r0, #0
	MOV      r1, #1
	ADD      r5, #0x1e
	MOV      r2, #0x44
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
	LDR      r2, [r6, #8]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	ADD      r2, r5, #0
	ADD      r2, #0x10
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x50
	MOV      r0, #0
	STR      r7, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0xe16
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x1ec]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #9
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x1e4]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #3
	STR      r0, [sp, #4]
	MOV      r0, #5
	STR      r0, [sp, #8]
	MOV      r0, #0x1b
	STR      r0, [sp, #0xc]
	MOV      r0, #0x11
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	LDR      r2, [pc, #0x1d0]
	LDR      r1, [pc, #0x1c8]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0x1cc]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
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
	BEQ      |loc_0801D27A|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0801D27A|
	POP      {r3, pc}
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r0, [r0, #0xc]
	MOV      r2, #0x12
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r0, #0x1f
	STR      r0, [r1, #4]
	STR      r2, [r1]
	MOV      r0, #1
	BX       lr
	PUSH     {r0, r4, r5, r6, r7, lr}
	SUB      sp, #0x138
	ADD      r4, sp, #0x104
	MOV      r2, #0x60
	MOV      r1, #0xc0
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x4f3e
	LDR      r5, [pc, #0x150]
	ADD      r3, sp, #0x100
	LDR      r0, [r5, #8]
	LDR      r1, [pc, #0x14c]
	STR      r0, [sp, #0x110]
	MOV      r0, #0
	STRB     r0, [r3, #4]
	MOV      r0, #1
	STRB     r0, [r3, #6]
	LDR      r0, [pc, #0x15c]
	STR      r0, [sp, #0x124]
	MOV      r0, #5
	STRB     r0, [r3, #7]
	LDR      r6, [sp, #0x138]
	MOV      r3, #0x2c
	ADD      r6, #0xff
	ADD      r6, #1
	LDR      r0, [r6, #0x18]
	MUL      r0, r3
	ADD      r7, r0, r1
	LDR      r0, [r7, #0x10]
	ADD      r1, sp, #4
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r2, [pc, #0x120]
	ADD      r1, sp, #4
	ADD      r2, #0x20
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x219e
	MOV      r0, #0x22
	STR      r0, [sp, #0x108]
	MOV      r0, #0x13
	STR      r0, [sp, #0x10c]
	LDRH     r0, [r7]
	LDR      r3, [pc, #0x114]
	LSL      r0, r0, #2
	LDR      r1, [r3, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	LDR      r0, [r6, #0x24]
	LDR      r4, [r6, #0xc]
	CMP      r0, #0
	BNE      |loc_0801D306|
	ADD      r4, #1
|loc_0801D306|
	LDR      r1, [r6, #0x28]
	CMP      r1, #0
	BNE      |loc_0801D312|
	CMP      r4, #1
	BLT      |loc_0801D312|
	ADD      r4, #1
|loc_0801D312|
	LDR      r1, [pc, #0xe8]
	CMP      r0, #0
	LDR      r5, [r1, #0x1c]
	LDR      r7, [r1, #0x18]
	BEQ      |loc_0801D368|
	STR      r7, [sp, #0x108]
	STR      r5, [sp, #0x10c]
	LDR      r2, [r6, #0x20]
	MOV      r1, #0x75
	CMP      r2, #0
	ADD      r0, sp, #0x104
	BEQ      |loc_0801D332|
	MOV      r1, #6
	CMP      r4, #0
	BEQ      |loc_0801D332|
	MOV      r1, #2
|loc_0801D332|
	ADD      r3, sp, #0x100
	STRB     r1, [r3, #7]
	LDR      r1, [pc, #0xc4]
	MOV      r3, #0x68
	LDR      r1, [r1, #0xc]
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1, #0x14]
	LDR      r2, [pc, #0xb8]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDRH     r1, [r1, #2]
	LDR      r3, [pc, #0xb0]
	LSL      r1, r1, #2
	LDR      r2, [r3, r1]
	MOV      r1, #0xff
	ADD      r1, #0x19
	LDR      r1, [r3, r1]
	BL       |inc_0x03d784_0x041118| + 0x512
	ADD      r5, #0xc
|loc_0801D368|
	LDR      r0, [r6, #0x28]
	CMP      r0, #0
	BEQ      |loc_0801D3B8|
	MOV      r1, #6
	CMP      r4, #1
	ADD      r0, sp, #0x104
	STR      r7, [sp, #0x108]
	STR      r5, [sp, #0x10c]
	BEQ      |loc_0801D37C|
	MOV      r1, #2
|loc_0801D37C|
	ADD      r3, sp, #0x100
	STRB     r1, [r3, #7]
	LDR      r2, [r6, #0x30]
	MOV      r3, #0x68
	LDR      r2, [r2]
	LDR      r1, [pc, #0x74]
	LSR      r2, r2, #0x1c
	SUB      r2, #1
	LDR      r1, [r1, #0xc]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1, #0x14]
	LDR      r2, [pc, #0x68]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDRH     r1, [r1, #2]
	LDR      r3, [pc, #0x60]
	LSL      r1, r1, #2
	LDR      r2, [r3, r1]
	MOV      r1, #0xff
	ADD      r1, #0x1d
	LDR      r1, [r3, r1]
	BL       |inc_0x03d784_0x041118| + 0x512
	ADD      r5, #0xc
|loc_0801D3B8|
	MOV      r1, #6
	CMP      r4, #2
	ADD      r0, sp, #0x104
	STR      r7, [sp, #0x108]
	STR      r5, [sp, #0x10c]
	BEQ      |loc_0801D3C6|
	MOV      r1, #2
|loc_0801D3C6|
	ADD      r3, sp, #0x100
	STRB     r1, [r3, #7]
	MOV      r1, #0xff
	ADD      r1, #0x21
	LDR      r3, [pc, #0x38]
	ADD      r4, r0, #0
	LDR      r1, [r3, r1]
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r1, r4, #0
	LDR      r0, [sp, #0x138]
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x2c]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	ADD      r0, sp, #0x104
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x13c
	POP      {r4, r5, r6, r7, pc}
|sub_0801D3F4|
	DCW      0x920c
	DCW      0x0804,0xafcc,0x0804,0xe9a8,0x0871,0x82ec,0x086f,0x82ec
	DCW      0x086b,0xbce8,0x0806,0xf800
|sub_0801D40E|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	SUB      r3, r0, #6
	LSL      r0, r0, #0
	DCW      0xf5a5,0x0803
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x1c0]
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1b8]
	LDR      r1, [r7, #4]
	MOV      r3, #0
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x1b8]
	CMP      r2, #0
	SUB      sp, #0x24
	BEQ      |sub_0801D44C|
	CMP      r2, #1
	BNE      |loc_0801D50A|
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #3
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
