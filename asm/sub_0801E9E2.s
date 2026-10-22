	CODE16
|sub_0801E9E2|
	LSR      r3, r7, #0x20
	LDR      r4, [r5, #0x20]
	LSR      r5, r0, #0x20
	LSR      r4, r3, #0x20
	LSR      r2, r6, #1
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	ADD      r6, sp, #0x2f0
	LSR      r4, r0, #0x20
	LDR      r3, [sp, #0xb0]
	LSR      r4, r0, #0x20
	LDR      r3, [sp]
	LSR      r4, r0, #0x20
	STMIA    r5!, {r2, r3, r4, r5, r6, r7}
	LSR      r7, r6, #1
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x2a8]
	SUB      sp, #0x24
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
	LDR      r6, [pc, #0x284]
	MOV      r1, #0
	LDR      r2, [r6, #4]
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
	LDR      r0, [r6, #4]
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
	LDR      r2, [r6, #4]
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
	MOV      r0, #0x78
	STR      r0, [sp, #0x14]
	MOV      r0, #1
	MOV      r1, #1
	STR      r1, [sp, #0x18]
	MOV      r1, #0x55
	MOV      r2, #0
	STR      r2, [sp, #0x1c]
	STR      r1, [sp, #0xc]
|unk_0801EAC2|
	INCBIN	baserom.gba_0x1eac2_0x1eac6.extracted
	MOV      r2, #0x40
	STR      r2, [sp, #0x10]
	STR      r1, [sp]
	ADD      r3, r5, #0
	ADD      r1, r4, #0
	MOV      r2, #0
	STR      r0, [sp, #8]
	MOV      r0, #0
	STR      r5, [sp, #4]
	BL       |inc_0x153f2_0x1a3f2| + 0x870
	ADD      r6, r4, #0
	ADD      r6, #0xff
	ADD      r6, #1
	STR      r0, [r6, #0x18]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	MOV      r1, #0
	MOV      r0, #0x78
	STR      r0, [sp, #0x14]
	STR      r1, [sp, #0x18]
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x82
	MOV      r1, #0x56
	ADD      r0, r5, #0
	STR      r1, [sp, #0xc]
	STR      r2, [sp, #0x10]
	MOV      r2, #0
	ADD      r1, r0, #0
	STR      r1, [sp]
	STR      r2, [sp, #4]
	ADD      r3, r5, #0
	ADD      r1, r4, #0
	MOV      r2, #1
	STR      r0, [sp, #8]
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x870
	ADD      r1, r0, #0
	STR      r0, [r6, #0x1c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0xe16
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7490
	BL       |inc_0x03d784_0x041118| + 0x29dc
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
|loc_0801EB40|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x75
	ADD      r6, r0, #0
	MOV      r3, #0x6e
	MOV      r2, #0x1e
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x5058
	MOV      r0, #2
	STRB     r0, [r4, #3]
	MOV      r0, #1
	STRB     r0, [r4, #2]
	LDR      r0, [pc, #0x168]
	MOV      r7, #0x16
	STR      r0, [r4, #0x20]
	MOV      r0, #0
	STRB     r0, [r4]
	MOV      r0, #0xe
	STRB     r0, [r4, #1]
	LDR      r0, [pc, #0x154]
	LDR      r1, [pc, #0x150]
	LDR      r0, [r0, #4]
	STR      r0, [r4, #0xc]
	STR      r7, [r4, #4]
	MOV      r0, #0x28
	STR      r0, [r4, #8]
	LSL      r0, r0, #3
	LDR      r1, [r1, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r5, #0
	ADD      r6, #0xff
	ADD      r6, #1
|loc_0801EB86|
	MOV      r1, #0x5d
	LDR      r0, [r6, #0x14]
	LSL      r1, r1, #5
	ADD      r0, r0, r1
	LDR      r0, [r0]
	CMP      r0, r5
	BLE      |loc_0801EBB6|
	LSL      r0, r5, #3
	SUB      r0, r0, r5
	LSL      r0, r0, #1
	ADD      r0, #0x36
	STR      r0, [r4, #8]
	STR      r7, [r4, #4]
	LDR      r0, [r6, #0x14]
	ADD      r0, r0, r1
	LSL      r1, r5, #3
	ADD      r0, r1, r0
	ADD      r0, #4
	ADD      r1, r4, #0
	BL       |sub_0801F810|
	ADD      r5, #1
	CMP      r5, #6
	BLT      |loc_0801EB86|
|loc_0801EBB6|
	MOV      r0, #0x28
	STR      r0, [r4, #8]
	MOV      r0, #0xff
	MOV      r7, #0x8c
	LDR      r1, [pc, #0xfc]
	STR      r7, [r4, #4]
	ADD      r0, #0x45
	LDR      r1, [r1, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r5, #0
|loc_0801EBCE|
	LDR      r1, [pc, #0xf8]
	LDR      r0, [r6, #0x14]
	ADD      r0, r0, r1
	LDR      r0, [r0]
	CMP      r0, r5
	BLE      |loc_0801EBFC|
	LSL      r0, r5, #3
	SUB      r0, r0, r5
	LSL      r0, r0, #1
	ADD      r0, #0x36
	STR      r0, [r4, #8]
	STR      r7, [r4, #4]
	LDR      r0, [r6, #0x14]
	ADD      r0, r0, r1
	LSL      r1, r5, #3
	ADD      r0, r1, r0
	ADD      r0, #4
	ADD      r1, r4, #0
	BL       |sub_0801F810|
	ADD      r5, #1
	CMP      r5, #6
	BLT      |loc_0801EBCE|
|loc_0801EBFC|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r4, r0, #0
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	MOV      r0, sp
	MOV      r5, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r3, #1
	MOV      r2, #0x4f
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x65c0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_0801EB40|
	LDR      r1, [pc, #0xa4]
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [pc, #0x84]
	ADD      r6, r0, #0
	LDR      r0, [pc, #0x90]
	LDR      r1, [r1]
	MOV      r3, #0
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x8c]
	CMP      r2, #0
	BEQ      |loc_0801EC60|
	CMP      r2, #1
	BNE      |loc_0801ECB8|
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
|loc_0801EC60|
	ADD      r5, r3, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r6, #0xff
	ADD      r6, #1
	LDR      r0, [r6, #0xc]
	MOV      r4, #1
	CMP      r0, #0
	BEQ      |loc_0801EC76|
	MOV      r4, #2
|loc_0801EC76|
	MOV      r0, #0xff
	ADD      r0, #0x1d
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801EC9E|
	LDR      r1, [pc, #0x54]
	LDR      r2, [pc, #0x54]
	STMIA    r0!, {r1, r5}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r5, [r1, #0xc]
	STR      r5, [r1, #8]
	STR      r5, [r1, #0x10]
	ADD      r1, #0x10
	STRB     r5, [r1, #4]
	STR      r2, [r0]
	STRB     r4, [r1, #8]
|loc_0801EC9E|
	BL       |inc_0x03d784_0x041118| + 0x11c
	CMP      r0, #1
	BLE      |loc_0801ECAE|
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
|loc_0801ECAE|
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7490
	BL       |inc_0x03d784_0x041118| + 0x29dc
|loc_0801ECB8|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|sub_0801ECBC|
|unk_0801ECBC|
	INCBIN	baserom.gba_0x1ecbc_0x1ecbe.extracted
