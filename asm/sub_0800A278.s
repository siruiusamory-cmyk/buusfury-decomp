	CODE16
|sub_0800A278|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x260]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LSL      r0, r1, #5
	LDR      r1, [pc, #0x25c]
	ADD      r0, r0, r1
	BIC      r0, r1
	ASR      r1, r0, #8
	STRB     r1, [r4, #5]
	ADD      r1, r0, r5
	SUB      r1, #1
	ADD      r0, r5, #0
	STR      r5, [r4, #0x14]
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [r4, #0xc]
	MOV      r0, #0
	STR      r0, [r4, #8]
	LSL      r0, r5, #4
	STR      r0, [r4, #0x10]
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
|sub_0800A2A8|
|unk_0800A2A8|
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		ADD r5, r1, #0
		ADD r1, #0xff
		ADD r1, #0xa1
		LDR r0, [r0, #8]
		SUB sp, #0x2c
		STR r1, [sp, #0x20]
		ADD r1, #4
		ADD r6, r4, #0
		ADD r6, #0x18
		STR r1, [sp, #0x28]
		ADD r1, r6, #4
		STR r1, [sp, #0x24]
		CMP r0, #0
		BNE      |loc_0800A3AC|
		LDR r0, [r4, #0x10]
		BL       |inc_0x03d784_0x041118| + 0x235a
		CMP r0, #0
		BEQ      |loc_0800A3AE|
		ADD r1, r5, #0
		ADD r0, r4, #0
		ADD r0, #0x28
		STR r0, [sp, #0x1c]
		BL       |Object_WriteBounds1|
		MOV r0, #5
		BL       |inc_0x03d784_0x041118| + 0x2348
		CMP r0, #4
		BGE      |loc_0800A2EA|
		STRB r0, [r5, #0x10]
|loc_0800A2EA|
		LDR r1, [sp, #0x20]
		LDR r1, [r1]
		LDR r2, [sp, #0x28]
		ASR r1, r1, #8
		LDR r2, [r2]
		STR r1, [sp, #0x14]
		ASR r2, r2, #8
		STR r2, [sp, #0x18]
		STR r1, [r4, #0x20]
		STR r2, [r4, #0x24]
		LDRB r3, [r5, #0x10]
		MOV r2, #0
		CMP r3, #0
		BEQ      |loc_0800A320|
		CMP r3, #1
		BEQ      |loc_0800A32E|
		CMP r3, #2
		BEQ      |loc_0800A340|
		CMP r3, #3
		BNE      |loc_0800A350|
		LDR r0, [r4, #0x14]
		STR r0, [r6]
		LDR r1, [sp, #0x24]
		STR r2, [r1]
		LDRB r0, [r4, #5]
		ADD r1, r2, #0
		B        |loc_0800A350|
|loc_0800A320|
		LDR r0, [r4, #0x14]
		STR r2, [r6]
		LDR r1, [sp, #0x24]
		STR r0, [r1]
		LDRB r1, [r4, #5]
		ADD r0, r2, #0
		B        |loc_0800A350|
|loc_0800A32E|
		LDR r0, [r4, #0x14]
		STR r2, [r6]
		LDR r1, [sp, #0x24]
		NEG r0, r0
		STR r0, [r1]
		LDRB r0, [r4, #5]
		NEG r1, r0
		ADD r0, r2, #0
		B        |loc_0800A350|
|loc_0800A340|
		LDR r0, [r4, #0x14]
		NEG r0, r0
		STR r0, [r6]
		LDR r1, [sp, #0x24]
		STR r2, [r1]
		LDRB r0, [r4, #5]
		NEG r0, r0
		ADD r1, r2, #0
|loc_0800A350|
		LDR r2, [r4, #0x20]
		ADD r7, r4, #0
		ADD r2, r2, r0
		STR r2, [r4, #0x20]
		LDR r2, [r4, #0x24]
		ADD r7, #0x38
		ADD r2, r2, r1
		STR r2, [r4, #0x24]
		LDR r2, [sp, #0x1c]
		STR r2, [sp, #0x18]
		LDR r2, [r2]
		LDR r3, [sp, #0x18]
		ADD r2, r2, r0
		LDR r3, [r3, #4]
		STR r2, [sp]
		ADD r3, r3, r1
		STR r3, [sp, #4]
		MOV ip, r2
		LDR r2, [sp, #4]
		MOV lr, r2
		LDR r2, [sp, #0x18]
		ADD r2, #8
		LDR r3, [r2]
		LDR r2, [r2, #4]
		ADD r0, r3, r0
		ADD r1, r2, r1
		MOV r2, lr
		STR r2, [sp, #0xc]
		ADD r2, sp, #8
		STR r0, [sp]
		STR r0, [sp, #0x10]
		MOV r3, ip
		STR r3, [sp, #8]
		ADD r0, r2, #0
		STR r1, [sp, #4]
		STR r1, [sp, #0x14]
		LDMIA r0!, {r0, r1, r2, r3}
		STMIA r7!, {r0, r1, r2, r3}
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x10]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |Thunk_JumpRegister1|
		B        |loc_0800A3B0|
|loc_0800A3AC|
		B        |loc_0800A3D0|
|loc_0800A3AE|
		B        |loc_0800A3CA|
|loc_0800A3B0|
		CMP r0, #0
		BEQ      |loc_0800A3CA|
		LDR r0, [r4, #0xc]
		STR r0, [r4, #8]
		LDRB r0, [r5, #0x10]
		STRB r0, [r4, #4]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x18]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |Thunk_JumpRegister1|
|loc_0800A3CA|
		LDR r0, [r4, #8]
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0xa2d4
|loc_0800A3D0|
		LDR r1, [sp, #0x20]
		LDR r2, [r6]
		LDR r0, [r1]
		ADD r0, r0, r2
		STR r0, [r1]
		LDR r0, [sp, #0x24]
		LDR r2, [r1, #4]
		LDR r0, [r0]
		ADD r0, r2, r0
		STR r0, [r1, #4]
		LDRB r0, [r4, #4]
		STRB r0, [r5, #0x10]
		LDR r0, [r4, #8]
		SUB r0, #1
		STR r0, [r4, #8]
		BNE      |inc_0x0158_0x143f2| + 0xa2c6
		LDR r2, [sp, #0x20]
		LDR r0, [r4, #0x20]
		LDR r1, [r4, #0x24]
		LSL r0, r0, #8
		STR r0, [r2]
		LDR r2, [sp, #0x28]
		LSL r1, r1, #8
		STR r1, [r2]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x14]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |Thunk_JumpRegister1|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x1c]
		ADD r2, r2, r1
		ADD r1, r5, #0
	INCBIN  baserom.gba_0xa418_0xa41a.extracted
|sub_0800A41A|
|unk_0800A41A|
	INCBIN	baserom.gba_0xa41a_0xa41e.extracted
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x18]
	ADD      r2, r2, r1
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	LDR      r2, [r0, #8]
	CMP      r2, #0
	BEQ      |loc_0800A444|
	LDR      r2, [r0]
	LDR      r3, [r2, #0x14]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800A444|
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_0800A46A|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800A46A|
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_0800A490|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800A490|
	POP      {r4, pc}
	LDR      r1, [pc, #0x54]
	PUSH     {r3, lr}
	LDR      r1, [r1]
	ADD      r0, #0x38
	ADD      r1, #0x80
	LDR      r1, [r1, #0x28]
	BL       |loc_08009324|
	POP      {r3, pc}
