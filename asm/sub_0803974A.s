	CODE16
|sub_0803974A|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	DCW      0xf5a5,0x0803
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	MOV      r2, #1
	LSL      r2, r2, #0xb
	PUSH     {lr}
	SUB      sp, #0x14
	MOV      r1, #0
	LDR      r0, [pc, #0xd0]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #5
	LSL      r2, r2, #0xa
	MOV      r1, #0
	LDR      r0, [pc, #0xc8]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #7
	STR      r0, [sp, #4]
	MOV      r0, #8
	STR      r0, [sp, #8]
	MOV      r0, #0x17
	STR      r0, [sp, #0xc]
	MOV      r0, #0xd
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	LDR      r2, [pc, #0xb4]
	LDR      r1, [pc, #0xa8]
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
	BEQ      |loc_080397CA|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080397CA|
	POP      {r3, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0x28
	MOV      r1, #0x80
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x4f3e
	MOV      r0, #1
	ADD      r3, sp, #0
	STRB     r0, [r3]
	STRB     r0, [r3, #2]
	LDR      r0, [pc, #0x58]
	LDR      r1, [pc, #0x60]
	STR      r0, [sp, #0x20]
	LDR      r0, [pc, #0x58]
	LDR      r0, [r0, #4]
	STR      r0, [sp, #0xc]
	MOV      r0, #0x40
	STR      r0, [sp, #4]
	MOV      r0, #0x14
	STR      r0, [sp, #8]
	MOV      r0, #2
	STRB     r0, [r3, #3]
	MOV      r0, #0xff
	ADD      r0, #0x29
	LDR      r1, [r1, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x24]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	LDR      r0, [pc, #0x1c]
	LDR      r1, [r0]
	MOV      r0, #1
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x16
	BNE      |loc_0803983A|
	MOV      r0, #0
|loc_0803983A|
	BX       lr
|sub_0803983C|
|unk_0803983C|
	INCBIN	baserom.gba_0x3983c_0x3983e.extracted
