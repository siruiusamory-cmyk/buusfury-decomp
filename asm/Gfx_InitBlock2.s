	CODE16
|Gfx_InitBlock2|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	LDR      r2, [r0, #0x44]
	LDR      r0, [r0, #0x38]
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [pc, #0x1d4]
	LDR      r0, [r0, #8]
	STR      r0, [r4, #0x20]
	MOV      r0, #0x78
	STR      r0, [r4, #0x18]
	MOV      r0, #0x18
	STR      r0, [r4, #0x1c]
	MOV      r0, #0x10
	STRB     r0, [r4, #0x15]
	ADD      r4, #0x14
	CMP      r5, #0
	BEQ      |loc_08033694|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
|loc_08033694|
	LDR      r1, [pc, #0x1bc]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	LDR      r0, [pc, #0x1ac]
	SUB      sp, #0x10
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #3
	LSL      r2, r2, #0xf
	MOV      r1, #0
	LSL      r0, r2, #0xa
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x40
	MOV      r1, #0
	MOV      r0, #3
	LSL      r0, r0, #0x19
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #0xc
	MOV      r1, #0
	LDR      r0, [pc, #0x17c]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #6
	STR      r0, [sp, #4]
	MOV      r0, #0xe
	MOV      r5, #0
	MOV      r6, #0x1e
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	STR      r6, [sp, #8]
	MOV      r2, #1
	STR      r5, [sp]
	LDR      r1, [pc, #0x168]
	BL       |inc_0x03d784_0x041118| + 0x28c
	MOV      r0, #0xa
	STR      r0, [sp, #4]
	MOV      r0, #0x12
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	MOV      r2, #0xf1
	STR      r5, [sp]
	STR      r6, [sp, #8]
	LDR      r1, [pc, #0x14c]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r0, [pc, #0x150]
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	STRH     r0, [r1, #8]
	ADD      r0, #0xff
	ADD      r0, #1
	STRH     r0, [r1, #0xa]
	MOV      r0, #0x52
	STRB     r5, [r0, r1]
	MOV      r0, #0x53
	STRB     r5, [r0, r1]
	STRH     r5, [r1, #0x10]
	STRH     r5, [r1, #0x12]
	LDR      r0, [pc, #0x138]
	LDR      r1, [pc, #0x140]
	STRH     r5, [r0]
	STRH     r5, [r0, #2]
	LDR      r0, [pc, #0x134]
	LDR      r5, [pc, #0x13c]
	STRH     r0, [r1, #0x10]
	MOV      r0, #3
	LSL      r0, r0, #8
	SUB      r1, #0x40
	STRH     r0, [r1]
	LDR      r0, [r4, #0x10]
	LSL      r0, r0, #2
	LDR      r1, [r5, r0]
	ADD      r0, r4, #0
	BL       |Gfx_InitBlock2|
	LDR      r0, [r4, #0x10]
	ADD      r0, #1
	LSL      r0, r0, #2
	LDR      r1, [r5, r0]
	ADD      r0, r4, #0
	BL       |Gfx_InitBlock1|
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0x110]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x108]
	LDR      r0, [pc, #0xe4]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
|sub_0803377A|
|unk_0803377A|
		BX       lr
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r0, [r0, #0xc]
		MOV r6, #0
		CMP r0, #0
		LDR r5, [pc, #0xc4]
		BNE      |loc_080337B2|
		LDR r0, [r4, #8]
		CMP r0, #0
		BNE      |loc_080337B2|
		LDR r0, [r5]
		LDRH r0, [r0, #4]
		LSL r1, r0, #0x1f
		BNE      |loc_0803379E|
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1f
		BEQ      |loc_080337B2|
|loc_0803379E|
		MOV r0, #1
		STR r0, [r4, #8]
		LDR r0, [r5, #4]
		LDR r7, [pc, #0xd8]
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r0, r7
		LDR r1, [pc, #0xcc]
		BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_080337B2|
		LDR r0, [r4, #4]
		ADD r0, #1
		STR r0, [r4, #4]
		CMP r0, #0x80
		BGE      |loc_080337D2|
		LDR r0, [r4, #8]
		CMP r0, #0
		BNE      |loc_080337CC|
		LDR r0, [r5]
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1f
		BEQ      |loc_08033836|
|loc_080337CC|
		MOV r0, #0x7f
		STR r0, [r4, #4]
		B        |loc_08033836|
|loc_080337D2|
		CMP r0, #0x80
		BNE      |Blend_WriteAlpha4|
		LDR r0, [r4, #0x10]
		LDR r1, [pc, #0xa8]
		ADD r0, #2
		STR r0, [r4, #0x10]
		CMP r0, r1
		BLT      |loc_08033836|
		MOV r0, #1
		STR r0, [r4, #8]
		LDR r0, [pc, #0x58]
		STR r0, [r4, #0x10]
		B        |loc_08033836|
