	CODE16
|sub_08016CCE|
	LSR      r3, r5, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      r4, sp, #0x2d0
	LSR      r4, r0, #0x20
	STR      r7, [sp, #0x160]
	LSR      r4, r0, #0x20
	STR      r5, [sp, #0x220]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x2c0]
	SUB      sp, #0x14
	LDR      r5, [r0, #0x5c]
	LDR      r7, [r0, #0x68]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x84
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
	LDR      r6, [pc, #0x29c]
	MOV      r1, #0
	LDR      r2, [r6, #8]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
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
	MOV      r2, #0x84
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
	MOV      r3, #0x90
	MOV      r0, #0
	STR      r7, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #8
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #6
	STR      r0, [sp, #4]
	MOV      r2, #6
	ADD      r1, r4, #0
	MOV      r3, #8
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #8
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #7
	STR      r0, [sp, #4]
	MOV      r2, #7
	ADD      r1, r4, #0
	MOV      r3, #0xd0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r1, [pc, #0x1d8]
	MOV      r0, #0x84
	LDR      r3, [r1, r0]
	LDR      r2, [r6, #8]
	STR      r3, [sp]
	MOV      r1, #0
	MOV      r5, #0x14
	ADD      r3, r5, #0
	STR      r1, [sp, #8]
	MOV      r0, #2
	STR      r2, [sp, #0xc]
	MOV      r2, #0x22
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r0, [pc, #0x1b0]
	MOV      r1, #2
	LDR      r3, [r0, #8]
	LDR      r2, [r6, #8]
	STR      r3, [sp]
	ADD      r3, r5, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	STR      r2, [sp, #0xc]
	MOV      r2, #0xce
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |loc_08016208|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r0, [r0, #0x14]
	MOV      r2, #0x12
	LSL      r0, r0, #4
	ADD      r0, #0x24
	STR      r0, [r1, #4]
	STR      r2, [r1]
	MOV      r0, #1
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x14c
	ADD      r4, sp, #0x114
	ADD      r6, r0, #0
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r7, #1
	ADD      r3, r7, #0
	MOV      r2, #0x24
	ADD      r1, r4, #0
	ADD      r0, r6, #0
	BL       |inc_0x0158_0x143f2| + 0x65c0
	MOV      r3, #0x56
	MOV      r2, #0x21
	MOV      r1, #0xa5
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x5058
	MOV      r3, #0xe0
	MOV      r2, #0x5e
	MOV      r1, #0x10
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x4ffc
	LDR      r0, [pc, #0x130]
	MOV      r3, #0x68
	LDR      r0, [r0, #0xc]
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r5, r0, r1
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x13b0e
	LDR      r0, [pc, #0x118]
	ADD      r3, sp, #0x100
	LDR      r0, [r0, #8]
	STR      r0, [sp, #0x120]
	MOV      r0, #0
	STRB     r0, [r3, #0x14]
	LDR      r0, [pc, #0x110]
	STRB     r7, [r3, #0x16]
	STR      r0, [sp, #0x134]
	MOV      r0, #0xaf
	STR      r0, [sp, #0x118]
	MOV      r0, #0x2d
	STR      r0, [sp, #0x11c]
	ADD      r0, r5, #0
	ADD      r0, #0x4c
	LDRH     r2, [r0]
	LDR      r7, [pc, #0xf4]
	MOV      r0, #0xdc
	LDR      r1, [r7, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x512
	MOV      r0, #0xaf
	STR      r0, [sp, #0x118]
	MOV      r0, #0x39
	STR      r0, [sp, #0x11c]
	ADD      r0, r5, #0
	ADD      r0, #0x4e
	LDRH     r2, [r0]
	MOV      r0, #0xe8
	LDR      r1, [r7, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x512
	MOV      r0, #0xaf
	STR      r0, [sp, #0x118]
	MOV      r0, #0x45
	STR      r0, [sp, #0x11c]
	ADD      r0, r5, #0
	ADD      r0, #0x50
	LDRH     r2, [r0]
	MOV      r0, #0xf4
	LDR      r1, [r7, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x512
	MOV      r0, #0xaf
	STR      r0, [sp, #0x118]
	MOV      r0, #0x51
	STR      r0, [sp, #0x11c]
	ADD      r0, r5, #0
	ADD      r0, #0x54
	LDRH     r2, [r0]
	MOV      r0, #0xff
	ADD      r0, #1
	LDR      r1, [r7, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x512
	ADD      r0, r6, #0
	ADD      r0, #0xff
	MOV      r4, #0
	ADD      r0, #1
	STR      r0, [sp, #0x148]
|loc_08016F1A|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	ADD      r0, #0x3c
	LDR      r0, [r0]
	MOV      r3, #0x2c
	LDR      r1, [pc, #0x94]
	MUL      r0, r3
	ADD      r6, r0, r1
	LSL      r7, r4, #4
	ADD      r0, r7, #0
	ADD      r0, #0x28
	MOV      r1, #0x22
	STR      r1, [sp, #0x118]
	STR      r0, [sp, #0x11c]
	LDRH     r0, [r6]
	LDR      r1, [pc, #0x74]
	LSL      r0, r0, #2
	LDR      r2, [r1, r0]
	MOV      r1, #0x7a
	ADD      r0, sp, #0x114
	BL       |inc_0x03d784_0x041118| + 0x540
	ADD      r0, r7, #0
	ADD      r0, #0x1c
	STR      r0, [sp, #0x108]
	MOV      r0, #0x20
	STR      r0, [sp, #0x10c]
	LDR      r0, [sp, #0x108]
	MOV      r1, #0x10
	ADD      r0, r0, r1
	STR      r1, [sp, #0x104]
	STR      r0, [sp, #0x110]
	ADD      r7, sp, #4
	ADD      r1, r7, #0
	LDR      r0, [r6, #0x10]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	ADD      r2, sp, #0x104
	ADD      r1, r7, #0
	ADD      r0, sp, #0x114
	BL       |inc_0x03d784_0x041118| + 0x219e
	LDR      r0, [sp, #0x148]
	LDR      r0, [r0, #0x14]
	CMP      r0, r4
	BNE      |loc_08016F94|
	MOV      r0, #0x13
	STR      r0, [sp, #0x118]
	MOV      r0, #0x6a
	STR      r0, [sp, #0x11c]
	MOV      r0, #0xc
	ADD      r3, sp, #0x100
	STRB     r0, [r3, #0x15]
	LDRH     r0, [r6, #2]
	LDR      r1, [pc, #0x28]
	LSL      r0, r0, #2
	LDR      r2, [r1, r0]
	MOV      r1, #0xcc
	ADD      r0, sp, #0x114
	BL       |inc_0x03d784_0x041118| + 0x5e2
|loc_08016F94|
	ADD      r4, #1
	CMP      r4, #4
	BLT      |loc_08016F1A|
	LDR      r1, [pc, #0x24]
	ADD      r0, sp, #0x114
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	ADD      r0, sp, #0x114
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x14c
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	STRH     r4, [r3, #0x16]
	LSR      r3, r5, #1
	DCW      0xf5a5,0x0803
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [pc, #0x138]
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x130]
	LDR      r1, [r1, #4]
	MOV      r3, #0
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x130]
	CMP      r2, #0
	BEQ      |sub_08017036|
	CMP      r2, #1
	BEQ      |loc_08017050|
	CMP      r2, #6
	BEQ      |loc_08017060|
	CMP      r2, #7
	BNE      |loc_08017074|
	ADD      r4, r3, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #0xff
	ADD      r0, #0x21
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801702E|
	LDR      r1, [pc, #0x10c]
	MOV      r2, #0xff
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r4, [r1, #0xc]
	STR      r4, [r1, #8]
	LDR      r3, [pc, #0x100]
	STR      r4, [r1, #0x10]
	ADD      r2, #0x15
	STR      r3, [r2, r0]
	LDR      r2, [pc, #0xfc]
	LDR      r3, [pc, #0xfc]
	STR      r2, [r0]
	ADD      r2, #0x38
	STR      r2, [r1, #0x14]
	LDRB     r2, [r3]
	ADD      r1, #0x18
	STRB     r2, [r1]
	LDRB     r2, [r3, #1]
	STRB     r2, [r1, #1]
	LDRB     r2, [r3, #2]
	STRB     r2, [r1, #2]
	LDRB     r2, [r3, #3]
	STRB     r2, [r1, #3]
|loc_0801702E|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
