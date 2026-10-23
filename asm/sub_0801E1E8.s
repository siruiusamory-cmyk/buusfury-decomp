	CODE16
|sub_0801E1E8|
	EXPORT |sub_0801E1E8|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x284]
	MOV      r1, #0xff
	ADD      r1, #0x35
	LDR      r5, [r0, r1]
	LDR      r7, [r0, #0x68]
	MOV      r0, #0xff
	ADD      r0, #0x15
	LDR      r0, [r0, r4]
	MOV      r3, #0x34
	LDR      r1, [pc, #0x278]
	MUL      r0, r3
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x30]
	MOV      r6, #1
	CMP      r0, #0
	SUB      sp, #0x14
	BNE      |loc_0801E210|
	MOV      r6, #0
|loc_0801E210|
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x4c
	STR      r2, [sp]
	MOV      r1, #1
	MOV      r0, #0
	STR      r1, [sp, #8]
	MOV      r2, #0
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	STR      r6, [r0, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r6, [pc, #0x244]
	MOV      r1, #0
	LDR      r2, [r6, #8]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x58
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
	MOV      r2, #0x4c
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
	MOV      r3, #0x58
	MOV      r0, #0
	STR      r7, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x1cc]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0xa9
	LSL      r2, r2, #7
	MOV      r1, #0
	LDR      r0, [pc, #0x1c4]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #2
	STR      r0, [sp, #4]
	MOV      r0, #5
	STR      r0, [sp, #8]
	MOV      r0, #0x1c
	STR      r0, [sp, #0xc]
	MOV      r0, #0x12
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	LDR      r2, [pc, #0x1b0]
	LDR      r1, [pc, #0x1a8]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0x1ac]
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
	BEQ      |loc_0801E30E|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0801E30E|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |inc_0x0158_0x143f2| + 0x6648
	POP      {r3, pc}
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x1fc
	SUB      sp, #0x1fc
	SUB      sp, #0x4c
	ADD      r6, sp, #0x3fc
	ADD      r6, #0x14
	ADD      r7, r0, #0
	MOV      r2, #0x68
	MOV      r1, #0xd0
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r0, r6, #0
	BL       |inc_0x0158_0x143f2| + 0x4f3e
	MOV      r0, #0xff
	ADD      r0, #0x15
	LDR      r0, [r0, r7]
	MOV      r3, #0x34
	LDR      r1, [pc, #0x138]
	MUL      r0, r3
	ADD      r5, r0, r1
	ADD      r4, r5, #0
	ADD      r4, #0xc
	LDR      r0, [r5, #0x18]
	ADD      r1, sp, #0x10
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r0, #0x10
	STR      r0, [sp]
	MOV      r0, #6
	STR      r0, [sp, #4]
	LDMIA    r4!, {r0, r1}
	ADD      r0, #0x10
	ADD      r1, #6
	STR      r1, [sp, #0xc]
	STR      r0, [sp, #8]
	SUB      r4, #8
	ADD      r0, r6, #0
	ADD      r1, sp, #0x10
	MOV      r2, sp
	BL       |inc_0x03d784_0x041118| + 0x219e
	MOV      r0, #1
	ADD      r3, sp, #0x3fc
	STRB     r0, [r3, #0x16]
	LDR      r0, [pc, #0x118]
	STR      r0, [r3, #0x34]
	MOV      r0, #0
	STRB     r0, [r3, #0x14]
	MOV      r0, #0xc
	STRB     r0, [r3, #0x15]
	LDR      r0, [pc, #0xf8]
	LDR      r0, [r0, #8]
	STR      r0, [r3, #0x20]
	MOV      r0, #5
	STRB     r0, [r3, #0x17]
	LDR      r0, [r4, #4]
	LDR      r1, [r4]
	LSR      r2, r0, #0x1f
	ADD      r0, r2, r0
	ASR      r0, r0, #1
	ADD      r0, #0xc
	STR      r0, [r3, #0x1c]
	ADD      r1, #0x12
	STR      r1, [r3, #0x18]
	LDRH     r0, [r5, #4]
	LDR      r1, [pc, #0xd4]
	LSL      r0, r0, #2
	LDR      r1, [r1, r0]
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r0, #0x75
	ADD      r3, sp, #0x3fc
	STRB     r0, [r3, #0x17]
	LDR      r0, [r4, #4]
	MOV      r1, #0x12
	ADD      r0, #0x12
	STR      r0, [r3, #0x1c]
	STR      r1, [r3, #0x18]
	LDRH     r0, [r5, #8]
	LDR      r1, [pc, #0xb4]
	LSL      r0, r0, #2
	LDR      r2, [r1, r0]
	MOV      r1, #0xb0
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x5e2
	ADD      r1, r6, #0
	ADD      r0, r7, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0xb0]
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x1fc
	ADD      sp, #0x1fc
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	LDR      r1, [pc, #0x8c]
	ADD      r4, r0, #0
	LDR      r0, [pc, #0xa0]
	LDR      r1, [r1, #4]
	MOV      r3, #0
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x9c]
	CMP      r2, #0
	BEQ      |loc_0801E416|
	CMP      r2, #1
	BNE      |loc_0801E438|
	ADD      r1, #0xff
	ADD      r1, #0xe1
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r4, pc}
|loc_0801E416|
	ADD      r1, #0xff
	ADD      r1, #0xed
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r4, #0xff
	ADD      r4, #1
	LDR      r0, [r4, #0x14]
	MOV      r3, #0x34
	LDR      r1, [pc, #0x4c]
	MUL      r0, r3
	ADD      r0, r0, r1
	BL       |loc_0801E14C|
	MOV      r0, #1
	BL       |inc_0x03d784_0x041118| + 0xf2
|loc_0801E438|
	MOV      r0, #0
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x38]
	MOV      r6, #1
	LDR      r1, [r0]
	MOV      r2, #0xc0
	LDRH     r1, [r1, #4]
	AND      r1, r2
	BEQ      |loc_0801E46E|
	LDR      r0, [r0, #4]
	MOV      r4, #0
	LDR      r7, [pc, #0x40]
	ADD      r3, r4, #0
	MOV      r2, #0x40
	ADD      r0, r0, r7
	LDR      r1, [pc, #0x40]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r1, [r0, #0xc]
	EOR      r1, r6
	ADD      r0, #0xc
	STMIA    r0!, {r1, r4}
|loc_0801E46E|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801E472|
	DCW      0x0000
	DCW      0xbce8,0x0806,0xd2f8,0x083b,0x07ec,0x0872,0xf800
|sub_0801E482|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	SUB      r3, r0, #6
	LSL      r0, r0, #0
	DCW      0xf5a5,0x0803
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	STR      r4, [sp, #0x1f0]
	LSR      r1, r6, #0x20
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r0, [pc, #0x290]
	LDR      r1, [sp, #0x24]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r2, [pc, #0x28c]
	LDR      r1, [pc, #0x28c]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x2250
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x280]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x24
	MOV      r1, #0
	STR      r1, [sp, #0x18]
	MOV      r1, #3
	MOV      r2, #1
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x78
	STR      r2, [sp, #0x10]
	SUB      r2, r1, #4
	SUB      r7, r1, #4
	STR      r1, [sp, #0xc]
	ADD      r4, r0, #0
	MOV      r1, #1
	MOV      r6, #1
	ADD      r3, r6, #0
	STR      r1, [sp]
	MOV      r0, #0x78
	STR      r2, [sp, #4]
	MOV      r2, #0
	STR      r0, [sp, #0x14]
	ADD      r1, r4, #0
	MOV      r0, #0
	STR      r7, [sp, #8]
	BL       |inc_0x049120_0x055620| + 0x7758
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0x34
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BEQ      |loc_0801E556|
	MOV      r2, #1
	MOV      r1, #1
	STR      r1, [sp, #0x18]
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x78
	MOV      r1, #4
	STR      r2, [sp, #0x10]
	SUB      r2, r1, #5
	STR      r1, [sp, #0xc]
	MOV      r1, #0
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r0, #0x86
	STR      r0, [sp, #0x14]
	MOV      r2, #1
	ADD      r1, r4, #0
	MOV      r3, #0
	ADD      r0, r5, #0
	STR      r7, [sp, #8]
	BL       |inc_0x0158_0x143f2| + 0x5f50
	LDR      r0, [pc, #0x200]
	STR      r0, [r5]
	STR      r6, [r5, #0x30]
|loc_0801E556|
	MOV      r0, #0xff
	ADD      r0, #0x15
	STR      r5, [r0, r4]
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0xe16
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [pc, #0x1d0]
	LDR      r0, [pc, #0x1d8]
	SUB      r1, #0x14
	LDR      r1, [r1, #4]
	MOV      r6, #0
	ADD      r5, r1, r0
	CMP      r2, #0
	LDR      r4, [pc, #0x1d0]
	BEQ      |sub_0801E5D4|
	MOV      r7, #0xff
	ADD      r7, #0x15
	CMP      r2, #1
	BEQ      |loc_0801E612|
	CMP      r2, #2
	BEQ      |loc_0801E64A|
	CMP      r2, #3
	BNE      |loc_0801E680|
	BL       |inc_0x03d784_0x041118| + 0x293e
	ADD      r1, r4, #0
	ADD      r3, r6, #0
	MOV      r2, #0x40
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r0, r7, #0
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801E5CC|
	LDR      r1, [pc, #0x1a8]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	STR      r6, [r1, #0x10]
	LDR      r1, [pc, #0x198]
	STR      r1, [r0]
|loc_0801E5CC|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
