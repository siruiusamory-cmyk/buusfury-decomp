	CODE16
|sub_08029014|
	EXPORT |sub_08029014|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x2a0]
	SUB      sp, #0x10
	LDR      r5, [r0, #0x68]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r1, #1
	MOV      r2, #0x4c
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r3, #0xc
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r6, [pc, #0x27c]
	MOV      r1, #0
	LDR      r2, [r6, #4]
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
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x258]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0xa9
	LSL      r2, r2, #7
	MOV      r1, #0
	LDR      r0, [pc, #0x250]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #2
	STR      r0, [sp]
	MOV      r0, #5
	STR      r0, [sp, #4]
	MOV      r0, #0x1c
	STR      r0, [sp, #8]
	MOV      r0, #0x12
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	LDR      r2, [pc, #0x23c]
	LDR      r1, [pc, #0x230]
	BL       |inc_0x03d784_0x041118| + 0x28c
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	LDR      r1, [r5, #0x14]
	MOV      r3, #0x68
	LDR      r0, [r6, #8]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDR      r1, [r5, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x1344a
	LDRB     r0, [r0]
	CMP      r0, #0xff
	BEQ      |loc_08029104|
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x4d
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #4
	STR      r0, [sp, #4]
	MOV      r2, #4
	ADD      r1, r4, #0
	MOV      r3, #0x8c
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	STR      r0, [r5, #0x1c]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x4d
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #5
	STR      r0, [sp, #4]
	MOV      r2, #5
	ADD      r1, r4, #0
	MOV      r3, #0xb4
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	STR      r0, [r5, #0x20]
	LDR      r1, [r5, #0x1c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r0, r4, #0
	LDR      r1, [r5, #0x20]
	BL       |inc_0x0158_0x143f2| + 0x64f6
|loc_08029104|
	LDR      r1, [pc, #0x1c8]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #8]
	LDRH     r1, [r0]
	LSR      r2, r0, #0x12
	ORR      r1, r2
	STRH     r1, [r0]
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	MOV      r3, #1
	LSL      r3, r3, #0x1a
	LDRH     r1, [r3]
	LSR      r2, r3, #0x12
	BIC      r1, r2
	STRH     r1, [r3]
	CMP      r0, #0
	BEQ      |loc_08029136|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08029136|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	ADD      r1, r0, #0
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x17c]
	ADD      r0, #0xc
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r1, #0
	MOV      r6, #0xff
	ADD      r6, #1
|loc_0802914E|
	ADD      r0, r1, #3
	ADD      r2, r6, #0
	CMP      r0, #8
	BGE      |loc_08029158|
	MOV      r2, #0
|loc_08029158|
	LSL      r0, r0, #0x1d
	LSR      r0, r0, #0x1a
	ADD      r2, r0, r2
	LSL      r3, r1, #1
	ADD      r3, r3, r1
	MOV      r0, #0
	LSL      r3, r3, #3
	MOV      ip, r3
|loc_08029168|
	ADD      r3, r0, #3
	ASR      r7, r3, #3
	LSL      r3, r3, #0x1d
	LSR      r3, r3, #0x1d
	LSL      r7, r7, #6
	ADD      r3, r3, r7
	LDR      r7, [r5, #4]
	ADD      r3, r3, r2
	LDRB     r3, [r7, r3]
	MOV      r7, ip
	ADD      r7, r7, r0
	ADD      r7, r7, r4
	ADD      r7, #0x30
	ADD      r0, #1
	CMP      r0, #0x10
	STRB     r3, [r7, #4]
	BLT      |loc_08029168|
	ADD      r1, #1
	CMP      r1, #8
	BLT      |loc_0802914E|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08029192|
|unk_08029192|
		PUSH {r0, r4, r5, r6, r7, lr}
		SUB sp, #0x150
		ADD r7, sp, #0x11c
		MOV r2, #0x68
		MOV r1, #0xd0
		ADD r0, r7, #0
		BL       |loc_0803F540|
		ADD r0, r7, #0
		BL       |inc_0x0158_0x143f2| + 0x4f3e
		LDR r0, [pc, #0x114]
		MOV r3, #0x68
		LDR r0, [r0, #8]
		LDR r4, [sp, #0x150]
		ADD r4, #0xff
		ADD r4, #1
		LDR r1, [r4, #0x14]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r5, r0, r1
		ADD r0, r5, #0
		LDR r1, [r4, #0x18]
		BL       |loc_080135A2|
		ADD r6, r0, #0
		LDR r0, [pc, #0xf4]
		ADD r3, sp, #0x100
		LDR r0, [r0, #4]
		STR r0, [sp, #0x128]
		MOV r0, #1
		STRB r0, [r3, #0x1e]
		LDR r0, [pc, #0xfc]
		STR r0, [sp, #0x13c]
		MOV r0, #0xc
		STRB r0, [r3, #0x1d]
		MOV r0, #0xe
		STR r0, [sp, #0x10c]
		MOV r0, #6
		STR r0, [sp, #0x110]
		MOV r0, #0x26
		STR r0, [sp, #0x114]
		MOV r0, #0x11
		STR r0, [sp, #0x118]
		ADD r0, sp, #4
		ADD r1, r6, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0xcd46
		ADD r2, sp, #0x10c
		ADD r1, sp, #4
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0x219e
		MOV r0, #5
		ADD r3, sp, #0x100
		STRB r0, [r3, #0x1f]
		MOV r0, #0x28
		STR r0, [sp, #0x120]
		MOV r0, #0xf
		STR r0, [sp, #0x124]
		LDRH r0, [r6, #0xc]
		LDR r1, [pc, #0xa8]
		LSL r0, r0, #2
		LDR r1, [r1, r0]
		ADD r0, r7, #0
		BL       |loc_0803DADA|
		MOV r0, #0x75
		ADD r3, sp, #0x100
		STRB r0, [r3, #0x1f]
		MOV r0, #0xe
		STR r0, [sp, #0x120]
		MOV r0, #0x1b
		STR r0, [sp, #0x124]
		LDRH r0, [r6, #0xe]
		LDR r1, [pc, #0x8c]
		LSL r0, r0, #2
		LDR r2, [r1, r0]
		MOV r1, #0xb4
		ADD r0, r7, #0
		BL       |loc_0803DD66|
		LDRB r0, [r6]
		CMP r0, #0xff
		DCW     0xD02E
		LDR r1, [r4, #0x18]
		LDR r0, [r4, #0x1c]
		LSL r1, r1, #1
		ADD r1, r1, r5
		ADD r1, #0x2e
		LDRB r1, [r1]
		CMP r1, #0
		BNE      |loc_08029254|
		MOV r1, #1
		B        |loc_08029256|
|loc_08029254|
		MOV r1, #0
|loc_08029256|
		MOV r3, #1
		SUB r1, r3, r1
		STR r1, [r0, #8]
		LDR r0, [r4, #0x18]
		LDR r1, [r4, #0x20]
		LSL r0, r0, #1
		ADD r0, r0, r5
		ADD r0, #0x2e
		LDRB r2, [r0]
		LDRB r0, [r0, #1]
		CMP r2, r0
		BNE      |sub_08029272|
		MOV r2, #1
		DCW     0xE000
