	CODE16
|Blend_WriteControl1|
	PUSH     {r4, r5, r6, lr}
	MOV      r6, #1
	LSL      r6, r6, #9
	ADD      r2, r6, #0
	MOV      r1, #0
	SUB      sp, #0x10
	LDR      r0, [pc, #0xcc]
	BL       |inc_0x049120_0x055620| + 0xc
	ADD      r2, r6, #0
	MOV      r1, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r4, #0
	LSL      r5, r6, #0x11
	STRH     r4, [r5]
	STRH     r4, [r5, #0x10]
	STRH     r4, [r5, #0x12]
	STRH     r4, [r5, #0x14]
	STRH     r4, [r5, #0x16]
	STRH     r4, [r5, #0x18]
	STRH     r4, [r5, #0x1a]
	STRH     r4, [r5, #0x1c]
	LDR      r0, [pc, #0xa8]
	STRH     r4, [r5, #0x1e]
	STRH     r4, [r0, #0x10]
	LDR      r0, [pc, #0xa8]
	MOV      r1, #0
	STRH     r0, [r5, #0xa]
	LSL      r0, r0, #0x19
	LDR      r2, [pc, #0xa4]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0x1e
	STR      r0, [sp, #8]
	MOV      r0, #0x14
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	MOV      r2, #1
	STR      r4, [sp]
	STR      r4, [sp, #4]
	LDR      r1, [pc, #0x90]
	BL       |inc_0x03d784_0x041118| + 0x28c
	STRH     r6, [r5]
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |Blend_WriteControl1|
	ADD      r0, r4, #0
	BL       |loc_08005228|
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0x74]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x68]
	LDR      r0, [pc, #0x54]
	BL       |inc_0x049120_0x055620| + 0x24
	LDR      r0, [pc, #0x24]
	MOV      r1, #0xe1
	LDR      r2, [pc, #0x60]
	SUB      r0, #8
	LDR      r0, [r0, #4]
	LSL      r1, r1, #2
	ADD      r1, r1, r2
	LDRB     r2, [r0, #5]
	CMP      r2, #1
	BNE      |loc_0800540E|
	LDR      r2, [r0, #0xc]
	CMP      r2, r1
	BEQ      |loc_08005412|
|loc_0800540E|
	BL       |inc_0x03d784_0x041118| + 0x198c
|loc_08005412|
	POP      {r4, pc}
|loc_08005414|
	DCW      0xe3d4
	DCW      0x083b,0x6a2c,0x0805,0x61cc,0x0805,0x0040,0x0600,0xd82c
	DCW      0x0804,0x05c4,0x0000,0x9488,0x0831,0x920c,0x0804,0xbf28
	DCW      0x0804,0xa430,0x0804,0x1914,0x0300,0x9b00,0x0804,0x0200
	DCW      0x0500,0x0040,0x0400,0x1e83,0x0000,0x9640,0x0000,0xf000
	DCW      0x0600,0x652c,0x0805,0xb78c
|loc_0800545E|
	LSR      r3, r7, #0x20
