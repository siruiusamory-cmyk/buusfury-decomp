	CODE16
|sub_08023770|
	SUB      r0, r2, #3
	CMP      r0, #5
	PUSH     {r3, lr}
	BCS      |loc_080237A0|
	ADD      r3, pc, #0x4
	LDRB     r3, [r3, r0]
	LSL      r3, r3, #1
	ADD      pc, r3
|loc_08023780|
	LSL      r2, r0, #8
	LSR      r7, r1, #0x1c
	LSL      r7, r1, #0
	LDR      r0, [pc, #0x3c]
	LDR      r0, [r0, #4]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BNE      |loc_080237A0|
	LDR      r1, [pc, #0x2c]
	MOV      r0, #1
	STR      r0, [r1]
|loc_080237A0|
	POP      {r3, pc}
	LSL      r0, r0, #0
	LSL      r4, r0, #0x16
	LSL      r0, r0, #0
	LSR      r4, r5, #0xb
	LSL      r0, r0, #0
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      r7, sp, #0x280
	LSR      r4, r0, #0x20
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	LSL      r4, r1, #0x10
	LSL      r0, r0, #0
|unk_080237BC|
	INCBIN	baserom.gba_0x237bc_0x237be.extracted
	LSR      r4, r0, #0x20
	STR      r4, [sp, #0x140]
	LSR      r4, r0, #0x20
|unk_080237C4|
	INCBIN	baserom.gba_0x237c4_0x237c6.extracted
	LSR      r2, r6, #1
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	PUSH     {r4, r6, lr}
	LSR      r4, r0, #0x20
	LDR      r3, [sp, #0xb0]
	LSR      r4, r0, #0x20
	LSR      r4, r5, #0x1d
	LSL      r0, r0, #0
	LDMIA    r2!, {r3, r5, r7}
	LSR      r4, r0, #0x20
	LSL      r4, r6, #0x17
	LSL      r0, r0, #0
	LSR      r4, r3, #0x1a
	LSL      r0, r0, #0
	LSR      r1, r5, #1
	LSR      r5, r0, #0x20
	LSL      r5, r6, #0x14
	LSR      r5, r0, #0x20
	LSR      r4, r0, #0x1c
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	MOV      r0, #0xff
	LDR      r7, [pc, #0x278]
	ADD      r0, #0x8d
	LDR      r3, [r7, r0]
	LDR      r6, [pc, #0x274]
	SUB      sp, #0x24
	LDR      r2, [r6]
	MOV      r1, #0
	STR      r1, [sp, #8]
	STR      r3, [sp]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	MOV      r3, #0x28
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0x2c
	STR      r0, [sp, #0x14]
	MOV      r2, #0
	STR      r2, [sp, #0x1c]
	MOV      r0, #1
	MOV      r1, #1
	STR      r1, [sp, #0x18]
	MOV      r2, #0x1c
	STR      r2, [sp, #0x10]
	MOV      r1, #0x61
	STR      r1, [sp, #0xc]
|unk_08023838|
	INCBIN	baserom.gba_0x23838_0x2383a.extracted
	MOV      r1, #2
	STR      r1, [sp]
	STR      r2, [sp, #4]
|unk_08023840|
	INCBIN	baserom.gba_0x23840_0x23842.extracted
	ADD      r1, r4, #0
	MOV      r2, #0
	STR      r0, [sp, #8]
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x870
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	STR      r0, [r5, #0x14]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	MOV      r1, #0
	MOV      r0, #0x2c
	STR      r0, [sp, #0x14]
	STR      r1, [sp, #0x18]
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x78
	MOV      r1, #0x62
	MOV      r0, #0
	MVN      r0, r0
	STR      r1, [sp, #0xc]
	STR      r2, [sp, #0x10]
	MOV      r2, #0
	MOV      r1, #2
	STR      r1, [sp]
	STR      r2, [sp, #4]
	ADD      r3, r0, #0
	ADD      r1, r4, #0
	MOV      r2, #1
	STR      r0, [sp, #8]
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x870
	ADD      r1, r0, #0
	STR      r0, [r5, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0xff
	ADD      r0, #0x91
	LDR      r3, [r7, r0]
	LDR      r2, [r6]
	MOV      r1, #0
	STR      r1, [sp, #8]
	STR      r3, [sp]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	MOV      r3, #0x52
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	MOV      r0, #0x56
	STR      r0, [sp, #0x14]
	STR      r2, [sp, #0x1c]
	MOV      r1, #0
	STR      r1, [sp, #0x18]
	MOV      r2, #0x1c
	MOV      r0, #4
	STR      r2, [sp, #0x10]
	MOV      r1, #0x65
	STR      r1, [sp, #0xc]
	SUB      r2, r0, #5
	MOV      r1, #9
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r2, #2
	ADD      r1, r4, #0
	STR      r0, [sp, #8]
	MOV      r3, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x870
	ADD      r1, r0, #0
	STR      r0, [r5, #0x1c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	MOV      r1, #1
	STR      r1, [sp, #0x18]
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x44
	MOV      r1, #0x66
	STR      r1, [sp, #0xc]
	STR      r2, [sp, #0x10]
	MOV      r0, #0x56
	STR      r0, [sp, #0x14]
	MOV      r2, #2
	MOV      r1, #9
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r0, #6
	STR      r0, [sp, #8]
	MOV      r2, #4
	ADD      r1, r4, #0
	MOV      r3, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x870
	ADD      r1, r0, #0
	STR      r0, [r5, #0x24]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	MOV      r1, #0
	STR      r1, [sp, #0x18]
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x6c
	MOV      r1, #0x67
	MOV      r0, #0x56
	STR      r0, [sp, #0x14]
	STR      r1, [sp, #0xc]
	STR      r2, [sp, #0x10]
	MOV      r2, #4
	MOV      r1, #9
	MOV      r0, #0
	MVN      r0, r0
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r2, #6
	ADD      r1, r4, #0
	STR      r0, [sp, #8]
	MOV      r3, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x870
	ADD      r1, r0, #0
	STR      r0, [r5, #0x2c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0x88
	STR      r0, [sp, #0x14]
	MOV      r2, #0
	STR      r2, [sp, #0x1c]
	MOV      r0, #0
	MVN      r0, r0
	MOV      r2, #0x9c
	STR      r2, [sp, #0x10]
	ADD      r2, r0, #0
	MOV      r1, #1
	STR      r1, [sp, #0x18]
	MOV      r1, #0x60
	STR      r1, [sp, #0xc]
	STR      r2, [sp]
	STR      r2, [sp, #4]
	MOV      r2, #9
	ADD      r1, r4, #0
	STR      r0, [sp, #8]
	MOV      r3, #2
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x870
	ADD      r1, r0, #0
	STR      r0, [r5, #0x38]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r0, [r7, #0x5c]
	STR      r0, [sp, #0x20]
	LDR      r0, [r7, #0x68]
	LDR      r1, [sp, #0x20]
	STR      r0, [sp, #0x1c]
	LDR      r0, [r6]
	BL       |inc_0x03d784_0x041118| + 0x2864
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	ADD      r7, r0, #0
	MOV      r2, #0x84
	STR      r2, [sp]
	MOV      r0, #0
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r2, #0
	ADD      r7, #0x1e
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r6]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	LDR      r2, [sp, #0x20]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r1, #1
	MOV      r2, #0x84
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r3, r7, #0
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r6]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	LDR      r2, [sp, #0x1c]
	STR      r1, [sp, #8]
	STR      r2, [sp]
	ADD      r2, r7, #0
	ADD      r2, #0x10
	MOV      r0, #5
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
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
	MOV      r0, #9
	STR      r0, [r5, #0xc]
	LDR      r0, [r6, #4]
	MOV      r3, #0
	STR      r3, [r0, #8]
	LDR      r1, [r6, #4]
	MOV      r0, #3
	STR      r0, [r1, #4]
	LDR      r1, [r6, #4]
	MOV      r0, #1
	STRB     r0, [r1]
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7284
	BL       |inc_0x03d784_0x041118| + 0x29dc
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	STMIA    r3!, {r2, r3, r6}
	LSR      r2, r6, #1
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r3, #1
	MOV      r2, #0x5f
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x65c0
	LDR      r1, [pc, #0x1e4]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	MOV      r5, #1
	CMP      r2, #0
	BEQ      |sub_08023AE4|
	CMP      r2, #1
	BNE      |loc_08023B50|
	MOV      r0, #0xbf
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_08023ADA|
	ADD      r3, r5, #0
	MOV      r2, #0xd
	MOV      r1, #0x5e
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x5308
	LDR      r0, [pc, #0x1b0]
	STR      r0, [r4]
	MOV      r0, #0xb
	LSL      r0, r0, #6
	ADD      r0, r4, r0
	STR      r5, [r0, #0x38]
|loc_08023ADA|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
