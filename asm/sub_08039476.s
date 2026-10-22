	CODE16
|sub_08039476|
	LSL      r0, r0, #0
	ADD      r2, #0xb0
	LSL      r0, r0, #0xc
	MOV      r2, #1
	LSL      r2, r2, #0xb
	PUSH     {lr}
	SUB      sp, #0x14
	MOV      r1, #0
	LDR      r0, [pc, #0xdc]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0xf
	LSL      r2, r2, #8
	MOV      r1, #0
	LDR      r0, [pc, #0xd4]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #9
	STR      r0, [sp, #4]
	MOV      r0, #8
	STR      r0, [sp, #8]
	MOV      r0, #0x15
	STR      r0, [sp, #0xc]
	MOV      r0, #0xd
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	LDR      r2, [pc, #0xc0]
	LDR      r1, [pc, #0xb4]
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
	POP      {pc}
	PUSH     {r3, lr}
	MOV      r3, #1
	LSL      r3, r3, #0x1a
	LDRH     r1, [r3]
	LSR      r2, r3, #0x12
	BIC      r1, r2
	STRH     r1, [r3]
	CMP      r0, #0
	BEQ      |loc_080394E6|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080394E6|
	POP      {r3, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0x28
	MOV      r1, #0x60
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x4f3e
	MOV      r0, #1
	ADD      r3, sp, #0
	STRB     r0, [r3]
	STRB     r0, [r3, #2]
	LDR      r0, [pc, #0x64]
	STR      r0, [sp, #0x20]
	LDR      r0, [pc, #0x64]
	LDR      r0, [r0]
	STR      r0, [sp, #0xc]
	MOV      r0, #0x30
	STR      r0, [sp, #4]
	MOV      r0, #0x14
	STR      r0, [sp, #8]
	MOV      r0, #2
	STRB     r0, [r3, #3]
	LDR      r0, [pc, #0x58]
	LDR      r1, [r0, #0x20]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x34]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	ADD      r2, r0, #0
	PUSH     {r3, lr}
	LDR      r3, [r1, #0x20]
	LDR      r0, [pc, #0x20]
	LDR      r1, [r1, #0x14]
	ADD      r2, #0xff
	ADD      r2, #0x19
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x480a
	MOV      r0, #1
	POP      {r3, pc}
|sub_08039562|
|unk_08039562|
	INCBIN	baserom.gba_0x39562_0x39566.extracted
