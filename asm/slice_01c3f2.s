	IMPORT |GBARam_Free|
	IMPORT |GBARam_Malloc|
|sub_0801C3F2|
	ADD      r4, r0, #0
	ADD      r6, r1, #0
	STR      r3, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0xdd08
	LDR      r5, [pc, #0x2a0]
	MOV      r1, #0x51
	LDR      r2, [pc, #0x2a0]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r7, [pc, #0x2a0]
	LDR      r0, [r5]
	MOV      r2, #0x40
	MOV      r3, #0
	ADD      r0, r0, r7
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r3, #0
	LDR      r0, [pc, #0x294]
	STR      r3, [r4, #0xc]
	LDRB     r0, [r0]
	MOV      r7, #1
	LSL      r7, r7, #0xa
	CMP      r0, #0
	BEQ      |sub_0801C486|
	CMP      r0, #1
	BNE      |loc_0801C482|
	ADD      r1, r6, #0
	ADD      r4, sp, #0x1c
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xfca2
	ADD      r2, r4, #0
	ADD      r2, #8
	ADD      r6, sp, #0x2c
	ADD      r1, sp, #0x1c
	ADD      r0, sp, #0xc
	BL       |inc_0x049120_0x055620| + 0x9e94
	LDR      r0, [sp, #0xc]
	ADD      r4, sp, #0x34
	ASR      r1, r0, #1
	LDR      r0, [sp, #0x10]
	STR      r1, [sp, #4]
	ASR      r0, r0, #1
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x30]
	MOV      r0, #0
	STR      r0, [sp, #0x14]
	MOV      r0, #2
	STR      r1, [sp, #0x2c]
	ADD      r1, r6, #0
	STR      r0, [sp, #0x18]
	ADD      r0, r4, #0
	ADD      r2, sp, #0x14
	BL       |inc_0x049120_0x055620| + 0x9e94
	MOV      r2, #0x38
	LDR      r0, [pc, #0x248]
	STR      r2, [sp, #8]
	MOV      r3, #7
	ADD      r1, r4, #0
	STR      r0, [sp]
	MOV      r0, #0
	LDR      r2, [pc, #0x240]
	STR      r7, [sp, #4]
	BL       |loc_0802A81C|
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0801C482|
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
|sub_0801C486|
|unk_0801C486|
		ADD r1, r6, #0
		ADD r6, sp, #0x1c
		ADD r0, r6, #0
		BL       |sub_0800FDFA|
		ADD r2, r6, #0
		ADD r2, #8
		ADD r1, sp, #0x1c
		ADD r0, sp, #0xc
		BL       |inc_0x049120_0x055620| + 0x9e94
		LDR r0, [sp, #0xc]
		MOV r2, #1
		ASR r1, r0, #1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x30]
		MOV r0, #0
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x2c]
		STR r2, [sp, #0x18]
		ADD r2, sp, #0x14
		ADD r1, sp, #0x2c
		ADD r0, sp, #0x34
		BL       |inc_0x049120_0x055620| + 0x9e94
		MOV r0, #0x48
		DCD     0xF87AF021
		ADD r6, r0, #0
		BEQ      |loc_0801C4E8|
		STR r7, [sp, #4]
		LDR r7, [pc, #0x1ec]
		MOV r2, #0x38
		MOV r0, #1
		LSL r0, r0, #0xe
		STR r2, [sp, #8]
		ADD r2, r7, #0
		STR r0, [sp]
		MOV r3, #3
		ADD r0, r6, #0
		ADD r1, sp, #0x34
		BL       |loc_0802A81C|
		LDR r0, [pc, #0x1d8]
		STR r0, [r6]
		STR r7, [r6, #0x44]
|loc_0801C4E8|
		STR r6, [r4, #0xc]
		LDR r0, [r5, #4]
		ADD r1, r6, #0
		BL       |sub_0801191A|
		B        |loc_0801C482|
|sub_0801C4F4|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r4, r0, #0
	LDR      r0, [r5, #0x50]
	LDR      r0, [r0]
	LSL      r1, r0, #4
	ADD      r0, r4, #0
	ADD      r0, #0x1c
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	LDRH     r2, [r5, #0x12]
	MUL      r0, r2
	SWI      6
	LDRB     r1, [r4, #0x14]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r2, [pc, #0x19c]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1]
	LSL      r1, r1, #0x1f
	BEQ      |sub_0801C540|
	ADD      r1, r4, #0
	ADD      r1, #0x20
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
|loc_0801C536|
	STRH     r0, [r1]
	LDRH     r2, [r1]
	CMP      r2, r0
	BNE      |loc_0801C536|
	POP      {r3, r4, r5, pc}
|sub_0801C540|
|unk_0801C540|
		ADD r1, r4, #0
		ADD r1, #0x1e
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
|loc_0801C548|
		STRH r0, [r1]
		LDRH r2, [r1]
		CMP r2, r0
		BNE      |loc_0801C548|
		B        |inc_0x1c3f2_0x2ab4c| + 0x14c
|sub_0801C552|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r4, #8]
	CMP      r1, #0
	BNE      |loc_0801C598|
	LDR      r1, [r0]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRB     r1, [r0, #0x14]
	LDR      r2, [pc, #0x150]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1]
	LSL      r2, r1, #0x1f
	LSR      r2, r2, #0x1f
	MOV      r1, #0
	CMP      r2, #0
	BEQ      |loc_0801C58E|
	ADD      r0, #0x20
|loc_0801C584|
	STRH     r1, [r0]
	LDRH     r2, [r0]
	CMP      r2, r1
	BNE      |loc_0801C584|
	B        |loc_0801C598|
|loc_0801C58E|
	ADD      r0, #0x1e
|loc_0801C590|
	STRH     r1, [r0]
	LDRH     r2, [r0]
	CMP      r2, r1
	BNE      |loc_0801C590|
|loc_0801C598|
	LDR      r0, [r4, #0xc]
	LDR      r4, [pc, #0x104]
	CMP      r0, #0
	BEQ      |loc_0801C5A8|
	ADD      r1, r0, #0
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_0801C5A8|
	MOV      r1, #0x51
	LDR      r2, [pc, #0xf8]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r2, [pc, #0xf4]
	LDR      r0, [r4]
	ADD      r0, r0, r2
	BL       |inc_0x03d784_0x041118| + 0xb7e
	POP      {r4, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r5, r0, #0
	LDRB     r0, [r0, #0x14]
	LDR      r6, [pc, #0xd8]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r6
	BL       |inc_0x153f2_0x1a3f2| + 0x1d3a
	MOV      r0, #0xe
	STRB     r0, [r5, #0x14]
	ADD      r0, r6, #0
	ADD      r0, #0xff
	ADD      r0, #0x51
	BL       |inc_0x153f2_0x1a3f2| + 0x1d2a
	LDRB     r0, [r5, #0x14]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r6
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x104f4
	POP      {r4, r5, r6, pc}
	AREA     CPilotTail, CODE, READONLY
	CODE16
|sub_0801C63C|
	BX       lr
|sub_0801C63E|
	PUSH     {r4, r5, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x14
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x20
	BLS      |sub_0801C664|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x14
	POP      {r4, r5, pc}
|sub_0801C664|
|unk_0801C664|
; cited by 0x0801C3FC (a pc-relative load targets 0x0801C6A0)
		LSR r0, r0, #4
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #0x10
		DCW     0xD1F8
		ADD r1, r4, #0
		ADD r5, sp, #4
		ADD r0, r5, #0
		BL       |sub_0804F944|
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0x48]
		LSL r0, r0, #3
		ADD r2, r0, r1
		ADD r1, r5, #0
		ADD r5, sp, #0xc
		ADD r0, r5, #0
		BL       |inc_0x049120_0x055620| + 0x9e94
		ADD r2, r4, #0
		ADD r1, r5, #0
		MOV r0, #0
		BL       |loc_080383D4|
		ADD r1, r0, #0
		LDR r0, [pc, #8]
		LDR r0, [r0, #4]
		BL       |sub_0801191A|
		DCW     0xE7DF
		DCD     0x0871DD38
	INCBIN  baserom.gba_0x1c6a4_0x1c6c6.extracted
|sub_0801C6C6|
	LSR      r1, r6, #1
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0801C700|
	MOV      r0, #0x60
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0801C700|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801C700|
|unk_0801C700|
		MOV r1, #0xff
		ADD r1, #1
		ADD r2, r7, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x1d4]
		STR r0, [r4]
		LDMIA r6!, {r1, r2}
		STR r1, [r4, #0x40]
		STR r2, [r4, #0x44]
		LDR r2, [r5]
		LDR r3, [r5, #4]
		LSL r2, r2, #8
		STR r2, [r4, #0x20]
		ADD r0, r4, #0
		LSL r3, r3, #8
		STR r3, [r4, #0x24]
		ADD r0, #0x4c
		MOV r5, #0
		MOV r1, #1
		LSL r1, r1, #0xb
		STR r5, [r4, #0x48]
		STR r1, [r0]
		ADD r6, r0, #4
		LDR r0, [pc, #0x1b4]
		LSR r1, r1, #2
		STR r1, [r6]
		STR r0, [r4, #0x18]
		MOV r0, #0x37
		STRB r0, [r4, #8]
		LDR r0, [r4, #0x44]
		SUB r0, r0, r1
		STR r0, [r4, #0x44]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		STRB r5, [r6, #4]
		ADD r0, r4, #0
		DCW     0xE7D6
|sub_0801C750|
	PUSH     {r4, r5, r6, lr}
	ADD      r1, r0, #0
	ADD      r1, #0x28
	ADD      r2, r1, #0
	LDR      r3, [r0, #0x28]
	LDR      r5, [r0, #0x30]
	ADD      r2, #8
	LDR      r1, [r0, #0x2c]
	LDR      r2, [r2, #4]
	SUB      sp, #0x10
	ADD      r1, r1, r2
	ADD      r3, r3, r5
	STR      r1, [sp, #4]
	ASR      r1, r1, #1
	ASR      r2, r3, #1
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	STR      r3, [sp]
	LDR      r5, [pc, #0x174]
	STR      r2, [sp]
	ADD      r1, r0, #0
	STR      r2, [sp, #8]
	LDR      r0, [r5, #4]
	ADD      r4, sp, #8
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r6, [pc, #0x164]
	ADD      r6, #8
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xc2fc
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r2, r6, #0
	ADD      r2, #8
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xc2fc
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r2, r6, #0
	ADD      r2, #0x10
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xc2fc
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r2, r6, #0
	ADD      r2, #0x18
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xc2fc
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0801C7F6|
	MOV      r2, #0x38
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x413a
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0801C7F6|
	LDR      r4, [pc, #0xfc]
	LDR      r0, [r5]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r0, r4
	LDR      r1, [pc, #0xec]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r5, #0x50
	ADD      r4, r0, #0
	LDRB     r0, [r5, #4]
	ADD      r7, r1, #0
	MOV      r6, #0xb
	CMP      r0, #0
	SUB      sp, #0x34
	BEQ      |sub_0801C8A8|
	CMP      r0, #1
	BNE      |loc_0801C82C|
	LDR      r0, [r4, #0x5c]
	SUB      r0, #1
	STR      r0, [r4, #0x5c]
	BPL      |loc_0801C82C|
	STR      r6, [r4, #0x5c]
|loc_0801C82C|
	LDR      r0, [r4, #0x48]
	ADD      r0, #1
	STR      r0, [r4, #0x48]
	LSL      r0, r0, #0x1c
	LSR      r0, r0, #0x1e
	CMP      r0, #3
	BNE      |loc_0801C83C|
	MOV      r0, #1
|loc_0801C83C|
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0xa4]
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	STR      r0, [r4, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDRB     r1, [r5, #4]
	MOV      r0, #1
	CMP      r1, #0
	BEQ      |loc_0801C8C0|
	CMP      r1, #1
	BNE      |loc_0801C8A4|
	LDR      r0, [r4, #0x58]
	SUB      r0, #1
	STR      r0, [r4, #0x58]
	BPL      |loc_0801C8A4|
	CMP      r7, #0
	BEQ      |loc_0801C89E|
	LDR      r0, [r4, #0x1c]
	CMP      r0, #0
	BEQ      |loc_0801C89E|
	LDR      r0, [r4, #0x1c]
	ADD      r3, sp, #0
	STR      r0, [sp, #0x20]
	LDRB     r0, [r4, #0x10]
	ADD      r6, sp, #4
	MOV      r5, sp
	STRB     r0, [r3, #0x14]
	LDR      r0, [pc, #0x7c]
	STR      r0, [sp, #0x1c]
	LSL      r0, r1, #0xa
	STR      r0, [sp, #0x18]
	ADD      r0, r4, #0
	ADD      r0, #0x28
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r6!, {r0, r1, r2, r3}
	MOV      r0, #2
	ADD      r3, sp, #0
	STRB     r0, [r3]
	LDR      r0, [pc, #0x58]
	STR      r4, [sp, #0x30]
	ADD      r2, r5, #0
	MOV      r1, #0
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x11ab4
|loc_0801C89E|
	ADD      r0, r4, #0
	BL       |sub_0801C750|
|loc_0801C8A4|
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
|sub_0801C8A8|
|unk_0801C8A8|
		LDR r1, [r4, #0x20]
		LDR r2, [r4, #0x40]
		ADD r1, r1, r2
		STR r1, [r4, #0x20]
		LDR r0, [r4, #0x44]
		LDR r1, [r4, #0x24]
		ADD r0, r1, r0
		STR r0, [r4, #0x24]
		LDR r0, [r4, #0x44]
		ADD r0, #0x20
		STR r0, [r4, #0x44]
		B        |loc_0801C82C|
|loc_0801C8C0|
|unk_0801C8C0|
		LDR r1, [r4, #0x50]
		SUB r1, #0x20
		STR r1, [r4, #0x50]
		LDR r2, [r4, #0x4c]
		ADD r1, r2, r1
		LDR r2, [pc, #0x30]
		STR r1, [r4, #0x4c]
		CMP r1, r2
		BGE      |loc_0801C8A4|
		STRB r0, [r5, #4]
		MOV r0, #0x1e
		ADD r4, #0x58
		STMIA r4!, {r0, r6}
		B        |loc_0801C8A4|
|sub_0801C8DC|
	PUSH     {r3, lr}
	BL       |inc_0x153f2_0x1a3f2| + 0x48d2
	POP      {r3, pc}
|sub_0801C8E4|
	DCW      0xa2e8
	DCW      0x0804,0xe984,0x0871,0xe200
|sub_0801C8EE|
	LSR      r1, r6, #1
	STR      r3, [sp, #0x320]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	DCW      0xf400,0xffff
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0801C91C|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0801C91C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801C91C|
|unk_0801C91C|
		MOV r1, #0xff
		ADD r1, #1
		ADD r2, r7, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x250]
		LDR r3, [pc, #0x258]
		STR r0, [r4]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r0, r6, #1
		ADD r0, r0, r6
		LDR r1, [pc, #0x244]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		LSL r0, r0, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		MOV r2, #0
		STR r2, [r4, #0x48]
		LSL r0, r6, #3
		LDR r1, [r3, r0]
		ADD r0, r0, r3
		STR r1, [r4, #0x40]
		LDR r0, [r0, #4]
		ADD r3, r2, #0
		STR r0, [r4, #0x44]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		LDR r0, [pc, #0x224]
		LDR r5, [pc, #0x22c]
		SUB r0, #0xc
		LDR r0, [r0]
		MOV r2, #0x40
		ADD r0, r0, r5
		LDR r1, [pc, #0x21c]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		DCW     0xE7D0
|sub_0801C978|
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x20]
	SUB      sp, #0x18
	ASR      r1, r1, #8
	STR      r1, [sp, #0x10]
	LDR      r1, [r0, #0x24]
	LDR      r4, [pc, #0x1fc]
	ASR      r1, r1, #8
	STR      r1, [sp, #0x14]
	ADD      r1, r0, #0
	SUB      r4, #0xc
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0801C9C0|
	MOV      r2, #0x38
	LSL      r0, r1, #3
	STR      r0, [sp]
	STR      r2, [sp, #8]
	STR      r1, [sp, #4]
	MOV      r3, #4
	MOV      r0, #0
	ADD      r1, sp, #0x10
	LDR      r2, [pc, #0x1dc]
	BL       |loc_0802A81C|
	ADD      r1, r0, #0
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0801C9C0|
	ADD      sp, #0x18
	POP      {r4, pc}
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x48]
	SUB      sp, #0x34
	ADD      r0, #1
	STR      r0, [r4, #0x48]
	ADD      r6, r4, #0
	ADD      r6, #0x40
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1e
	ADD      r5, r6, #4
	CMP      r0, #0
	BNE      |loc_0801CA6C|
	LDR      r0, [pc, #0x1a4]
	SUB      r0, #0xc
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	CMP      r0, #0x40
	BLT      |loc_0801CA6C|
	LDR      r1, [r6]
	LDR      r2, [r5]
	LSL      r1, r1, #0xb
	LSL      r2, r2, #0xb
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	ADD      r0, r4, #0
	ADD      r0, #0x20
	STR      r1, [sp, #0x14]
	STR      r1, [sp, #0x1c]
	STR      r2, [sp, #0x18]
	STR      r2, [sp, #0x20]
	LDR      r1, [r0]
	LDR      r2, [sp, #0x1c]
	LDR      r3, [r0, #4]
	SUB      r2, r1, r2
	LDR      r7, [sp, #0x20]
	STR      r2, [sp, #0x14]
	STR      r2, [sp, #0x24]
	SUB      r3, r3, r7
	ASR      r2, r2, #8
	STR      r2, [sp, #0x2c]
	STR      r3, [sp, #0x18]
	STR      r3, [sp, #0x28]
	LDR      r2, [r6]
	LDR      r7, [r5]
	LSL      r2, r2, #0xb
	LSL      r3, r7, #0xb
	ASR      r3, r3, #8
	ASR      r2, r2, #8
	STR      r2, [sp, #0x14]
	STR      r2, [sp, #0x1c]
	STR      r3, [sp, #0x18]
	STR      r3, [sp, #0x20]
	ADD      r1, r0, #4
	LDR      r0, [r0]
	LDR      r1, [r1]
	SUB      r0, r0, r2
	SUB      r1, r1, r3
	STR      r0, [sp, #0x14]
	STR      r0, [sp, #0x24]
	ASR      r0, r1, #8
	STR      r1, [sp, #0x28]
	MOV      r2, #0x38
	STR      r2, [sp, #8]
	STR      r0, [sp, #0x30]
	STR      r1, [sp, #0x18]
	MOV      r1, #0x40
	LDR      r0, [pc, #0x144]
	LDR      r2, [pc, #0x130]
	STR      r1, [sp, #4]
	MOV      r3, #3
	STR      r0, [sp]
	ADD      r2, #0x30
	MOV      r0, #0
	ADD      r1, sp, #0x2c
	BL       |loc_0802A81C|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x120]
	SUB      r0, #0xc
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0801CA6C|
	LDR      r0, [r4, #0x20]
	LDR      r1, [r6]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x20]
	LDR      r0, [r4, #0x24]
	LDR      r1, [r5]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x24]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r6, [pc, #0x100]
	SUB      r6, #0xc
	LDR      r0, [r6, #8]
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r2, [r4, #0x30]
	CMP      r1, r2
	BGE      |loc_0801CAAA|
	LDR      r1, [r4, #0x28]
	LDR      r2, [r0, #8]
	CMP      r1, r2
	BGE      |loc_0801CAAA|
	LDR      r1, [r0, #4]
	LDR      r2, [r4, #0x34]
	CMP      r1, r2
	BGE      |loc_0801CAAA|
	LDR      r1, [r4, #0x2c]
	LDR      r0, [r0, #0xc]
	CMP      r1, r0
	BLT      |sub_0801CAB6|
|loc_0801CAAA|
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
|sub_0801CAB6|
|unk_0801CAB6|
		ADD r0, r4, #0
		ADD r0, #0x28
		LDR r1, [r6, #8]
		ADD r5, r0, #0
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_0801CAD2|
		ADD r0, r4, #0
		BL       |sub_0801C978|
		DCW     0xE7EF
|loc_0801CAD2|
		LDR r0, [sp, #0x38]
		CMP r0, #0
		DCW     0xD0EC
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		DCW     0xD0E9
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		MOV r7, sp
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0xac]
		STR r0, [sp, #0x1c]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x18]
		LDMIA r5!, {r1, r2, r3, r5}
		ADD r0, sp, #4
		STMIA r0!, {r1, r2, r3, r5}
		MOV r5, #0
		ADD r3, sp, #0
		STRB r5, [r3]
		STR r4, [sp, #0x30]
		ADD r2, r7, #0
		MOV r1, #0
		LDR r0, [r6, #4]
		BL       |loc_08011C70|
		CMP r0, #0
		DCW     0xD0D0
		LDR r6, [r6]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0x7c]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDR r0, [pc, #0x64]
		ADD r3, r5, #0
		MOV r2, #0x40
		ADD r0, r6, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x1cb32_0x1cb34.extracted
|sub_0801CB34|
|unk_0801CB34|
	INCBIN	baserom.gba_0x1cb34_0x1cb38.extracted
	PUSH     {r3, lr}
	CMP      r1, #0
	BNE      |loc_0801CB76|
	LDR      r1, [r2, #0x30]
	CMP      r1, r0
	BNE      |sub_0801CB48|
	MOV      r0, #0
	POP      {r3, pc}
|sub_0801CB48|
|unk_0801CB48|
		ADD r1, r2, #4
		LDR r2, [r2, #4]
		LDR r3, [r0, #0x30]
		CMP r2, r3
		BGE      |loc_0801CB72|
		LDR r2, [r0, #0x28]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_0801CB72|
		LDR r2, [r1, #4]
		LDR r3, [r0, #0x34]
		CMP r2, r3
		BGE      |loc_0801CB72|
		LDR r2, [r0, #0x2c]
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BGE      |loc_0801CB72|
		BL       |sub_0801C978|
		MOV r0, #1
		DCW     0xE7E9
|loc_0801CB72|
		MOV r0, #0
		DCW     0xE7E7
|loc_0801CB76|
|unk_0801CB76|
; cited by 0x0801C928 (a pc-relative load targets 0x0801CB7C)
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		DCW     0xE7E4
	INCBIN  baserom.gba_0x1cb7c_0x1cb86.extracted
|sub_0801CB86|
	LSR      r1, r6, #1
	STR      r3, [sp, #0x3e0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	CMP      r7, #0xdc
	LSR      r1, r6, #1
	CMP      r2, #0xaa
	LSL      r0, r0, #0
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDR      r0, [pc, #0x210]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x4c
	CMP      r1, #0
	BNE      |sub_0801CBB6|
	MOV      r0, #1
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
|sub_0801CBB6|
|unk_0801CBB6|
		ADD r0, sp, #0xc
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		STR r0, [sp, #8]
		STR r0, [sp, #0x20]
		MOV r5, #1
		ADD r1, r4, #0
		ADD r0, sp, #0x24
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0x24]
		LDR r1, [sp, #0x2c]
		LDR r2, [sp, #0x30]
		ADD r1, r0, r1
		LDR r0, [sp, #0x28]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x38]
		ASR r1, r1, #1
		LDR r0, [sp, #0x1c]
		STR r1, [sp, #4]
		SUB r0, r0, r1
		STR r1, [sp, #0x34]
		LDR r1, [sp, #0x20]
		LDR r2, [sp, #0x38]
		STR r0, [sp, #4]
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #8]
		STR r1, [sp, #0x40]
		STR r0, [sp, #0x3c]
		BGE      |loc_0801CC18|
		NEG r0, r2
|loc_0801CC18|
		ADD r1, r0, #0
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BGE      |loc_0801CC22|
		NEG r0, r0
|loc_0801CC22|
		ADD r7, r1, #0
		CMP r1, r0
		STR r1, [sp, #0x34]
		STR r0, [sp, #0x38]
		BLE      |loc_0801CC3A|
		LDR r1, [sp, #0x3c]
		MOV r0, #2
		CMP r1, #0
		BGT      |loc_0801CC36|
		MOV r0, #3
|loc_0801CC36|
		STRB r0, [r4, #0x10]
		B        |loc_0801CC46|
|loc_0801CC3A|
		ADD r7, r0, #0
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BGT      |loc_0801CC44|
		MOV r5, #0
|loc_0801CC44|
		STRB r5, [r4, #0x10]
|loc_0801CC46|
		CMP r7, #0
		BNE      |loc_0801CC4E|
		MOV r0, #0
		DCW     0xE7B1
|loc_0801CC4E|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_0801CC6E|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
|loc_0801CC6E|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		LDR r0, [sp, #0x3c]
		LDR r1, [sp, #0x40]
		LSL r0, r0, #8
		LSL r1, r1, #8
		STR r1, [sp, #0x38]
		STR r0, [sp, #0x34]
		LDR r1, [r6, #4]
		LDR r2, [sp, #0x38]
		MUL r0, r1
		MUL r2, r1
		ASR r1, r2, #8
		ASR r0, r0, #8
		ADD r5, r4, #0
		ADD r5, #0xff
		STR r1, [sp, #0x10]
		STR r1, [sp, #0x18]
		LSL r1, r0, #8
		ADD r5, #0xa1
		STR r0, [sp, #0xc]
		STR r0, [sp, #0x14]
		LSL r7, r7, #8
		ADD r0, r7, #0
		BL       |sub_08046E58|
		STR r0, [sp, #8]
		LDR r0, [sp, #0x18]
		LSL r1, r0, #8
		ADD r0, r7, #0
		BL       |sub_08046E58|
		LDR r1, [sp, #8]
		STR r0, [sp, #0x10]
		ADD r0, r1, #0
		STR r1, [sp, #0xc]
		LDR r1, [sp, #0x10]
		STR r0, [sp, #0x1c]
		STR r1, [sp, #0x20]
		LDR r0, [r5]
		LDR r1, [sp, #0x1c]
		ADD r7, r5, #4
		SUB r0, r0, r1
		LDR r1, [r5, #4]
		LDR r2, [sp, #0x20]
		STR r0, [sp, #0xc]
		SUB r1, r1, r2
		STR r1, [sp, #0x10]
		STR r1, [sp, #0x30]
		STR r1, [sp, #0x28]
		STR r0, [sp, #0x2c]
		STR r0, [sp, #0x24]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x2c
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0801CCFC|
		LDR r0, [sp, #0x2c]
		STR r0, [r5]
		LDR r0, [sp, #0x30]
		STR r0, [r7]
		B        |loc_0801CD7C|
|loc_0801CCFC|
		ADD r0, r6, #4
		LDR r1, [sp, #0x3c]
		STR r0, [sp, #0x48]
		ADD r3, sp, #0x24
		CMP r1, #0
		BGE      |loc_0801CD10|
		LDR r0, [r6, #4]
		NEG r0, r0
		STR r0, [sp, #0x20]
		ADD r0, sp, #0x20
|loc_0801CD10|
		LDR r1, [r5]
		LDR r0, [r0]
		ADD r3, sp, #0x24
		SUB r0, r1, r0
		STR r0, [sp, #0x24]
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa5
		STR r0, [sp, #0x44]
		LDR r0, [r0]
		STR r0, [sp, #0x28]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, r3, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0801CD42|
		LDR r0, [sp, #0x24]
		STR r0, [r5]
		LDR r0, [sp, #0x28]
		STR r0, [r7]
		B        |loc_0801CD7C|
|loc_0801CD42|
		LDR r0, [r5]
		ADD r1, sp, #0x44
		STR r0, [sp, #0x24]
		LDMIA r1!, {r0, r1}
		LDR r2, [sp, #0x40]
		ADD r3, sp, #0x24
		CMP r2, #0
		BGE      |loc_0801CD5A|
		LDR r1, [r6, #4]
		NEG r1, r1
		STR r1, [sp, #0x20]
		ADD r1, sp, #0x20
|loc_0801CD5A|
		LDR r0, [r0]
		LDR r1, [r1]
		SUB r0, r0, r1
		STR r0, [sp, #0x28]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, r3, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0801CD8E|
		LDR r0, [sp, #0x24]
		STR r0, [r5]
		LDR r0, [sp, #0x28]
		STR r0, [r7]
|loc_0801CD7C|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #0
		DCW     0xE711
|loc_0801CD8E|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #1
		DCW     0xE708
|sub_0801CDA0|
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801CDB4|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0801CDB4|
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STR      r5, [sp, #0x390]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x228]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x44
	CMP      r1, #0
	BNE      |sub_0801CDD6|
	MOV      r0, #0
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
|sub_0801CDD6|
|unk_0801CDD6|
		ADD r0, sp, #0xc
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		STR r0, [sp, #8]
		STR r0, [sp, #0x20]
		ADD r0, sp, #0x24
		ADD r1, r4, #0
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0x24]
		LDR r1, [sp, #0x2c]
		LDR r2, [sp, #0x30]
		ADD r1, r0, r1
		LDR r0, [sp, #0x28]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x38]
		ASR r1, r1, #1
		LDR r0, [sp, #0x1c]
		STR r1, [sp, #4]
		SUB r0, r0, r1
		STR r1, [sp, #0x34]
		LDR r1, [sp, #0x20]
		LDR r2, [sp, #0x38]
		STR r0, [sp, #4]
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #8]
		STR r1, [sp, #0x40]
		STR r0, [sp, #0x3c]
		BGE      |loc_0801CE36|
		NEG r0, r2
|loc_0801CE36|
		ADD r1, r0, #0
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BGE      |loc_0801CE40|
		NEG r0, r0
|loc_0801CE40|
		STR r1, [sp, #0x34]
		STR r0, [sp, #0x38]
		ADD r0, r1, #0
		MOV r6, #0
		LDR r1, [sp, #0x38]
		MOV r7, #3
		CMP r0, r1
		STR r6, [sp, #0x38]
		STR r6, [sp, #0x34]
		BLE      |loc_0801CEA0|
		CMP r1, #3
		BGE      |loc_0801CE86|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0801CE78|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
|loc_0801CE78|
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BGT      |loc_0801CE80|
		MOV r7, #2
|loc_0801CE80|
		STRB r7, [r4, #0x10]
		MOV r0, #1
		DCW     0xE7A5
|loc_0801CE86|
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BLE      |loc_0801CE94|
		STRB r6, [r4, #0x10]
		LDR r0, [r5, #4]
		STR r0, [sp, #0x38]
		B        |loc_0801CEEC|
|loc_0801CE94|
		MOV r0, #1
		STRB r0, [r4, #0x10]
		LDR r0, [r5, #4]
		NEG r0, r0
		STR r0, [sp, #0x38]
		B        |loc_0801CEEC|
|loc_0801CEA0|
		CMP r0, #3
		BGE      |loc_0801CED4|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0801CEC4|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
|loc_0801CEC4|
		LDR r1, [sp, #0x40]
		MOV r0, #1
		CMP r1, #0
		BLE      |loc_0801CECE|
		MOV r0, #0
|loc_0801CECE|
		STRB r0, [r4, #0x10]
		MOV r0, #1
		DCW     0xE77E
|loc_0801CED4|
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BLE      |loc_0801CEE2|
		STRB r7, [r4, #0x10]
		LDR r0, [r5, #4]
		STR r0, [sp, #0x34]
		B        |loc_0801CEEC|
|loc_0801CEE2|
		MOV r0, #2
		STRB r0, [r4, #0x10]
		LDR r0, [r5, #4]
		NEG r0, r0
		STR r0, [sp, #0x34]
|loc_0801CEEC|
		MOV r0, #0x4e
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BEQ      |loc_0801CF0C|
		MOV r0, #0x11
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BEQ      |loc_0801CF0C|
		MOV r0, #0x4c
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BNE      |loc_0801CF2E|
|loc_0801CF0C|
		LDRH r0, [r4, #0x12]
		CMP r0, #0
		BEQ      |loc_0801CF16|
		CMP r0, #0x10
		BNE      |loc_0801CF2E|
|loc_0801CF16|
		LDR r0, [pc, #0xdc]
		MOV r1, #0x27
		LDR r2, [pc, #0xdc]
		LSL r1, r1, #4
		ADD r1, r1, r2
		LDR r5, [pc, #0xd8]
		LDR r0, [r0]
		MOV r2, #0x40
		ADD r3, r6, #0
		ADD r0, r0, r5
		BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_0801CF2E|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		ADD r5, r4, #0
		ADD r5, #0xff
		ADD r5, #0xa1
		LDR r0, [r5]
		LDR r1, [sp, #0x34]
		ADD r6, r5, #4
		ADD r0, r0, r1
		LDR r1, [r5, #4]
		LDR r2, [sp, #0x38]
		STR r0, [sp, #0x1c]
		ADD r1, r1, r2
		STR r1, [sp, #0x20]
		STR r1, [sp, #0x28]
		STR r1, [sp, #0x30]
		STR r0, [sp, #0x24]
		STR r0, [sp, #0x2c]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x2c
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0801CFA8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_0801CF8E|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
|loc_0801CF8E|
		LDR r0, [sp, #0x2c]
		STR r0, [r5]
		LDR r0, [sp, #0x30]
		STR r0, [r6]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #0
		DCW     0xE714
|loc_0801CFA8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0801CFC8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
|loc_0801CFC8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #1
		DCW     0xE6FB
|sub_0801CFDA|
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801CFEE|
	LDR      r1, [pc, #0x14]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0801CFEE|
	POP      {r4, pc}
|sub_0801CFF0|
	DCW      0x1c34
	DCW      0x0300,0xe254
|sub_0801CFF6|
	LSR      r1, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LDR      r2, [sp, #0xb0]
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x84]
	SUB      sp, #0x10
	LDR      r0, [r0]
	MOV      r2, #0
	LDR      r3, [pc, #0x80]
	STR      r2, [sp, #8]
	CMP      r1, #0
	STR      r0, [sp, #0xc]
	STR      r3, [sp, #4]
	BEQ      |loc_0801D020|
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_0801D020|
	ADD      r1, r2, #0
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	LDR      r0, [pc, #0x68]
	MOV      r4, #1
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0801D040|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0801D040|
	ADD      r0, r4, #0
	ADD      sp, #0x10
	POP      {r4, pc}
|sub_0801D046|
|unk_0801D046|
	INCBIN	baserom.gba_0x1d046_0x1d04a.extracted
|sub_0801D04A|
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x3c]
	SUB      sp, #0x10
	LDR      r0, [r0]
	MOV      r2, #0
	LDR      r3, [pc, #0x38]
	STR      r2, [sp, #8]
	CMP      r1, #0
	STR      r0, [sp, #0xc]
	STR      r3, [sp, #4]
	BEQ      |loc_0801D066|
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_0801D066|
	ADD      r1, r2, #0
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	LDR      r0, [pc, #0x24]
	MOV      r4, #1
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0801D086|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0801D086|
	ADD      r0, r4, #0
	ADD      sp, #0x10
	POP      {r4, pc}
|sub_0801D08C|
|unk_0801D08C|
	INCBIN	baserom.gba_0x1d08c_0x1d08e.extracted
|sub_0801D08E|
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	CMP      r3, #0xcc
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #4]
	BX       lr
|sub_0801D0A0|
|unk_0801D0A0|
	INCBIN	baserom.gba_0x1d0a0_0x1d0a6.extracted
|sub_0801D0A6|
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0801D0C4|
	MOV      r0, #0xff
	ADD      r0, #0x35
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0801D0C4|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801D0C4|
|unk_0801D0C4|
		LDR r0, [pc, #0x32c]
		ADD r5, r4, #0
		STR r0, [r4]
		MOV r0, #0
		ADD r5, #0xff
		ADD r5, #1
		STR r0, [r4, #4]
		STR r0, [r5, #0xc]
		STR r0, [r5, #8]
		STR r0, [r5, #0x10]
		LDR r0, [pc, #0x31c]
		LDR r2, [pc, #0x320]
		STR r0, [r4]
		LDR r0, [r2, #0xc]
		LSL r1, r6, #2
		ADD r0, #0xe4
		ADD r0, r1, r0
		ADD r0, #4
		STR r0, [r5, #0x30]
		STR r6, [r5, #0x14]
		STR r7, [r5, #0x18]
		LDR r0, [r2, #0xc]
		MOV r3, #0x68
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r6, r0, r1
		MOV r0, #0x2c
		LDR r1, [pc, #0x2fc]
		MUL r0, r7
		ADD r7, r0, r1
		ADD r0, r6, #0
		BL       |loc_080135D2|
		LDRB r1, [r7, #0x15]
		CMP r0, r1
		BLT      |loc_0801D12A|
		LDRB r0, [r6, #0x14]
		LDR r1, [pc, #0x2ec]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDRB r0, [r0]
		LSL r0, r0, #0x1d
		LSR r0, r0, #0x1f
		BNE      |loc_0801D12A|
		MOV r0, #1
		B        |loc_0801D12C|
|loc_0801D12A|
		MOV r0, #0
|loc_0801D12C|
		STR r0, [r5, #0x20]
		LDR r2, [pc, #0x2cc]
		LDR r0, [r5, #0x30]
		LDR r2, [r2, #0xc]
		LDR r1, [r0]
		LDRB r2, [r2]
		LSR r1, r1, #0x1c
		SUB r1, #1
		CMP r1, r2
		BEQ      |loc_0801D144|
		MOV r1, #1
		B        |loc_0801D146|
|loc_0801D144|
		MOV r1, #0
|loc_0801D146|
		STR r1, [r5, #0x24]
		LDR r0, [r0]
		MOV r2, #1
		LSR r0, r0, #0x1c
		BNE      |loc_0801D152|
		MOV r2, #0
|loc_0801D152|
		ADD r0, r1, r2
		STR r0, [r5, #0x2c]
		STR r2, [r5, #0x28]
		ADD r0, r4, #0
		DCW     0xE7B2
|sub_0801D15C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x2a4]
	SUB      sp, #0x14
	LDR      r5, [r0, #0x5c]
	LDR      r7, [r0, #0x68]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x44
	STR      r2, [sp]
	MOV      r0, #0
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r2, #0
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	MOV      r1, #0xff
	ADD      r1, #0x1d
	STR      r0, [r1, r4]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r6, [pc, #0x268]
	MOV      r1, #0
	LDR      r2, [r6, #8]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x50
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
	MOV      r2, #0x44
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
	MOV      r3, #0x50
	MOV      r0, #0
	STR      r7, [sp]
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
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x1ec]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #9
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x1e4]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #3
	STR      r0, [sp, #4]
	MOV      r0, #5
	STR      r0, [sp, #8]
	MOV      r0, #0x1b
	STR      r0, [sp, #0xc]
	MOV      r0, #0x11
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	LDR      r2, [pc, #0x1d0]
	LDR      r1, [pc, #0x1c8]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0x1cc]
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
	BEQ      |loc_0801D27A|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0801D27A|
	POP      {r3, pc}
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r0, [r0, #0xc]
	MOV      r2, #0x12
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r0, #0x1f
	STR      r0, [r1, #4]
	STR      r2, [r1]
	MOV      r0, #1
	BX       lr
	PUSH     {r0, r4, r5, r6, r7, lr}
	SUB      sp, #0x138
	ADD      r4, sp, #0x104
	MOV      r2, #0x60
	MOV      r1, #0xc0
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x4f3e
	LDR      r5, [pc, #0x150]
	ADD      r3, sp, #0x100
	LDR      r0, [r5, #8]
	LDR      r1, [pc, #0x14c]
	STR      r0, [sp, #0x110]
	MOV      r0, #0
	STRB     r0, [r3, #4]
	MOV      r0, #1
	STRB     r0, [r3, #6]
	LDR      r0, [pc, #0x15c]
	STR      r0, [sp, #0x124]
	MOV      r0, #5
	STRB     r0, [r3, #7]
	LDR      r6, [sp, #0x138]
	MOV      r3, #0x2c
	ADD      r6, #0xff
	ADD      r6, #1
	LDR      r0, [r6, #0x18]
	MUL      r0, r3
	ADD      r7, r0, r1
	LDR      r0, [r7, #0x10]
	ADD      r1, sp, #4
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r2, [pc, #0x120]
	ADD      r1, sp, #4
	ADD      r2, #0x20
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x219e
	MOV      r0, #0x22
	STR      r0, [sp, #0x108]
	MOV      r0, #0x13
	STR      r0, [sp, #0x10c]
	LDRH     r0, [r7]
	LDR      r3, [pc, #0x114]
	LSL      r0, r0, #2
	LDR      r1, [r3, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	LDR      r0, [r6, #0x24]
	LDR      r4, [r6, #0xc]
	CMP      r0, #0
	BNE      |loc_0801D306|
	ADD      r4, #1
|loc_0801D306|
	LDR      r1, [r6, #0x28]
	CMP      r1, #0
	BNE      |loc_0801D312|
	CMP      r4, #1
	BLT      |loc_0801D312|
	ADD      r4, #1
|loc_0801D312|
	LDR      r1, [pc, #0xe8]
	CMP      r0, #0
	LDR      r5, [r1, #0x1c]
	LDR      r7, [r1, #0x18]
	BEQ      |loc_0801D368|
	STR      r7, [sp, #0x108]
	STR      r5, [sp, #0x10c]
	LDR      r2, [r6, #0x20]
	MOV      r1, #0x75
	CMP      r2, #0
	ADD      r0, sp, #0x104
	BEQ      |loc_0801D332|
	MOV      r1, #6
	CMP      r4, #0
	BEQ      |loc_0801D332|
	MOV      r1, #2
|loc_0801D332|
	ADD      r3, sp, #0x100
	STRB     r1, [r3, #7]
	LDR      r1, [pc, #0xc4]
	MOV      r3, #0x68
	LDR      r1, [r1, #0xc]
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1, #0x14]
	LDR      r2, [pc, #0xb8]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDRH     r1, [r1, #2]
	LDR      r3, [pc, #0xb0]
	LSL      r1, r1, #2
	LDR      r2, [r3, r1]
	MOV      r1, #0xff
	ADD      r1, #0x19
	LDR      r1, [r3, r1]
	BL       |inc_0x03d784_0x041118| + 0x512
	ADD      r5, #0xc
|loc_0801D368|
	LDR      r0, [r6, #0x28]
	CMP      r0, #0
	BEQ      |loc_0801D3B8|
	MOV      r1, #6
	CMP      r4, #1
	ADD      r0, sp, #0x104
	STR      r7, [sp, #0x108]
	STR      r5, [sp, #0x10c]
	BEQ      |loc_0801D37C|
	MOV      r1, #2
|loc_0801D37C|
	ADD      r3, sp, #0x100
	STRB     r1, [r3, #7]
	LDR      r2, [r6, #0x30]
	MOV      r3, #0x68
	LDR      r2, [r2]
	LDR      r1, [pc, #0x74]
	LSR      r2, r2, #0x1c
	SUB      r2, #1
	LDR      r1, [r1, #0xc]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1, #0x14]
	LDR      r2, [pc, #0x68]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDRH     r1, [r1, #2]
	LDR      r3, [pc, #0x60]
	LSL      r1, r1, #2
	LDR      r2, [r3, r1]
	MOV      r1, #0xff
	ADD      r1, #0x1d
	LDR      r1, [r3, r1]
	BL       |inc_0x03d784_0x041118| + 0x512
	ADD      r5, #0xc
|loc_0801D3B8|
	MOV      r1, #6
	CMP      r4, #2
	ADD      r0, sp, #0x104
	STR      r7, [sp, #0x108]
	STR      r5, [sp, #0x10c]
	BEQ      |loc_0801D3C6|
	MOV      r1, #2
|loc_0801D3C6|
	ADD      r3, sp, #0x100
	STRB     r1, [r3, #7]
	MOV      r1, #0xff
	ADD      r1, #0x21
	LDR      r3, [pc, #0x38]
	ADD      r4, r0, #0
	LDR      r1, [r3, r1]
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r1, r4, #0
	LDR      r0, [sp, #0x138]
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x2c]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	ADD      r0, sp, #0x104
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x13c
	POP      {r4, r5, r6, r7, pc}
|sub_0801D3F4|
	DCW      0x920c
	DCW      0x0804,0xafcc,0x0804,0xe9a8,0x0871,0x82ec,0x086f,0x82ec
	DCW      0x086b,0xbce8,0x0806,0xf800
|sub_0801D40E|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	SUB      r3, r0, #6
	LSL      r0, r0, #0
	DCW      0xf5a5,0x0803
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x1c0]
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1b8]
	LDR      r1, [r7, #4]
	MOV      r3, #0
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x1b8]
	CMP      r2, #0
	SUB      sp, #0x24
	BEQ      |sub_0801D44C|
	CMP      r2, #1
	BNE      |loc_0801D50A|
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #3
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
|sub_0801D44C|
|unk_0801D44C|
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r4, #0xff
		ADD r4, #1
		LDR r0, [r4, #0xc]
		LDR r1, [r4, #0x24]
		CMP r1, #0
		BNE      |loc_0801D460|
		ADD r0, #1
|loc_0801D460|
		LDR r1, [r4, #0x28]
		CMP r1, #0
		BNE      |loc_0801D46C|
		CMP r0, #1
		BLT      |loc_0801D46C|
		ADD r0, #1
|loc_0801D46C|
		CMP r0, #0
		BEQ      |loc_0801D4C4|
		CMP r0, #1
		BEQ      |loc_0801D4E4|
		CMP r0, #2
		BNE      |loc_0801D50A|
		MOV r1, #0x2f
		LDR r0, [r7, #0x14]
		LSL r1, r1, #6
		ADD r5, r0, r1
		MOV r2, #0
		MOV r1, #9
		LDR r0, [r5, #0x38]
		BL       |loc_08011C70|
		ADD r6, r0, #0
		LDR r0, [r7, #0x10]
		ADD r0, #0x80
		LDR r0, [r0, #0x10]
		CMP r0, #0
		BNE      |loc_0801D4BC|
		CMP r6, #0
		BEQ      |loc_0801D4BC|
		ADD r2, r7, #0
		MOV r7, #0x61
		LDR r0, [r5, #0x38]
		LSL r7, r7, #4
		ADD r1, r0, r7
		LDR r3, [pc, #0x144]
		LDR r1, [r1]
		LDR r3, [r3]
		ADD r1, r1, r3
		CMP r1, #8
		BGE      |loc_0801D4BC|
		BL       |loc_080116FC|
		MOV r1, #0xff
		ADD r1, #1
		CMP r0, r1
		DCW     0xDA27
|loc_0801D4BC|
		MOV r0, #4
		BL       |inc_0x03d784_0x041118| + 0xf2
		DCW     0xE054
|loc_0801D4C4|
		LDR r0, [r4, #0x20]
		CMP r0, #0
		BEQ      |loc_0801D4E0|
		LDR r0, [r7, #0xc]
		ADD r4, #0x14
		LDRB r1, [r0]
		LDMIA r4!, {r2, r3}
		BL       |inc_0x0158_0x143f2| + 0x4470
		MOV r0, #1
		BL       |inc_0x03d784_0x041118| + 0xf2
		MOV r0, #1
		DCW     0xE7B3
|loc_0801D4E0|
		MOV r0, #0
		DCW     0xE7B1
|loc_0801D4E4|
		LDR r0, [r4, #0x30]
		MOV r3, #0x2c
		LDR r0, [r0]
		LDR r2, [pc, #0x104]
		LSL r1, r0, #4
		LSR r1, r1, #4
		MUL r1, r3
		ADD r1, r1, r2
		LDRB r2, [r1, #0x14]
		LSR r1, r0, #0x1c
		SUB r1, #1
		LDR r0, [r7, #0xc]
		BL       |loc_08004544|
		MOV r0, #3
		BL       |inc_0x03d784_0x041118| + 0xf2
		MOV r0, #1
		DCW     0xE79E
|loc_0801D50A|
|unk_0801D50A|
		B        |loc_0801D572|
		LDR r5, [r5, #0x38]
		ADD r1, r6, #0
		ADD r0, sp, #0xc
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ASR r1, r1, #1
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x20]
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		LDR r6, [r4, #0x18]
		MOV r0, #0x14
		DCW     0xF020
		DCW     0xF83F
		CMP r0, #0
		BEQ      |loc_0801D550|
		MOV r1, #1
		STR r1, [r0, #4]
		LDR r1, [pc, #0xb0]
		ADD r2, sp, #0x1c
		STR r1, [r0]
		LDMIA r2!, {r1, r2}
		ADD r0, #8
		STMIA r0!, {r1, r2, r6}
		SUB r0, #0x14
|loc_0801D550|
		ADD r1, r5, r7
		LDR r2, [r1]
		ADD r3, r2, #1
		STR r3, [r1]
		LSL r2, r2, #2
		ADD r1, r2, r1
		STR r0, [r1, #4]
		LDR r0, [pc, #0x84]
		LDR r1, [r4, #0x14]
		LDR r0, [r0, #0xc]
		BL       |inc_0x0158_0x143f2| + 0x44fe
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0xf2
		MOV r0, #1
		DCW     0xE76A
|loc_0801D572|
		MOV r0, #0
		DCW     0xE768
|sub_0801D576|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [pc, #0x68]
	LDR      r3, [pc, #0x68]
	LDR      r1, [r1]
	LDR      r5, [pc, #0x68]
	LDRH     r1, [r1, #4]
	LDR      r3, [r3, #4]
	ADD      r4, r0, #0
	LDR      r2, [pc, #0x58]
	ADD      r4, #0xff
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	ADD      r4, #1
	MOV      r7, #0
	SUB      r5, #0xc
	ADD      r6, r3, r2
	CMP      r1, #0
	BEQ      |loc_0801D5B4|
	ADD      r1, r5, #0
	ADD      r3, r7, #0
	MOV      r2, #0x40
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0xc]
	SUB      r0, #1
	STR      r0, [r4, #0xc]
	BPL      |loc_0801D5B2|
	LDR      r0, [r4, #0x2c]
	STR      r0, [r4, #0xc]
|loc_0801D5B2|
	STR      r7, [r4, #0x10]
|loc_0801D5B4|
	LDR      r0, [pc, #0x2c]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1f
	BEQ      |loc_0801D5DC|
	ADD      r1, r5, #0
	ADD      r3, r7, #0
	MOV      r2, #0x40
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0xc]
	ADD      r0, #1
	STR      r0, [r4, #0xc]
	LDR      r1, [r4, #0x2c]
	CMP      r0, r1
	BLE      |loc_0801D5DA|
	STR      r7, [r4, #0xc]
|loc_0801D5DA|
	STR      r7, [r4, #0x10]
|loc_0801D5DC|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801D5E0|
	DCW      0x05c4
	DCW      0x0000,0xe9a8
|sub_0801D5E6|
	LSR      r1, r6, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	SUB      r4, r7, r3
	LSL      r0, r0, #0xc
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	LDR      r2, [sp, #0x2f0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x35c]
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r1, #0xc]
	MOV      r3, #0x68
	LDRB     r2, [r1]
	ADD      r5, r0, #0
	ADD      r5, #0xff
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r4, r1, r2
	ADD      r5, #1
	LDR      r1, [r5, #0x14]
	LSL      r1, r1, #2
	ADD      r2, r1, r4
	ADD      r2, #0x3c
	LDR      r6, [r2]
	ADD      r1, r5, #0
	ADD      r1, #0x50
	LDR      r0, [r1]
	CMP      r0, #0
	BEQ      |loc_0801D63C|
	ADD      r0, r2, #0
	LDR      r2, [r5, #0x3c]
	LSL      r2, r2, #3
	ADD      r1, r2, r1
	LDR      r1, [r1, #4]
	LSL      r1, r1, #4
	LSR      r1, r1, #4
|loc_0801D634|
	STR      r1, [r0]
	LDR      r2, [r0]
	CMP      r2, r1
	BNE      |loc_0801D634|
|loc_0801D63C|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x13b0e
	LDR      r0, [r5, #0x14]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	ADD      r0, #0x3c
|loc_0801D64A|
	STR      r6, [r0]
	LDR      r1, [r0]
	CMP      r1, r6
	BNE      |loc_0801D64A|
	ADD      r0, r4, #0
	ADD      r0, #0x4c
	LDRH     r0, [r0]
	STR      r0, [r5, #0x28]
	ADD      r0, r4, #0
	ADD      r0, #0x4e
	LDRH     r0, [r0]
	STR      r0, [r5, #0x2c]
	ADD      r0, r4, #0
	ADD      r0, #0x50
	LDRH     r0, [r0]
	STR      r0, [r5, #0x30]
	ADD      r0, r4, #0
	ADD      r0, #0x54
	LDRH     r0, [r0]
	STR      r0, [r5, #0x34]
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	ADD      r5, r0, #0
	CMP      r0, #0
	BNE      |sub_0801D68C|
	LDR      r0, [pc, #0x2dc]
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BNE      |sub_0801D68C|
	ADD      r0, r5, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801D68C|
|unk_0801D68C|
		LDR r0, [pc, #0x2d0]
		MOV r1, #0
		STMIA r5!, {r0, r1}
		SUB r5, #8
		ADD r4, r5, #0
		ADD r4, #0xff
		ADD r4, #1
		MOV r0, #0
		STR r0, [r4, #0xc]
		STR r0, [r4, #8]
		STR r0, [r4, #0x10]
		LDR r0, [pc, #0x2c0]
		ADD r7, r4, #0
		STR r0, [r5]
		MOV r0, #0
		ADD r7, #0x50
		STR r0, [r7]
		LDR r0, [pc, #0x2a8]
		STR r6, [r4, #0x14]
		LDR r0, [r0, #0xc]
		MOV r3, #0x68
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r6, r0, r1
		ADD r0, r6, #0
		BL       |loc_08013C66|
		ADD r0, r6, #0
		ADD r0, #0x4c
		LDRH r0, [r0]
		STR r0, [r4, #0x28]
		STR r0, [r4, #0x18]
		ADD r0, r6, #0
		ADD r0, #0x4e
		LDRH r0, [r0]
		STR r0, [r4, #0x2c]
		STR r0, [r4, #0x1c]
		ADD r0, r6, #0
		ADD r0, #0x50
		LDRH r0, [r0]
		STR r0, [r4, #0x30]
		STR r0, [r4, #0x20]
		ADD r0, r6, #0
		ADD r0, #0x54
		LDRH r0, [r0]
		STR r0, [r4, #0x34]
		STR r0, [r4, #0x24]
		MOV r0, #0
		LDR r1, [pc, #0x264]
		STR r0, [r4, #0x3c]
		LDR r1, [r1, #0xc]
		ADD r1, #0xe4
		LDR r2, [r1]
		CMP r2, #0
		BLE      |loc_0801D74C|
|loc_0801D700|
		LSL r2, r0, #2
		ADD r2, r2, r1
		ADD r2, #4
		LDR r3, [r2]
		LSL r6, r3, #4
		MOV ip, r3
		MOV r3, #0x2c
		LSR r6, r6, #4
		MUL r3, r6
		LDR r6, [pc, #0x254]
		ADD r3, r3, r6
		LDRB r3, [r3, #0x14]
		LDR r6, [r4, #0x14]
		CMP r3, r6
		BNE      |loc_0801D744|
		LDR r6, [pc, #0x238]
		MOV r3, ip
		LDR r6, [r6, #0xc]
		LSR r3, r3, #0x1c
		LDRB r6, [r6]
		SUB r3, #1
		CMP r3, r6
		BNE      |loc_0801D732|
		LDR r3, [r7]
		STR r3, [r4, #0x3c]
|loc_0801D732|
		LDR r3, [r7]
		ADD r6, r3, #1
		LSL r3, r3, #3
		ADD r3, r3, r7
		STR r6, [r7]
		LDR r2, [r2]
		ADD r3, #4
		STR r0, [r3, #4]
		STR r2, [r3]
|loc_0801D744|
		LDR r2, [r1]
		ADD r0, #1
		CMP r2, r0
		BGT      |loc_0801D700|
|loc_0801D74C|
		LDR r0, [r4, #0x3c]
		SUB r0, #2
		STR r0, [r4, #0x38]
		BPL      |loc_0801D758|
		MOV r0, #0
		STR r0, [r4, #0x38]
|loc_0801D758|
		ADD r0, r5, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x1206
		ADD r0, r5, #0
		DCW     0xE793
	INCBIN  baserom.gba_0x1d762_0x1d790.extracted
|sub_0801D790|
	MOV      r0, #0
	STR      r0, [r1, #8]
	POP      {r4, r5}
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1cc]
	SUB      sp, #0x14
	LDR      r6, [r0, #0x5c]
	LDR      r0, [r0, #0x68]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x84
	STR      r0, [sp, #0x10]
	MOV      r0, #0
	STR      r2, [sp]
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r2, #0
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #0x41
	STR      r0, [r5]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r7, [pc, #0x184]
	MOV      r1, #0
	LDR      r2, [r7, #8]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
	STR      r6, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r6, #0
	LDR      r0, [r7, #8]
	BL       |inc_0x03d784_0x041118| + 0x2864
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	ADD      r6, r0, #0
	MOV      r1, #1
	ADD      r6, #0x1e
	MOV      r2, #0x84
	STR      r2, [sp]
	ADD      r3, r6, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r7, #8]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	LDR      r2, [sp, #0x10]
	STR      r1, [sp, #8]
	STR      r2, [sp]
	ADD      r2, r6, #0
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
	LDR      r1, [pc, #0xd8]
	MOV      r0, #0x84
	LDR      r3, [r1, r0]
	LDR      r2, [r7, #8]
	STR      r3, [sp]
	MOV      r1, #0
	MOV      r6, #0x14
	ADD      r3, r6, #0
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
	LDR      r0, [pc, #0xb0]
	MOV      r1, #2
	LDR      r3, [r0, #8]
	LDR      r2, [r7, #8]
	STR      r3, [sp]
	ADD      r3, r6, #0
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
	MOV      r0, #0xff
	ADD      r0, #0x51
	LDR      r0, [r0, r4]
	CMP      r0, #0
	BEQ      |sub_0801D94C|
	MOV      r2, #1
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1e
	MOV      r1, #1
	MOV      r6, #0x9e
	ADD      r3, r6, #0
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #2
	STR      r0, [sp, #4]
	MOV      r2, #2
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	STR      r0, [r5, #4]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	STR      r2, [sp, #0xc]
	MOV      r2, #0x4b
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #3
	ADD      r3, r6, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	MOV      r2, #3
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	STR      r0, [r5, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0xe16
	ADD      r1, r0, #0
	STR      r0, [r5, #0xc]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_0801D94C|
|unk_0801D94C|
		MOV r0, #0
		STR r0, [r5, #4]
		STR r0, [r5, #8]
		LDR r1, [r5]
		STR r0, [r1, #8]
		DCW     0xE7F7
	INCBIN  baserom.gba_0x1d958_0x1d95a.extracted
|sub_0801D95A|
	LSR      r1, r6, #1
	LSR      r4, r4, #4
	LSL      r0, r0, #0
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      r0, sp, #0x3d0
	LSR      r4, r0, #0x20
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	ADD      r0, #0xff
	ADD      r0, #1
	ADD      r0, #0x38
	LDMIA    r0!, {r0, r2}
	SUB      r0, r2, r0
	LSL      r0, r0, #4
	ADD      r0, #0x24
	STR      r0, [r1, #4]
	MOV      r2, #0x12
	STR      r2, [r1]
	MOV      r0, #1
	BX       lr
|sub_0801D988|
|unk_0801D988|
		PUSH {r0, r4, r5, r6, r7, lr}
		SUB sp, #0x158
		MOV r2, #0xa0
		MOV r1, #0xf0
		ADD r0, sp, #0x11c
		BL       |loc_0803F540|
		MOV r3, #0
		MOV r2, #0x24
		ADD r1, sp, #0x11c
		LDR r0, [sp, #0x158]
		BL       |loc_08006718|
		LDR r2, [sp, #0x158]
		MOV r5, #1
		ADD r2, #0xff
		ADD r2, #0x51
		STR r2, [sp, #0x154]
		LDR r0, [r2]
		LDR r7, [pc, #0x2b8]
		CMP r0, #0
		BEQ      |loc_0801DA8A|
		LDR r2, [sp, #0x158]
		ADD r0, r5, #0
		ADD r2, #0xff
		ADD r2, #0x41
		LDR r1, [r2, #4]
		LDR r4, [sp, #0x158]
		ADD r4, #0xff
		ADD r4, #1
		LDR r3, [r4, #0x3c]
		CMP r3, #0
		BGT      |loc_0801D9CC|
		MOV r0, #0
|loc_0801D9CC|
		STR r0, [r1, #8]
		LDR r0, [r2, #8]
		LDR r2, [sp, #0x154]
		LDR r1, [r2]
		LDR r2, [r4, #0x3c]
		SUB r1, #1
		CMP r1, r2
		BLE      |loc_0801D9E0|
		MOV r1, #1
		B        |loc_0801D9E2|
|loc_0801D9E0|
		MOV r1, #0
|loc_0801D9E2|
		STR r1, [r0, #8]
		MOV r1, #0xa5
		MOV r3, #0x4b
		MOV r2, #0x2d
		ADD r6, sp, #0x11c
		ADD r0, r6, #0
		BL       |loc_080051B0|
		MOV r3, #0xe0
		MOV r2, #0x5e
		MOV r1, #0x10
		ADD r0, r6, #0
		BL       |loc_08005154|
		LDR r6, [pc, #0x26c]
		MOV r3, #0x68
		LDR r0, [r6, #0xc]
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		STR r0, [sp, #0x118]
		BL       |loc_08013C66|
		LDR r0, [r6, #8]
		ADD r3, sp, #0x100
		STR r0, [sp, #0x128]
		MOV r0, #0
		STRB r0, [r3, #0x1c]
		STRB r5, [r3, #0x1e]
		LDR r0, [pc, #0x24c]
		MOV r6, #0xaf
		STR r0, [sp, #0x13c]
		MOV r0, #0x28
		STR r0, [sp, #0x124]
		STR r6, [sp, #0x120]
		LDR r0, [r4, #0x18]
		LDR r2, [r4, #0x28]
		CMP r2, r0
		BNE      |loc_0801DA3A|
		MOV r0, #0x37
		B        |loc_0801DA44|
|loc_0801DA3A|
		CMP r2, r0
		BLE      |loc_0801DA42|
		MOV r0, #0x38
		B        |loc_0801DA44|
|loc_0801DA42|
		MOV r0, #0x39
|loc_0801DA44|
		LSL r0, r0, #2
		LDR r1, [r7, r0]
		ADD r5, r7, #0
		ADD r7, sp, #0x11c
		ADD r0, r7, #0
		BL       |sub_0803DC96|
		MOV r0, #0x34
		STR r0, [sp, #0x124]
		STR r6, [sp, #0x120]
		LDR r0, [r4, #0x1c]
		LDR r2, [r4, #0x2c]
		CMP r2, r0
		BNE      |loc_0801DA64|
		MOV r0, #0x3a
		B        |loc_0801DA6E|
|loc_0801DA64|
		CMP r2, r0
		BLE      |loc_0801DA6C|
		MOV r0, #0x3b
		B        |loc_0801DA6E|
|loc_0801DA6C|
		MOV r0, #0x3c
|loc_0801DA6E|
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, r7, #0
		BL       |sub_0803DC96|
		MOV r0, #0x40
		STR r0, [sp, #0x124]
		STR r6, [sp, #0x120]
		LDR r0, [r4, #0x20]
		LDR r2, [r4, #0x30]
		CMP r2, r0
		BNE      |loc_0801DA8C|
		MOV r0, #0x3d
		B        |loc_0801DA96|
|loc_0801DA8A|
		B        |sub_0801DC20|
|loc_0801DA8C|
		CMP r2, r0
		BLE      |loc_0801DA94|
		MOV r0, #0x3e
		B        |loc_0801DA96|
|loc_0801DA94|
		MOV r0, #0x3f
|loc_0801DA96|
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, r7, #0
		BL       |sub_0803DC96|
		MOV r0, #0xaf
		STR r0, [sp, #0x120]
		MOV r0, #0x4c
		STR r0, [sp, #0x124]
		LDR r0, [r4, #0x24]
		LDR r2, [r4, #0x34]
		CMP r2, r0
		BNE      |loc_0801DAB4|
		MOV r0, #0x40
		B        |loc_0801DABE|
|loc_0801DAB4|
		CMP r2, r0
		BLE      |loc_0801DABC|
		MOV r0, #0x41
		B        |loc_0801DABE|
|loc_0801DABC|
		MOV r0, #0x42
|loc_0801DABE|
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, r7, #0
		BL       |sub_0803DC96|
		LDR r2, [sp, #0x154]
		LDR r0, [r4, #0x3c]
		MOV r3, #0x2c
		LSL r0, r0, #3
		ADD r0, r0, r2
		LDR r0, [r0, #4]
		LDR r2, [pc, #0x19c]
		LSL r0, r0, #4
		LSR r0, r0, #4
		MUL r0, r3
		ADD r6, r0, r2
		MOV r0, #0xaf
		STR r0, [sp, #0x120]
		MOV r0, #0x58
		STR r0, [sp, #0x124]
		LDR r0, [sp, #0x118]
		BL       |loc_080135D2|
		LDRB r2, [r6, #0x15]
		CMP r0, r2
		BLT      |loc_0801DAF6|
		MOV r0, #0x43
		B        |loc_0801DAF8|
|loc_0801DAF6|
		MOV r0, #0x44
|loc_0801DAF8|
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, sp, #0x11c
		BL       |sub_0803DC96|
		LDR r0, [r4, #0x3c]
		LDR r2, [r4, #0x38]
		SUB r1, r0, #3
		CMP r2, r1
		BGE      |loc_0801DB0E|
		STR r1, [r4, #0x38]
|loc_0801DB0E|
		LDR r1, [r4, #0x38]
		CMP r0, r1
		BGE      |loc_0801DB16|
		STR r0, [r4, #0x38]
|loc_0801DB16|
		MOV r6, #0
|loc_0801DB18|
		LDR r0, [r4, #0x38]
		LDR r2, [sp, #0x154]
		ADD r0, r0, r6
		LDR r1, [r2]
		CMP r1, r0
		BLE      |loc_0801DC06|
		LDR r2, [sp, #0x154]
		LSL r1, r0, #3
		ADD r7, r1, r2
		ADD r7, #4
		LDR r1, [r7]
		MOV r3, #0x2c
		LSL r1, r1, #4
		LSR r1, r1, #4
		LDR r2, [pc, #0x13c]
		MUL r1, r3
		ADD r5, r1, r2
		LDR r1, [r4, #0x3c]
		CMP r1, r0
		BNE      |loc_0801DB7A|
		MOV r0, #2
		ADD r3, sp, #0x100
		STRB r0, [r3, #0x1f]
		MOV r0, #0x13
		STR r0, [sp, #0x120]
		MOV r0, #0x6a
		STR r0, [sp, #0x124]
		MOV r0, #0xc
		STRB r0, [r3, #0x1d]
		LDRH r0, [r5, #2]
		LDR r1, [pc, #0x110]
		LSL r0, r0, #2
		LDR r2, [r1, r0]
		MOV r1, #0xcc
		ADD r0, sp, #0x11c
		BL       |loc_0803DD66|
		LDR r0, [sp, #0x118]
		BL       |loc_080135D2|
		LDRB r1, [r5, #0x15]
		CMP r0, r1
		BLT      |loc_0801DB72|
		MOV r0, #6
		B        |loc_0801DB74|
|loc_0801DB72|
		MOV r0, #0x75
|loc_0801DB74|
		ADD r3, sp, #0x100
		STRB r0, [r3, #0x1f]
		B        |loc_0801DB90|
|loc_0801DB7A|
		LDR r0, [sp, #0x118]
		BL       |loc_080135D2|
		LDRB r1, [r5, #0x15]
		CMP r0, r1
		BLT      |loc_0801DB8A|
		MOV r0, #2
		B        |loc_0801DB8C|
|loc_0801DB8A|
		MOV r0, #0x75
|loc_0801DB8C|
		ADD r3, sp, #0x100
		STRB r0, [r3, #0x1f]
|loc_0801DB90|
		LSL r0, r6, #4
		STR r0, [sp, #0x150]
		ADD r0, #0x1c
		STR r0, [sp, #0x10c]
		MOV r0, #0x20
		STR r0, [sp, #0x110]
		LDR r0, [sp, #0x10c]
		MOV r1, #0x10
		ADD r0, r0, r1
		STR r1, [sp, #0x108]
		STR r0, [sp, #0x114]
		LDR r0, [r5, #0x10]
		ADD r1, sp, #8
		BL       |inc_0x03d784_0x041118| + 0x1bc
		ADD r2, sp, #0x108
		ADD r1, sp, #8
		ADD r0, sp, #0x11c
		BL       |inc_0x03d784_0x041118| + 0x219e
		LDR r0, [sp, #0x150]
		MOV r1, #0x22
		ADD r0, #0x28
		STR r0, [sp, #0x124]
		STR r1, [sp, #0x120]
		LDR r0, [r7]
		LSR r0, r0, #0x1c
		LDRH r0, [r5]
		BEQ      |loc_0801DC08|
		LDR r5, [pc, #0x9c]
		LSL r0, r0, #2
		LDR r0, [r5, r0]
		STR r0, [sp, #4]
		MOV r0, #0xff
		ADD r0, #0x15
		LDR r1, [r5, r0]
		LDR r0, [sp, #0x128]
		BL       |sub_0803FFE8|
		MOV r1, #0x7a
		SUB r1, r1, r0
		ADD r0, sp, #0x11c
		LDR r2, [sp, #4]
		BL       |loc_0803DCC4|
		LDR r0, [r7]
		LDR r1, [pc, #0x88]
		LSR r0, r0, #0x1c
		SUB r0, #1
		LDRB r0, [r1, r0]
		ADD r3, sp, #0x100
		STRB r0, [r3, #0x1f]
		MOV r0, #0xff
		ADD r0, #0x15
		LDR r1, [r5, r0]
		ADD r0, sp, #0x11c
		BL       |loc_0803DADA|
		B        |loc_0801DC16|
|loc_0801DC06|
		DCW     0xE01F
|loc_0801DC08|
		LDR r1, [pc, #0x5c]
		LSL r0, r0, #2
		LDR r2, [r1, r0]
		MOV r1, #0x7a
		ADD r0, sp, #0x11c
		BL       |loc_0803DCC4|
|loc_0801DC16|
		ADD r6, #1
		CMP r6, #4
		BGE      |loc_0801DC1E|
		B        |loc_0801DB18|
|loc_0801DC1E|
		DCW     0xE013
|sub_0801DC20|
	LDR      r6, [pc, #0x48]
	ADD      r3, sp, #0x100
	LDR      r0, [r6, #8]
	STR      r0, [sp, #0x128]
	MOV      r0, #0x78
	STRB     r5, [r3, #0x1c]
	STR      r0, [sp, #0x120]
	MOV      r0, #0x58
	STR      r0, [sp, #0x124]
	LDR      r0, [pc, #0x3c]
	STRB     r5, [r3, #0x1e]
	STR      r0, [sp, #0x13c]
	MOV      r0, #2
	STRB     r0, [r3, #0x1f]
	MOV      r0, #0xff
	ADD      r0, #0x25
	LDR      r1, [r7, r0]
	ADD      r0, sp, #0x11c
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r6, sp, #0x11c
	ADD      r1, r6, #0
	LDR      r0, [sp, #0x158]
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x28]
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	ADD      r0, sp, #0x11c
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x15c
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	DCW      0xe9d8,0x0871,0xf5a5,0x0803
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	STRB     r0, [r2, #0x16]
	LSR      r3, r5, #1
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	PUSH     {r4, r5, r6, r7}
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #0x51
	MOV      r1, #0
	LDR      r2, [pc, #0x2f8]
	STR      r1, [r4]
	LDR      r2, [r2, #0xc]
	ADD      r2, #0xe4
	LDR      r3, [r2]
	CMP      r3, #0
	BLE      |loc_0801DCD0|
	ADD      r5, r4, #0
	LDR      r6, [pc, #0x2ec]
	SUB      r5, #0x50
|loc_0801DC9E|
	LSL      r0, r1, #2
	ADD      r0, r0, r2
	ADD      r0, #4
	LDR      r3, [r0]
	LSL      r7, r3, #4
	LSR      r7, r7, #4
	MOV      r3, #0x2c
	MUL      r3, r7
	ADD      r3, r3, r6
	LDRB     r3, [r3, #0x14]
	LDR      r7, [r5, #0x14]
	CMP      r3, r7
	BNE      |loc_0801DCC8|
	LDR      r3, [r4]
	ADD      r7, r3, #1
	LSL      r3, r3, #3
	STR      r7, [r4]
	LDR      r0, [r0]
	ADD      r3, r3, r4
	ADD      r3, #4
	STMIA    r3!, {r0, r1}
|loc_0801DCC8|
	LDR      r0, [r2]
	ADD      r1, #1
	CMP      r0, r1
	BGT      |loc_0801DC9E|
|loc_0801DCD0|
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_0801DCD4|
|unk_0801DCD4|
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		CMP r2, #8
		BHS      |loc_0801DCE6|
		DCW     0xA302
		ADD r3, r3, r2
		LDRH r3, [r3, r2]
		LSL r3, r3, #1
		ADD pc, r3
|loc_0801DCE6|
		B        |loc_0801DDEC|
	INCBIN  baserom.gba_0x1dce8_0x1dd72.extracted
|sub_0801DD72|
	MOV      r0, #0xff
	ADD      r0, #0x19
	LDR      r4, [r5, #0x14]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801DD9A|
	LDR      r1, [pc, #0x210]
	MOV      r3, #0
	STMIA    r0!, {r1, r3}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r3, [r1, #0xc]
	STR      r3, [r1, #8]
	LDR      r2, [pc, #0x208]
	STR      r3, [r1, #0x10]
	STR      r2, [r0]
	STR      r4, [r1, #0x14]
|loc_0801DD9A|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801DDA2|
|unk_0801DDA2|
	INCBIN  baserom.gba_0x1dda2_0x1ddec.extracted
|loc_0801DDEC|
		B        |loc_0801DF7E|
	INCBIN  baserom.gba_0x1ddee_0x1df7e.extracted
|loc_0801DF7E|
		MOV r0, #0
		DCW     0xE70E
|sub_0801DF82|
	LSL      r0, r0, #0
	DCW      0xe9d8,0x0871
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      r0, sp, #0x320
	LSR      r4, r0, #0x20
	STR      r5, [sp, #0x220]
	LSR      r4, r0, #0x20
|unk_0801DFA0|
	INCBIN	baserom.gba_0x1dfa0_0x1dfa2.extracted
	LSR      r4, r0, #0x20
	LDR      r0, [sp, #0x3c0]
	LSR      r4, r0, #0x20
	ADD      r4, r2, r4
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0x24]
	PUSH     {r4, lr}
	LDR      r1, [r0]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1c
	LSR      r1, r1, #0x1f
	BEQ      |sub_0801DFCE|
	LDR      r0, [r0, #4]
	LDR      r4, [pc, #0x1c]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r0, r4
	LDR      r1, [pc, #0x10]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	POP      {r4, pc}
|sub_0801DFCE|
|unk_0801DFCE|
		MOV r0, #0
		POP {r4, pc}
|sub_0801DFD2|
	LSL      r0, r0, #0
	DCW      0xe9d8,0x0871
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	PUSH     {r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x24
	BNE      |sub_0801DFFC|
	MOV      r0, #0x48
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0801DFFC|
	ADD      r0, r4, #0
	ADD      sp, #0x24
	POP      {r4, r5, pc}
|sub_0801DFFC|
|unk_0801DFFC|
; cited by 0x00436D96 (a pool word names 0x0801E010)
		MOV r1, #1
		LSL r1, r1, #0xa
		ADD r2, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x138]
		STR r0, [r4]
		MOV r0, #0
		STR r0, [r4, #0x40]
		MOV r0, #1
		STR r0, [r4, #0x44]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		LDR r1, [r4, #0x1c]
		ADD r0, sp, #0xc
		BL       |loc_0800FE34|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #0x20]
		ASR r1, r1, #1
		STR r0, [sp, #8]
		LDR r0, [pc, #0x10c]
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		LDR r2, [sp, #0x20]
		STR r0, [r4, #0x18]
		LSL r1, r1, #8
		LSL r2, r2, #8
		STR r1, [r4, #0x20]
		STR r2, [r4, #0x24]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [r4, #0x1c]
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #0x10]
		ADD r0, r1, #0
		STR r1, [sp, #0xc]
		LDR r1, [sp, #0x10]
		STR r0, [sp, #0x14]
		ADD r0, r1, #0
		STR r1, [sp, #0x18]
		LDR r1, [r4, #0x1c]
		ADD r1, #0xff
		ADD r1, #0x91
		LDRB r1, [r1, #0xd]
		LSR r1, r1, #1
		ADD r0, r0, r1
		ADD r0, #1
		STR r0, [r4, #4]
		ADD r0, r4, #0
		DCW     0xE7BB
		PUSH {r4, lr}
		ADD r4, r0, #0
		ADD r0, #0x40
		LDMIA r0!, {r0, r1}
		SUB sp, #0x20
		CMP r1, #0
		BEQ      |loc_0801E09C|
		ADD r0, #1
		STR r0, [r4, #0x40]
		CMP r0, #0x38
		BLT      |loc_0801E0AE|
		MOV r0, #0x18
		STR r0, [r4, #0x40]
		B        |loc_0801E0AE|
|loc_0801E09C|
		CMP r0, #0x18
		BLT      |sub_0801E0A6|
		MOV r0, #0x17
		STR r0, [r4, #0x40]
		B        |loc_0801E0AE|
|sub_0801E0A6|
	CMP      r0, #0
	BLE      |loc_0801E0AE|
	SUB      r0, #1
	STR      r0, [r4, #0x40]
|loc_0801E0AE|
	ADD      r0, sp, #8
	LDR      r1, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x10]
	LDR      r2, [sp, #0x14]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0xc]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r0, [sp, #0x1c]
	LDR      r2, [sp, #0x1c]
	STR      r1, [sp]
	STR      r1, [sp, #0x18]
	LSL      r1, r1, #8
	STR      r0, [sp, #4]
	STR      r1, [r4, #0x20]
	LSL      r2, r2, #8
	STR      r2, [r4, #0x24]
	LDR      r0, [r4, #0x40]
	LDR      r1, [pc, #0x68]
	ASR      r0, r0, #3
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	STR      r0, [r4, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r0, [r4, #0x1c]
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #0xc]
	ADD      r0, r1, #0
	STR      r1, [sp, #8]
	LDR      r1, [sp, #0xc]
	STR      r0, [sp, #0x10]
	ADD      r0, r1, #0
	STR      r1, [sp, #0x14]
	LDR      r1, [r4, #0x1c]
	ADD      r1, #0xff
	ADD      r1, #0x91
	LDRB     r1, [r1, #0xd]
	LSR      r1, r1, #1
	ADD      r0, r0, r1
	ADD      r0, #1
	STR      r0, [r4, #4]
	ADD      sp, #0x20
	POP      {r4, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x40]
	LSL      r2, r1, #0x1f
	BPL      |sub_0801E12E|
	MOV      r0, #0
	POP      {r3, pc}
|sub_0801E12E|
|unk_0801E12E|
		CMP r1, #0
		DCW     0xD104
		LDR r1, [r0, #0x44]
		CMP r1, #0
		DCW     0xD101
		MOV r0, #0
		DCW     0xE7F7
	INCBIN  baserom.gba_0x1e13c_0x1e13e.extracted
|sub_0801E13E|
|unk_0801E13E|
	INCBIN	baserom.gba_0x1e13e_0x1e142.extracted
	LSL      r0, r0, #0
	PUSH     {r7}
	LSR      r4, r0, #0x20
	LSL      r0, r5, #0xb
	LSR      r2, r6, #1
|loc_0801E14C|
	PUSH     {lr}
	LDR      r1, [r0, #0x30]
	MOV      r0, #0
	SUB      sp, #0x6c
	STR      r0, [sp]
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	MOV      r2, #0
	BL       |inc_0x0158_0x143f2| + 0x3ee0
	ADD      sp, #0x6c
	POP      {pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	LDRB     r1, [r0]
	MOV      r6, #0
	ADD      r4, r2, #0
	LSL      r1, r1, #0x1e
	LSR      r1, r1, #0x1f
	CMP      r1, #0
	SUB      sp, #0x70
	BEQ      |sub_0801E18A|
	LDR      r1, [r0, #0x30]
	STR      r6, [sp, #4]
	STR      r6, [sp, #0x48]
	ADD      r0, sp, #4
	MOV      r2, #0
	BL       |inc_0x0158_0x143f2| + 0x3ee0
	ADD      sp, #0x70
	POP      {r4, r5, r6, pc}
|sub_0801E18A|
|unk_0801E18A|
		MOV r0, #0x14
		DCD     0xFA14F01F
		CMP r0, #0
		BEQ      |loc_0801E19E|
		LDR r1, [pc, #0x48]
		STMIA r0!, {r1, r6}
		SUB r0, #8
		STR r5, [r0, #0xc]
		STR r6, [r0, #8]
|loc_0801E19E|
		ADD r1, r0, #0
		CMP r4, #0
		BEQ      |loc_0801E1AA|
		ADD r6, r4, #0
		ADD r6, #0xff
		ADD r6, #0x8d
|loc_0801E1AA|
		ADD r2, r6, #0
		LDR r6, [pc, #0x34]
		LDR r0, [r6, #4]
		BL       |inc_0x153f2_0x1a3f2| + 0x3f78
		LDR r1, [r4]
		MOV r2, #0x88
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		DCW     0xD0DF
		LDR r0, [r6]
		MOV r2, #0xff
		ADD r0, r0, r5
		LDRB r1, [r0, #2]
		ADD r2, #1
		ADD r1, #1
		CMP r1, r2
		BGE      |loc_0801E1DA|
		STRB r1, [r0, #2]
		DCW     0xE7D5
|loc_0801E1DA|
		MOV r1, #0xff
		STRB r1, [r0, #2]
		DCW     0xE7D2
|sub_0801E1E0|
	LDMIA    r0!, {r2, r3, r4, r5}
	LSR      r4, r0, #0x20
	LSL      r4, r4, #0x1f
	LSR      r2, r6, #1
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
|sub_0801E5D4|
|unk_0801E5D4|
		BL       |inc_0x03d784_0x041118| + 0x2954
		ADD r1, r4, #0
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #0xbf
		LSL r0, r0, #2
		DCD     0xFFE6F01E
		ADD r4, r0, #0
		BEQ      |loc_0801E608|
		MOV r3, #1
		MOV r2, #0xa
		MOV r1, #9
		ADD r0, r4, #0
		BL       |loc_08005460|
		LDR r0, [pc, #0x168]
		STR r0, [r4]
		MOV r0, #0xb
		LSL r0, r0, #6
		ADD r0, r4, r0
		STR r6, [r0, #0x38]
|loc_0801E608|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE7DF
|loc_0801E612|
|unk_0801E612|
		BL       |inc_0x03d784_0x041118| + 0x2912
		ADD r1, r4, #0
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r7, #0
		DCD     0xFFC8F01E
		CMP r0, #0
		BEQ      |loc_0801E642|
		LDR r1, [pc, #0x130]
		STMIA r0!, {r1, r6}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		LDR r1, [pc, #0x124]
		STR r1, [r0]
|loc_0801E642|
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE7C3
|loc_0801E64A|
|unk_0801E64A|
		BL       |inc_0x03d784_0x041118| + 0x2928
		ADD r1, r4, #0
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r7, #0
		DCD     0xFFACF01E
		CMP r0, #0
		BEQ      |loc_0801E67A|
		LDR r1, [pc, #0xf8]
		STMIA r0!, {r1, r6}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		LDR r1, [pc, #0xec]
		STR r1, [r0]
|loc_0801E67A|
		BL       |inc_0x03d784_0x041118| + 0xcc
		DCW     0xE000
|loc_0801E680|
|unk_0801E680|
		B        |loc_0801E686|
		MOV r0, #1
		DCW     0xE7A5
|loc_0801E686|
		MOV r0, #0
		DCW     0xE7A3
|sub_0801E68A|
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0xbc]
	SUB      r4, #0x14
	LDR      r0, [r4]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1f
	BEQ      |loc_0801E6D6|
	BL       |inc_0x03d784_0x041118| + 0x2954
	LDR      r0, [r4, #4]
	MOV      r4, #0
	LDR      r5, [pc, #0xb4]
	ADD      r3, r4, #0
	MOV      r2, #0x40
	ADD      r0, r0, r5
	LDR      r1, [pc, #0xb0]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #0xff
	ADD      r0, #0x1d
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801E6D2|
	LDR      r1, [pc, #0xa0]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r4, [r1, #0xc]
	STR      r4, [r1, #8]
	STR      r4, [r1, #0x10]
	LDR      r1, [pc, #0x9c]
	STR      r1, [r0]
|loc_0801E6D2|
	BL       |inc_0x03d784_0x041118| + 0xcc
|loc_0801E6D6|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	PUSH     {r3, lr}
	LDR      r2, [r1, #0x14]
	LDR      r2, [r2, #0x30]
	CMP      r2, #0
	BNE      |loc_0801E6F6|
	LDR      r2, [r1, #0xc]
	CMP      r2, #1
	BNE      |loc_0801E6F6|
	MOV      r2, #0
	STR      r2, [r1, #0xc]
	STR      r2, [r1, #0x10]
|loc_0801E6F6|
	BL       |inc_0x0158_0x143f2| + 0x667e
	POP      {r3, pc}
|sub_0801E6FC|
|unk_0801E6FC|
		ADD r2, r0, #0
		ADD r0, r1, #0
		MOV r1, #1
		PUSH {r4, lr}
		STRB r1, [r0]
		STRB r1, [r0, #2]
		LDR r1, [pc, #0x64]
		STR r1, [r0, #0x20]
		LDR r1, [r2, #4]
		ADD r1, #0xff
		ADD r1, #1
		LDR r1, [r1, #0xc]
		LDR r3, [r2, #8]
		CMP r1, r3
		BNE      |sub_0801E71E|
		MOV r1, #6
		B        |loc_0801E728|
|sub_0801E71E|
	LDR      r3, [r2, #0x30]
	MOV      r1, #2
	CMP      r3, #0
	BNE      |loc_0801E728|
	MOV      r1, #0x75
|loc_0801E728|
	STRB     r1, [r0, #3]
	LDR      r1, [pc, #0x20]
	SUB      r1, #0x14
	LDR      r1, [r1, #8]
	STR      r1, [r0, #0xc]
	LDR      r3, [r2, #0x20]
	LDR      r4, [r2, #0x24]
	STR      r3, [r0, #4]
	STR      r4, [r0, #8]
	LDR      r1, [r2, #0x1c]
	BL       |inc_0x03d784_0x041118| + 0x356
	POP      {r4, pc}
|sub_0801E742|
	DCW      0x0000
	DCW      0xe3d4,0x083b,0x6a2c,0x0805,0x080c,0x0872,0x0040,0x0600
	DCW      0xe358,0x0804,0x05c4,0x0000,0x9488,0x0831,0x920c,0x0804
	DCW      0xb5ac,0x0804,0x947c,0x0804,0x94d8,0x0804,0xf70d
|sub_0801E772|
	LSR      r3, r0, #0x20
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r0, [pc, #0x258]
	LDR      r1, [sp, #0x24]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r2, [pc, #0x254]
	LDR      r1, [pc, #0x254]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x2250
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x248]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r4, lr}
	SUB      sp, #0x20
	ADD      r4, r0, #0
	MOV      r0, #0x78
	STR      r0, [sp, #0x14]
	MOV      r2, #1
	STR      r2, [sp, #0x1c]
	MOV      r0, #0
	MOV      r1, #0
	STR      r1, [sp, #0x18]
	MVN      r0, r0
	MOV      r2, #0x78
	STR      r2, [sp, #0x10]
	MOV      r1, #0x5f
	STR      r1, [sp, #0xc]
	ADD      r2, r0, #0
	MOV      r1, #1
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r2, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #8]
	MOV      r3, #1
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7758
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0x86
	STR      r0, [sp, #0x14]
	MOV      r2, #1
	STR      r2, [sp, #0x1c]
	MOV      r0, #0
	MOV      r1, #1
	STR      r1, [sp, #0x18]
	MVN      r0, r0
	MOV      r2, #0x78
	STR      r2, [sp, #0x10]
	MOV      r1, #0x4f
	STR      r1, [sp, #0xc]
	ADD      r2, r0, #0
	MOV      r1, #0
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r2, #1
	ADD      r1, r4, #0
	STR      r0, [sp, #8]
	MOV      r3, #0
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7758
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0xe16
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	BL       |inc_0x03d784_0x041118| + 0x2a3e
	MOV      r1, #0
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x71dc
	BL       |inc_0x03d784_0x041118| + 0x29dc
	ADD      sp, #0x20
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x198]
	LDR      r0, [pc, #0x1a4]
	SUB      r3, #0x24
	LDR      r1, [r3, #4]
	MOV      r5, #0xff
	ADD      r0, r1, r0
	ADD      r5, #0x21
	MOV      r4, #1
	CMP      r2, #0
	LDR      r1, [pc, #0x198]
	LDR      r6, [pc, #0x18c]
	BEQ      |sub_0801E8DA|
	CMP      r2, #1
	BNE      |loc_0801E94C|
	MOV      r7, #0
	ADD      r3, r7, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r0, r5, #0
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801E89A|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STMIA    r0!, {r6, r7}
	STR      r7, [r1, #0xc]
	STR      r7, [r1, #8]
	SUB      r0, #8
	ADD      r2, r1, #0
	ADD      r2, #0x10
	STR      r7, [r1, #0x10]
	LDR      r3, [pc, #0x168]
	STRB     r7, [r2, #4]
	STR      r3, [r0]
	STR      r7, [r1, #0x18]
	STRB     r4, [r2, #0xc]
|loc_0801E89A|
	BL       |inc_0x03d784_0x041118| + 0x11c
	CMP      r0, #2
	BNE      |loc_0801E960|
	LDR      r3, [pc, #0x144]
	SUB      r3, #0x24
	LDR      r0, [r3, #0xc]
	BL       |inc_0x03d784_0x041118| + 0x2a16
	MOV      r0, #0xbf
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BEQ      |loc_0801E8D0|
	ADD      r3, r4, #0
	MOV      r2, #0xd
	MOV      r1, #0x5e
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x5308
	LDR      r0, [pc, #0x138]
	STR      r0, [r5]
	MOV      r0, #0xb
	LSL      r0, r0, #6
	ADD      r0, r5, r0
	STR      r7, [r0, #0x38]
|loc_0801E8D0|
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801E8DA|
|unk_0801E8DA|
		MOV r7, #0
		ADD r3, r7, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r5, #0
		DCW     0xF01E
		DCW     0xFE67
		CMP r0, #0
		BEQ      |loc_0801E90E|
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STMIA r0!, {r6, r7}
		STR r7, [r1, #0xc]
		STR r7, [r1, #8]
		SUB r0, #8
		ADD r2, r1, #0
		ADD r2, #0x10
		STR r7, [r1, #0x10]
		LDR r3, [pc, #0xf8]
		STRB r7, [r2, #4]
		STR r3, [r0]
		STR r7, [r1, #0x18]
		MOV r1, #2
		STRB r1, [r2, #0xc]
|loc_0801E90E|
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #2
		DCW     0xD11D
		LDR r3, [pc, #0xd0]
		SUB r3, #0x24
		LDR r0, [r3, #0xc]
		BL       |inc_0x03d784_0x041118| + 0x2a16
		MOV r0, #0xbf
		LSL r0, r0, #2
		DCD     0xFE48F01E
		ADD r5, r0, #0
		BEQ      |loc_0801E944|
		ADD r3, r4, #0
		MOV r2, #0xd
		MOV r1, #0x5e
		ADD r0, r5, #0
		BL       |loc_08005460|
		LDR r0, [pc, #0xc4]
		STR r0, [r5]
		MOV r0, #0xb
		LSL r0, r0, #6
		ADD r0, r5, r0
		STR r4, [r0, #0x38]
|loc_0801E944|
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xcc
		DCW     0xE000
|loc_0801E94C|
|unk_0801E94C|
		B        |loc_0801E96C|
		MOV r0, #1
		DCW     0xE7C2
		MOV r1, #0
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x71dc
		BL       |inc_0x03d784_0x041118| + 0x29dc
		B        |loc_0801E96C|
|loc_0801E960|
|unk_0801E960|
		MOV r1, #0
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x71dc
		BL       |inc_0x03d784_0x041118| + 0x29dc
|loc_0801E96C|
		MOV r0, #0
		DCW     0xE7B3
|sub_0801E970|
	LDR      r0, [pc, #0x74]
	PUSH     {r3, r4, r5, lr}
	SUB      r0, #0x24
	LDR      r1, [r0]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1e
	LSR      r1, r1, #0x1f
	BEQ      |loc_0801E9BC|
	LDR      r0, [r0, #4]
	MOV      r4, #0
	LDR      r5, [pc, #0x6c]
	ADD      r3, r4, #0
	MOV      r2, #0x40
	ADD      r0, r0, r5
	LDR      r1, [pc, #0x68]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	BL       |inc_0x03d784_0x041118| + 0x2a3e
	MOV      r0, #0xff
	ADD      r0, #0x21
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801E9B8|
	LDR      r1, [pc, #0x4c]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r4, [r1, #0xc]
	STR      r4, [r1, #8]
	STR      r4, [r1, #0x10]
	LDR      r1, [pc, #0x4c]
	STR      r1, [r0]
|loc_0801E9B8|
	BL       |inc_0x03d784_0x041118| + 0xcc
|loc_0801E9BC|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	BL       |inc_0x03d784_0x041118| + 0x2a3e
	BL       |inc_0x03d784_0x041118| + 0x2954
	LDR      r0, [pc, #0x1c]
	SUB      r0, #0x24
	LDR      r0, [r0, #0x10]
	BL       |inc_0x0158_0x143f2| + 0x9528
	MOV      r1, #0
	LDR      r0, [pc, #0x30]
	BL       |inc_0x0158_0x143f2| + 0x12430
	POP      {r3, pc}
|sub_0801E9DE|
|unk_0801E9DE|
	INCBIN	baserom.gba_0x1e9de_0x1e9e2.extracted
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
|sub_0801ECBE|
	LSR      r6, r0, #0x20
	LSR      r4, r5, #0x20
	LSR      r2, r6, #1
	DCW      0xf5a5,0x0803
	LSR      r4, r1, #0xf
	LSL      r0, r0, #0
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	STMIA    r0!, {r4, r5, r6, r7}
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x48]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0801ECFA|
	MOV      r0, #1
	POP      {r4, pc}
|loc_0801ECFA|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x669c
	POP      {r4, pc}
|sub_0801ED02|
|unk_0801ED02|
		MOV r0, #0
		BX       lr
|sub_0801ED06|
	SUB      r1, r2, #3
	CMP      r1, #5
	BCS      |loc_0801ED22|
	ADD      r3, pc, #0x4
	LDRB     r3, [r3, r1]
	LSL      r3, r3, #1
	ADD      pc, r3
|loc_0801ED14|
	LSL      r2, r0, #0x18
	LSL      r6, r0, #0x18
	LSL      r7, r0, #0
	MOV      r1, #1
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r1, [r0, #0x2c]
|loc_0801ED22|
	BX       lr
	MOV      r1, #1
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r1, [r0, #0x2c]
	BX       lr
	LSL      r0, r0, #0
	LSR      r0, r6, #0x1f
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x324]
	SUB      sp, #0x14
	LDR      r1, [r0, #0x68]
	LDR      r5, [r0, #0x5c]
	STR      r1, [sp, #0x10]
	MOV      r1, #0xff
	ADD      r1, #0x4d
	LDR      r7, [r0, r1]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x36
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
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r6, [pc, #0x2f8]
	MOV      r1, #0
	LDR      r2, [r6, #4]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x42
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
	MOV      r2, #0x36
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
	LDR      r2, [sp, #0x10]
	STR      r1, [sp, #8]
	STR      r2, [sp]
	ADD      r2, r5, #0
	ADD      r2, #0x10
	MOV      r0, #5
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x42
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r6, #4]
	MOV      r1, #0
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x10
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x1c
	MOV      r0, #0
	STR      r7, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x24
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #4
	STR      r0, [sp, #4]
	MOV      r2, #4
	ADD      r1, r4, #0
	MOV      r3, #0x24
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	STR      r0, [r5, #0x30]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x24
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #5
	STR      r0, [sp, #4]
	MOV      r2, #5
	ADD      r1, r4, #0
	MOV      r3, #0x56
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	STR      r0, [r5, #0x34]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x208]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x55
	LSL      r2, r2, #7
	MOV      r1, #0
	LDR      r0, [pc, #0x200]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #7
	STR      r0, [sp]
	MOV      r0, #6
	STR      r0, [sp, #4]
	MOV      r0, #0x18
	STR      r0, [sp, #8]
	MOV      r0, #0x10
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	LDR      r2, [pc, #0x1ec]
	LDR      r1, [pc, #0x1e4]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0x1e8]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #8]
	LDRH     r1, [r0]
	LSR      r2, r0, #0x12
	ORR      r1, r2
	STRH     r1, [r0]
	MOV      r0, #0
	STR      r0, [r5, #0x28]
	MOV      r1, #1
	STR      r1, [r5, #0x1c]
	STR      r0, [r5, #0x2c]
	ADD      r5, #0x20
	STMIA    r5!, {r0, r1}
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
	BEQ      |loc_0801EEC8|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0801EEC8|
	POP      {r3, pc}
|sub_0801EECA|
|unk_0801EECA|
		PUSH {r4, r5, r6, r7, lr}
		SUB sp, #0x34
		ADD r5, r0, #0
		MOV r2, #0x50
		MOV r1, #0x88
		MOV r0, sp
		MOV r6, sp
		BL       |loc_0803F540|
		ADD r0, r6, #0
		BL       |inc_0x0158_0x143f2| + 0x4f3e
		ADD r4, r5, #0
		ADD r4, #0xff
		ADD r4, #1
		LDR r1, [r4, #0x30]
		LDR r2, [r4, #0x1c]
		MOV r7, #1
		ADD r0, r7, #0
		CMP r2, #0
		BGT      |loc_0801EEF6|
		MOV r0, #0
|loc_0801EEF6|
		STR r0, [r1, #8]
		LDR r1, [r4, #0x14]
		LDR r0, [pc, #0x17c]
		LDR r2, [r4, #0x34]
		LDR r3, [r4, #0x1c]
		CMP r1, r0
		BHS      |loc_0801EF06|
		ADD r0, r1, #0
|loc_0801EF06|
		CMP r3, r0
		BHS      |sub_0801EF0E|
		MOV r0, #1
		DCW     0xE000
|sub_0801EF0E|
	MOV      r0, #0
	ADD      r1, r6, #0
	STR      r0, [r2, #8]
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	MOV      r0, #0
	ADD      r3, sp, #0
	STRB     r0, [r3]
	MOV      r0, #0x10
	STR      r0, [sp, #4]
	STR      r0, [sp, #8]
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r1, r6, #0
	ADD      r0, #0x15
	BL       |sub_0801F810|
	ADD      r3, sp, #0
	STRB     r7, [r3]
	MOV      r0, #0x44
	STR      r0, [sp, #4]
	MOV      r0, #0x2f
	STR      r0, [sp, #8]
	LDR      r2, [r4, #0x1c]
	ADD      r0, r6, #0
	ADD      r1, pc, #0x138
	BL       |inc_0x03d784_0x041118| + 0x512
	LDR      r1, [pc, #0x120]
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
	MOV      r1, #0
	MVN      r1, r1
	CMP      r2, #0
	PUSH     {r3, lr}
	BEQ      |sub_0801EF74|
	CMP      r2, #1
	BNE      |loc_0801EF8A|
	ADD      r0, r1, #0
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r3, pc}
|sub_0801EF74|
|unk_0801EF74|
		ADD r0, #0xff
		ADD r0, #1
		LDR r0, [r0, #0x1c]
		CMP r0, #0
		BLE      |loc_0801EF80|
		ADD r1, r0, #0
|loc_0801EF80|
		ADD r0, r1, #0
		BL       |inc_0x03d784_0x041118| + 0xf2
		MOV r0, #1
		DCW     0xE7F3
|loc_0801EF8A|
|unk_0801EF8A|
		MOV r0, #0
		DCW     0xE7F1
		PUSH {r3, r4, r5, r6, r7, lr}
		LDR r2, [pc, #0xd0]
		ADD r5, r0, #0
		LDR r0, [r2]
		ADD r4, r5, #0
		LDRH r0, [r0, #2]
		ADD r4, #0xff
		ADD r4, #1
		LSL r1, r0, #0x1a
		LSR r1, r1, #0x1f
		MOV r6, #0
		CMP r1, #0
		BNE      |loc_0801EFBC|
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BNE      |loc_0801EFBC|
		MOV r0, #0xa
		STR r0, [r4, #0x28]
		STR r6, [r4, #0x2c]
		MOV r0, #1
		STR r0, [r4, #0x24]
		STR r6, [r4, #0x20]
		B        |loc_0801F056|
|loc_0801EFBC|
		LDR r0, [r4, #0x2c]
		CMP r0, #0
		BNE      |sub_0801F052|
		LDR r0, [r4, #0x20]
		ADD r0, #1
		STR r0, [r4, #0x20]
		CMP r0, #0x32
		BLE      |loc_0801EFF8|
		LDR r7, [r4, #0x24]
		CMP r7, #1
		BNE      |loc_0801EFE4|
		LDR r0, [r4, #0x1c]
		BL       |sub_08053034|
		CMP r0, #0
		BNE      |loc_0801EFE4|
		MOV r0, #0xa
		STR r0, [r4, #0x24]
		STR r6, [r4, #0x20]
		B        |loc_0801EFF8|
|loc_0801EFE4|
		CMP r7, #0xa
		BNE      |loc_0801EFF8|
		LDR r0, [r4, #0x1c]
		BL       |sub_08053058|
		CMP r0, #0
		BNE      |loc_0801EFF8|
		MOV r0, #0x64
		STR r0, [r4, #0x24]
		STR r6, [r4, #0x20]
|loc_0801EFF8|
		LDR r2, [pc, #0x68]
		LDR r0, [r2]
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x1a
		LSR r0, r0, #0x1f
		BEQ      |loc_0801F014|
		LDR r0, [r4, #0x1c]
		LDR r1, [r4, #0x24]
		CMP r0, r1
		BLE      |loc_0801F012|
		SUB r0, r0, r1
		STR r0, [r4, #0x1c]
		B        |loc_0801F014|
|loc_0801F012|
		STR r6, [r4, #0x1c]
|loc_0801F014|
		LDR r0, [r2]
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		DCW     0xD00D
		LDR r0, [r4, #0x1c]
		LDR r1, [r4, #0x24]
		LDR r3, [pc, #0x54]
		ADD r2, r0, r1
		LDR r1, [r4, #0x14]
		ADD r0, r3, #0
		CMP r1, r3
		BHS      |loc_0801F030|
		ADD r0, r1, #0
|loc_0801F030|
		CMP r2, r0
		BHS      |sub_0801F038|
		STR r2, [r4, #0x1c]
		DCW     0xE000
|sub_0801F038|
	STR      r0, [r4, #0x1c]
	LDR      r0, [r4, #0x28]
	CMP      r0, #0
	BEQ      |loc_0801F044|
	SUB      r0, #1
	STR      r0, [r4, #0x28]
|loc_0801F044|
	LDR      r0, [r4, #0x28]
	STR      r0, [r4, #0x2c]
	STR      r6, [r4, #0x10]
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x669c
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801F052|
|unk_0801F052|
; cited by 0x0801ED38 (a pc-relative load targets 0x0801F060)
		SUB r0, #1
		STR r0, [r4, #0x2c]
|loc_0801F056|
		ADD r0, r5, #0
		BL       |loc_080067F4|
		DCW     0xE7F8
	INCBIN  baserom.gba_0x1f05e_0x1f06a.extracted
|sub_0801F06A|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	SUB      r3, r0, #6
	LSL      r0, r0, #0
	STMIA    r3!, {r4, r6}
	LSL      r0, r0, #0
|loc_0801F07C|
	LSL      r0, r4, #0
	LSL      r5, r4, #0
	LSL      r4, r4, #1
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0xc
	ADD      r4, r0, #0
	BL       |loc_08024120|
	MOV      r0, #0xff
	ADD      r3, sp, #0
	STRB     r0, [r3, #9]
	ADD      r4, #0xff
	ADD      r4, #1
	MOV      r0, #0xff
	ADD      r0, #0x35
	LDR      r7, [r4, #0x18]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_0801F0EC|
	LDR      r0, [pc, #0x1ac]
	MOV      r1, #0xff
	STR      r0, [r4]
	MOV      r0, #4
	ADD      r1, #0x15
	STRB     r0, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	MOV      r6, #0
	STR      r6, [r5, #0x1c]
	SUB      r1, r0, #5
	ADD      r0, r4, #0
	STR      r6, [r5, #0x20]
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0x180]
	LDR      r1, [pc, #0x184]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x17c]
	STR      r6, [r0]
	LDR      r0, [pc, #0x180]
	STR      r6, [r1]
	STR      r0, [r4]
	STR      r6, [r5, #0x2c]
	STR      r6, [r1]
	STR      r7, [r5, #0x30]
|loc_0801F0EC|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x29dc
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	BL       |sub_0802426E|
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x164]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0801F118|
	MOV      r0, #2
	POP      {r4, pc}
|loc_0801F118|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x669c
	POP      {r4, pc}
	ADD      r3, r0, #0
	ADD      r3, #0xff
	PUSH     {r4, r5, r6, r7}
	ADD      r3, #1
	LDR      r0, [r3, #0x30]
	MOV      r5, #0x5d
	LSL      r5, r5, #5
	ADD      r0, r0, r5
	LDR      r0, [r0]
	STRB     r0, [r1]
	LDR      r0, [pc, #0x128]
	LDR      r2, [r0]
	MOV      r0, #2
	STRB     r2, [r1, #1]
	LDRB     r4, [r1]
	MOV      r2, #0
	CMP      r4, #0
	BLE      |loc_0801F180|
|loc_0801F144|
	LDR      r4, [r3, #0x30]
	ADD      r6, r4, r5
	LSL      r4, r2, #3
	ADD      r6, r4, r6
	LDR      r7, [r6, #4]
	ADD      r6, r0, #1
	STRB     r7, [r1, r0]
	LDR      r0, [r3, #0x30]
	ADD      r2, #1
	ADD      r0, r0, r5
	ADD      r0, r4, r0
	LDR      r0, [r0, #4]
	LSR      r7, r0, #8
	STRB     r7, [r1, r6]
	ADD      r0, r6, #1
	LDR      r6, [r3, #0x30]
	ADD      r6, r6, r5
	ADD      r6, r4, r6
	LDRB     r7, [r6, #8]
	ADD      r6, r0, #1
	STRB     r7, [r1, r0]
	LDR      r0, [r3, #0x30]
	ADD      r0, r0, r5
	ADD      r0, r4, r0
	LDRB     r4, [r0, #9]
	ADD      r0, r6, #1
	STRB     r4, [r1, r6]
	LDRB     r4, [r1]
	CMP      r4, r2
	BGT      |loc_0801F144|
|loc_0801F180|
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_0801F184|
|unk_0801F184|
		PUSH {r4, r5, r6, r7}
		SUB r2, #3
		CMP r2, #5
		SUB sp, #8
		BHS      |loc_0801F21A|
		ADR      r3, |loc_0801F198|
		LDRB r3, [r3, r2]
		LSL r3, r3, #1
		ADD pc, r3
		LSL r0, r0, #0
|loc_0801F198|
		LSL r1, r0, #0xd
		ADD r4, r8
		LSL r4, r0, #1
		LDRB r4, [r1]
		LDRB r3, [r1, #1]
		MOV r2, #2
		CMP r3, #0
		BEQ      |sub_0801F1AC|
		MOV r3, #1
		DCW     0xE000
|sub_0801F1AC|
	MOV      r3, #0
	ADD      r5, r0, #0
	ADD      r5, #0xff
	ADD      r5, #1
	LDR      r0, [pc, #0xa8]
	STR      r3, [r5, #0x2c]
	LDR      r0, [r0]
	CMP      r0, #0
	BNE      |loc_0801F21A|
	CMP      r4, #0
	BLE      |loc_0801F214|
|loc_0801F1C2|
	ADD      r3, r2, #0
	LDRB     r6, [r1, r3]
	ADD      r2, #1
	ADD      r3, r2, #1
	LDRB     r2, [r1, r2]
	MOV      r7, #0xff
	LSL      r7, r7, #8
	LSL      r2, r2, #8
	AND      r2, r7
	ORR      r2, r6
	STR      r2, [sp]
	LDRB     r6, [r1, r3]
	ADD      r2, r3, #1
	ADD      r3, sp, #0
	STRB     r6, [r3, #4]
	ADD      r3, r2, #0
	LDRB     r6, [r1, r3]
	ADD      r3, sp, #0
	ADD      r2, #1
	STRB     r6, [r3, #5]
	LDR      r3, [r5, #0x30]
	LDR      r6, [pc, #0x7c]
	ADD      r0, #1
	ADD      r3, r3, r6
	LDR      r6, [r3]
	ADD      r7, r6, #1
	LSL      r6, r6, #3
	ADD      r6, r6, r3
	STR      r7, [r3]
	ADD      r3, sp, #0
	LDRH     r3, [r3]
	ADD      r6, #4
	CMP      r0, r4
	STRH     r3, [r6]
	ADD      r3, sp, #0
	LDRH     r3, [r3, #2]
	STRH     r3, [r6, #2]
	ADD      r3, sp, #0
	LDRH     r3, [r3, #4]
	STRH     r3, [r6, #4]
	BLT      |loc_0801F1C2|
|loc_0801F214|
	LDR      r1, [pc, #0x48]
	MOV      r0, #1
	STR      r0, [r1]
|loc_0801F21A|
	ADD      sp, #8
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_0801F220|
|unk_0801F220|
	INCBIN	baserom.gba_0x1f220_0x1f22a.extracted
|sub_0801F22A|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	LDR      r0, [r1, #0x30]
	LDR      r3, [pc, #0x38]
	ADD      r0, r0, r3
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_0801F250|
|loc_0801F23C|
	LDR      r0, [r1, #0x30]
	ADD      r0, r0, r3
	LDR      r2, [r0]
	SUB      r2, #1
	STR      r2, [r0]
	LDR      r0, [r1, #0x30]
	ADD      r0, r0, r3
	LDR      r0, [r0]
	CMP      r0, #0
	BNE      |loc_0801F23C|
|loc_0801F250|
	BX       lr
|sub_0801F252|
	DCW      0x0000
	DCW      0x92ec,0x0804,0xffff
|sub_0801F25A|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	STMIA    r5!, {r3, r5, r6, r7}
	LSR      r4, r0, #0x20
	LSR      r0, r6, #0x1f
	LSL      r0, r0, #0xc
	LSR      r4, r1, #0xf
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	BL       |loc_08024120|
	ADD      r4, #0xff
	ADD      r4, #0x11
	MOV      r0, #0xff
	ADD      r0, #0x31
	LDRB     r7, [r4, #8]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_0801F2D6|
	LDR      r0, [pc, #0x100]
	MOV      r1, #0xff
	STR      r0, [r4]
	MOV      r0, #6
	ADD      r1, #0x15
	STRB     r0, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	MOV      r6, #0
	STR      r6, [r5, #0x1c]
	SUB      r1, r0, #7
	ADD      r0, r4, #0
	STR      r6, [r5, #0x20]
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0xd4]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0xd4]
	STR      r6, [r0]
	LDR      r0, [pc, #0xd4]
	STR      r6, [r0]
	LDR      r0, [pc, #0xd4]
	STR      r0, [r4]
	ADD      r0, r5, #0
	ADD      r0, #0x20
	STRB     r6, [r0, #0xe]
	STRB     r6, [r0, #0xf]
	STRB     r6, [r0, #0xd]
	STRB     r7, [r0, #0xc]
|loc_0801F2D6|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x29dc
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	BL       |sub_0802426E|
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0xb4]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LSL      r1, r0, #0x18
	LSR      r1, r1, #0x18
	BEQ      |loc_0801F308|
	MOV      r0, #2
	CMP      r1, #1
	BEQ      |loc_0801F306|
	MOV      r0, #3
|loc_0801F306|
	POP      {r4, pc}
|loc_0801F308|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x669c
	POP      {r4, pc}
	ADD      r0, #0xff
	ADD      r0, #0x21
	LDRB     r2, [r0, #0xc]
	STRB     r2, [r1]
	LDRB     r0, [r0, #0xd]
	STRB     r0, [r1, #1]
	MOV      r0, #2
	BX       lr
|sub_0801F320|
|unk_0801F320|
		SUB r2, #3
		CMP r2, #5
		BHS      |loc_0801F364|
		ADR      r3, |loc_0801F330|
		LDRB r3, [r3, r2]
		LSL r3, r3, #1
		ADD pc, r3
		LSL r0, r0, #0
|loc_0801F330|
		LSL r3, r0, #0xc
		LSR r2, r3, #0xc
		LSL r3, r2, #0
		ADD r1, r0, #0
		ADD r1, #0xff
		MOV r2, #2
		ADD r1, #0x21
		STRB r2, [r1, #0xd]
		LDRB r2, [r1, #0xc]
		STRB r2, [r1, #0xe]
		B        |loc_0801F364|
	INCBIN  baserom.gba_0x1f346_0x1f364.extracted
|loc_0801F364|
		ADD r0, #0xff
		ADD r0, #0x21
		LDRB r2, [r0, #0xd]
		CMP r2, #0
		DCW     0xD00C
		LDRB r1, [r0, #0xc]
		CMP r1, #0
		DCW     0xD009
		LDRB r3, [r0, #0xe]
		CMP r1, r3
		DCW     0xD106
		CMP r1, #1
		BNE      |sub_0801F384|
		CMP r2, #1
		BNE      |sub_0801F384|
		DCW     0xE000
|sub_0801F384|
	MOV      r1, #2
	STRB     r1, [r0, #0xf]
	BX       lr
|sub_0801F38A|
	DCW      0x0000
	DCW      0x92ec,0x0804,0xffff
|sub_0801F392|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	POP      {r4, r5}
	LSR      r4, r0, #0x20
	LSR      r0, r6, #0x1f
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7}
	LDRB     r6, [r2, #4]
	MOV      r7, #0
	MVN      r7, r7
	CMP      r6, #0
	BNE      |sub_0801F3B6|
	ADD      r0, r7, #0
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_0801F3B6|
|unk_0801F3B6|
		LDR r5, [r1]
		MOV r0, #0
		CMP r5, #0
		BLE      |loc_0801F3D8|
|loc_0801F3BE|
		LSL r3, r0, #3
		ADD r3, r3, r1
		ADD r3, #4
		LDRB r4, [r3, #4]
		CMP r4, r6
		BNE      |loc_0801F3D2|
		LDRB r3, [r3, #5]
		LDRB r4, [r2, #5]
		CMP r3, r4
		DCW     0xD0EF
|loc_0801F3D2|
		ADD r0, #1
		CMP r5, r0
		BGT      |loc_0801F3BE|
|loc_0801F3D8|
		ADD r0, r7, #0
		DCW     0xE7EA
|sub_0801F3DC|
	PUSH     {r4, r5, r6, r7}
	CMP      r3, #0
	BNE      |sub_0801F3E8|
	MOV      r0, #0
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_0801F3E8|
|unk_0801F3E8|
		LDRB r7, [r2, #4]
		CMP r7, #0
		BNE      |loc_0801F3F2|
		MVN r0, r7
		B        |loc_0801F418|
|loc_0801F3F2|
		LDR r6, [r1]
		MOV r0, #0
		CMP r6, #0
		BLE      |loc_0801F414|
|loc_0801F3FA|
		LSL r4, r0, #3
		ADD r4, r4, r1
		ADD r4, #4
		LDRB r5, [r4, #4]
		CMP r5, r7
		BNE      |loc_0801F40E|
		LDRB r4, [r4, #5]
		LDRB r5, [r2, #5]
		CMP r4, r5
		BEQ      |loc_0801F418|
|loc_0801F40E|
		ADD r0, #1
		CMP r6, r0
		BGT      |loc_0801F3FA|
|loc_0801F414|
		MOV r0, #0
		MVN r0, r0
|loc_0801F418|
		CMP r0, #0
		BLT      |loc_0801F42C|
		LSL r0, r0, #3
		ADD r0, r0, r1
		ADD r0, #4
		LDR r1, [r0]
		ADD r1, r1, r3
		STR r1, [r0]
		MOV r0, #1
		DCW     0xE7DB
|loc_0801F42C|
		LDR r0, [r1]
		ADD r4, r0, #0
		SUB r4, #0xff
		SUB r4, #0x4f
		BNE      |loc_0801F43A|
		MOV r0, #0
		DCW     0xE7D4
|loc_0801F43A|
		ADD r4, r0, #1
		LSL r0, r0, #3
		ADD r0, r0, r1
		STR r4, [r1]
		LDR r1, [r2, #4]
		ADD r0, #4
		STR r1, [r0, #4]
		STR r3, [r0]
		MOV r0, #1
		DCW     0xE7CA
|sub_0801F44E|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x360]
	ADD      r6, #0x11
	SUB      sp, #0x10
	MOV      r1, #2
	STRB     r1, [r6, #4]
	LDR      r1, [r0, #0xc]
	ADD      r7, r5, #0
	ADD      r1, #0xe4
	STR      r1, [sp, #0xc]
	LDR      r0, [r1]
	ADD      r7, #0xff
	ADD      r7, #0x2d
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_0801F49E|
|loc_0801F474|
	MOV      r0, #0
	ADD      r3, sp, #0
	STRB     r0, [r3, #4]
	LDR      r1, [sp, #0xc]
	LSL      r0, r4, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	ADD      r1, r7, #0
	STRB     r0, [r3, #5]
	MOV      r3, #1
	ADD      r0, r5, #0
	MOV      r2, sp
	BL       |sub_0801F3DC|
	MOV      r0, #0
	STRB     r0, [r6, #4]
	LDR      r1, [sp, #0xc]
	ADD      r4, #1
	LDR      r0, [r1]
	CMP      r0, r4
	BGT      |loc_0801F474|
|loc_0801F49E|
	MOV      r4, #0
|loc_0801F4A0|
	MOV      r0, #0x34
	LDR      r1, [pc, #0x318]
	MUL      r0, r4
	ADD      r0, r0, r1
	LDRB     r0, [r0]
	LSL      r0, r0, #0x1f
	BNE      |loc_0801F4D6|
	MOV      r0, #1
	ADD      r3, sp, #0
	STRB     r0, [r3, #4]
	LDR      r0, [pc, #0x300]
	STRB     r4, [r3, #5]
	LDR      r0, [r0, #0xc]
	ADD      r1, r7, #0
	ADD      r0, r0, r4
	STR      r0, [sp, #8]
	LDRB     r3, [r0, #2]
	ADD      r0, r5, #0
	MOV      r2, sp
	BL       |sub_0801F3DC|
	LDR      r0, [sp, #8]
	LDRB     r0, [r0, #2]
	CMP      r0, #0
	BEQ      |loc_0801F4D6|
	MOV      r0, #0
	STRB     r0, [r6, #4]
|loc_0801F4D6|
	ADD      r4, #1
	CMP      r4, #0x53
	BLT      |loc_0801F4A0|
	LDR      r0, [pc, #0x2d8]
	LDR      r1, [pc, #0x2e0]
	LDR      r0, [r0, #0xc]
	ADD      r0, r0, r1
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_0801F502|
	MOV      r1, #2
	ADD      r3, sp, #0
	STRB     r1, [r3, #4]
	MOV      r4, #0
	STRB     r4, [r3, #5]
	LDR      r3, [r0]
	ADD      r1, r7, #0
	ADD      r0, r5, #0
	MOV      r2, sp
	BL       |sub_0801F3DC|
	STRB     r4, [r6, #4]
|loc_0801F502|
	ADD      sp, #0x10
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BNE      |loc_0801F51A|
	LDR      r0, [pc, #0x2b4]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0801F51A|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_0801F51A|
	LDR      r0, [pc, #0x2ac]
	MOV      r1, #0
	STMIA    r4!, {r0, r1}
	SUB      r4, #8
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r1, [r0, #0xc]
	STR      r1, [r0, #8]
	LDR      r2, [pc, #0x29c]
	STR      r1, [r0, #0x10]
	STR      r2, [r4]
	MOV      r2, #0xff
	ADD      r2, #0x2d
	STR      r1, [r2, r4]
	MOV      r2, #0x5d
	LSL      r2, r2, #5
	ADD      r2, r4, r2
	STR      r1, [r2]
	LDR      r2, [pc, #0x28c]
	ADD      r2, r4, r2
	STR      r1, [r2]
	STR      r1, [r0, #0x20]
	STR      r1, [r0, #0x24]
	STR      r1, [r0, #0x28]
	ADD      r0, r4, #0
	BL       |sub_0801F44E|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_0801F556|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	MOV      r0, #0x5d
	LSL      r0, r0, #5
	ADD      r7, r5, r0
	LDR      r2, [pc, #0x254]
	LDR      r0, [r7]
	LDR      r2, [r2, #0xc]
	LDR      r1, [pc, #0x258]
	MOV      r4, #0
	ADD      r6, r2, r1
	CMP      r0, #0
	BLE      |loc_0801F5BA|
|loc_0801F570|
	LSL      r0, r4, #3
	ADD      r0, r0, r7
	ADD      r0, #4
	LDRB     r1, [r0, #4]
	CMP      r1, #0
	BEQ      |sub_0801F58C|
	CMP      r1, #1
	BEQ      |loc_0801F598|
	CMP      r1, #2
	BNE      |loc_0801F5B2|
	LDR      r0, [r0]
	LDR      r1, [r6]
	SUB      r0, r1, r0
	B        |sub_0801F5AA|
|sub_0801F58C|
|unk_0801F58C|
		LDRB r1, [r0, #5]
		LDR r0, [pc, #0x228]
		LDR r0, [r0, #0xc]
		BL       |loc_08004468|
		B        |loc_0801F5B2|
|loc_0801F598|
|unk_0801F598|
		LDR r1, [pc, #0x21c]
		LDRB r2, [r0, #5]
		LDR r1, [r1, #0xc]
		LDR r0, [r0]
		ADD r1, r1, r2
		LDRB r2, [r1, #2]
		SUB r0, r2, r0
		STRB r0, [r1, #2]
		B        |loc_0801F5B2|
|sub_0801F5AA|
	STR      r0, [r6]
	LDR      r1, [r6]
	CMP      r1, r0
	BNE      |sub_0801F5AA|
|loc_0801F5B2|
	LDR      r0, [r7]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_0801F570|
|loc_0801F5BA|
	LDR      r0, [pc, #0x214]
	MOV      r4, #0
	ADD      r5, r5, r0
	LDR      r0, [r5]
	CMP      r0, #0
	BLE      |loc_0801F61C|
	LDR      r7, [pc, #0x1f0]
|loc_0801F5C8|
	LSL      r0, r4, #3
	ADD      r0, r0, r5
	ADD      r0, #4
	LDRB     r1, [r0, #4]
	CMP      r1, #0
	BEQ      |sub_0801F5E4|
	CMP      r1, #1
	BEQ      |loc_0801F5EE|
	CMP      r1, #2
	BNE      |loc_0801F614|
	LDR      r0, [r0]
	LDR      r1, [r6]
	ADD      r0, r1, r0
	B        |sub_0801F60C|
|sub_0801F5E4|
|unk_0801F5E4|
		LDRB r1, [r0, #5]
		LDR r0, [r7, #0xc]
		BL       |loc_08004448|
		B        |loc_0801F614|
|loc_0801F5EE|
|unk_0801F5EE|
		LDRB r2, [r0, #5]
		LDR r1, [r7, #0xc]
		LDR r0, [r0]
		ADD r1, r1, r2
		LDRB r2, [r1, #2]
		ADD r0, r2, r0
		MOV r2, #0xff
		ADD r2, #1
		CMP r0, r2
		BGE      |loc_0801F606|
		STRB r0, [r1, #2]
		B        |loc_0801F614|
|loc_0801F606|
		MOV r0, #0xff
		STRB r0, [r1, #2]
		B        |loc_0801F614|
|sub_0801F60C|
	STR      r0, [r6]
	LDR      r1, [r6]
	CMP      r1, r0
	BNE      |sub_0801F60C|
|loc_0801F614|
	LDR      r0, [r5]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_0801F5C8|
|loc_0801F61C|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801F61E|
|unk_0801F61E|
		PUSH {r4, r5, r6, r7, lr}
		LDR r1, [pc, #0x1b0]
		SUB sp, #0x1c
		LDR r5, [r1, #0x5c]
		LDR r6, [r1, #0x68]
		MOV r2, #0
		STR r2, [sp, #0xc]
		MOV r2, #0x84
		ADD r4, r0, #0
		MOV r0, #0
		STR r2, [sp]
		MOV r1, #1
		STR r1, [sp, #8]
		MOV r2, #0
		MOV r3, #0xc
		ADD r1, r4, #0
		STR r0, [sp, #4]
		BL       |loc_08013E64|
		STR r0, [sp, #0x18]
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		LDR r7, [pc, #0x168]
		MOV r1, #0
		LDR r2, [r7, #8]
		STR r1, [sp, #8]
		MOV r0, #5
		STR r2, [sp, #0xc]
		MOV r2, #0x1c
		STR r0, [sp, #4]
		ADD r1, r4, #0
		MOV r3, #0x90
		MOV r0, #0
		STR r5, [sp]
		BL       |loc_08014124|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		ADD r1, r5, #0
		LDR r0, [r7, #8]
		BL       |sub_0803FFE8|
		MOV r2, #0
		STR r2, [sp, #0xc]
		ADD r5, r0, #0
		MOV r1, #1
		ADD r5, #0x1e
		MOV r2, #0x84
		STR r2, [sp]
		ADD r3, r5, #0
		STR r1, [sp, #4]
		STR r1, [sp, #8]
		ADD r1, r4, #0
		MOV r2, #1
		MOV r0, #0
		BL       |loc_08013E64|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		LDR r2, [r7, #8]
		MOV r1, #0
		STR r2, [sp, #0xc]
		ADD r2, r5, #0
		ADD r2, #0x10
		STR r1, [sp, #8]
		MOV r0, #5
		STR r0, [sp, #4]
		ADD r1, r4, #0
		MOV r3, #0x90
		MOV r0, #0
		STR r6, [sp]
		BL       |loc_08014124|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		MOV r0, #0xff
		LDR r1, [pc, #0x10c]
		ADD r0, #0x51
		LDR r0, [r1, r0]
		ADD r1, r6, #0
		STR r0, [sp, #0x14]
		LDR r0, [r7, #8]
		BL       |sub_0803FFE8|
		ADD r3, r0, r5
		MOV r2, #0
		STR r2, [sp, #0xc]
		ADD r5, r3, #0
		ADD r5, #0x14
		MOV r2, #0x84
		MOV r1, #1
		STR r1, [sp, #8]
		STR r2, [sp]
		ADD r3, r5, #0
		MOV r0, #7
		STR r0, [sp, #4]
		ADD r1, r4, #0
		MOV r2, #7
		MOV r0, #0
		BL       |loc_08013E64|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		LDR r2, [r7, #8]
		MOV r1, #0
		STR r2, [sp, #0xc]
		LDR r2, [sp, #0x14]
		STR r1, [sp, #8]
		STR r2, [sp]
		ADD r2, r5, #0
		ADD r2, #0x1a
		MOV r0, #5
		STR r0, [sp, #4]
		ADD r1, r4, #0
		MOV r3, #0x90
		MOV r0, #0
		BL       |loc_08014124|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		MOV r2, #0
		STR r2, [sp, #0xc]
		MOV r2, #0x28
		MOV r1, #1
		MOV r6, #0x6e
		ADD r3, r6, #0
		STR r1, [sp, #8]
		STR r2, [sp]
		MOV r0, #2
		STR r0, [sp, #4]
		MOV r2, #2
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08013E64|
		ADD r5, r4, #0
		ADD r5, #0xff
		ADD r5, #1
		STR r0, [r5, #0x18]
		MOV r2, #0
		STR r2, [sp, #0xc]
		MOV r2, #0x70
		MOV r1, #1
		STR r1, [sp, #8]
		STR r2, [sp]
		MOV r0, #3
		ADD r3, r6, #0
		ADD r1, r4, #0
		STR r0, [sp, #4]
		MOV r2, #3
		MOV r0, #0
		BL       |loc_08013E64|
		STR r0, [r5, #0x1c]
		LDR r1, [r5, #0x18]
		ADD r0, r4, #0
		BL       |loc_0800664E|
		ADD r0, r4, #0
		LDR r1, [r5, #0x1c]
		BL       |loc_0800664E|
		MOV r0, #0xff
		ADD r0, #0x15
		LDRB r0, [r0, r4]
		CMP r0, #2
		DCW     0xD008
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08016208|
		ADD r1, r0, #0
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x1f790_0x1f792.extracted
|sub_0801F792|
|unk_0801F792|
	INCBIN	baserom.gba_0x1f792_0x1f796.extracted
	LDR      r1, [sp, #0x18]
	MOV      r0, #0
	STR      r0, [r1, #8]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x72f4
|unk_0801F7AE|
	INCBIN	baserom.gba_0x1f7ae_0x1f7b0.extracted
|loc_0801F7B0|
|unk_0801F7B0|
	INCBIN	baserom.gba_0x1f7b0_0x1f7b2.extracted
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	LSR      r4, r7, #0x20
	LSR      r2, r6, #1
	BCS      |loc_0801F7B0|
	LSR      r3, r7, #0x20
	LSL      r4, r6, #0x13
	LSL      r0, r0, #0
	LSR      r0, r7, #0xf
	LSL      r0, r0, #0
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      r6, pc, #0x30
	LSR      r4, r0, #0x20
	LSR      r4, r1, #0xf
	LSL      r0, r0, #0
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	MOV      r2, #0xff
	ADD      r2, #0x15
	LDRB     r2, [r2, r0]
	ADD      r0, #0xff
	ADD      r0, #1
	CMP      r2, #0
	BEQ      |sub_0801F7FE|
	CMP      r2, #1
	BNE      |loc_0801F7FA|
	LDR      r0, [r0, #0x28]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #1
	ADD      r0, #0x3c
	STR      r0, [r1, #4]
	MOV      r2, #0x88
	STR      r2, [r1]
|loc_0801F7FA|
	MOV      r0, #1
	BX       lr
|sub_0801F7FE|
|unk_0801F7FE|
		LDR r0, [r0, #0x24]
|loc_0801F800|
|unk_0801F800|
		LSL r3, r0, #3
		SUB r0, r3, r0
		LSL r0, r0, #1
		ADD r0, #0x2e
		STR r0, [r1, #4]
		MOV r2, #0x12
		STR r2, [r1]
		B        |loc_0801F7FA|
|sub_0801F810|
	PUSH     {r3, r4, r5, lr}
	ADD      r3, r0, #0
	LDRB     r2, [r3, #4]
	ADD      r0, r1, #0
	LDR      r1, [pc, #0x31c]
	CMP      r2, #0
	BEQ      |sub_0801F836|
	CMP      r2, #1
	BEQ      |loc_0801F84E|
	CMP      r2, #2
	BNE      |loc_0801F834|
	MOV      r2, #0xff
	ADD      r2, #0x49
	LDR      r2, [r1, r2]
	LDR      r3, [r3]
	ADD      r1, pc, #0x30C
	BL       |inc_0x03d784_0x041118| + 0x512
|loc_0801F834|
	POP      {r3, r4, r5, pc}
|sub_0801F836|
|unk_0801F836|
		LDRB r2, [r3, #5]
		MOV r3, #0x2c
		MUL r2, r3
		LDR r3, [pc, #0x30c]
		ADD r2, r2, r3
		LDRH r2, [r2]
		LSL r2, r2, #2
		LDR r2, [r1, r2]
		MOV r1, #0x54
		BL       |loc_0803DCC4|
		B        |loc_0801F834|
|loc_0801F84E|
|unk_0801F84E|
		LDR r4, [r3]
		LDR r2, [pc, #0x2fc]
		CMP r4, #1
		BNE      |loc_0801F86A|
		LDRB r4, [r3, #5]
		MOV r3, #0x34
		MUL r3, r4
		ADD r2, r3, r2
		LDRH r2, [r2, #2]
		LSL r2, r2, #2
		LDR r1, [r1, r2]
		BL       |loc_0803DADA|
		B        |loc_0801F834|
|loc_0801F86A|
		LDRB r5, [r3, #5]
		MOV r3, #0x34
		MUL r3, r5
		ADD r2, r3, r2
		LDRH r2, [r2, #2]
		LSL r2, r2, #2
		LDR r2, [r1, r2]
		ADR      r1, |loc_0801FB3C|
		ADD r3, r4, #0
		BL       |sub_0803DC96|
		B        |loc_0801F834|
|sub_0801F882|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r5, #0xff
	ADD      r5, #1
	ADD      r4, r1, #0
	LDR      r1, [r5, #0x18]
	MOV      r7, #1
	STR      r7, [r1, #0x10]
	LDR      r1, [r5, #0x1c]
	ADD      r2, r5, #0
	STR      r7, [r1, #0x10]
	MOV      r1, #0xff
	ADD      r1, #0x15
	LDRB     r1, [r1, r0]
	ADD      r2, #0x2c
	STR      r2, [sp]
	MOV      r2, #0x5d
	LSL      r2, r2, #5
	ADD      r6, r0, r2
	CMP      r1, #0
	BEQ      |sub_0801F8CE|
	CMP      r1, #1
	BNE      |loc_0801F902|
	LDR      r1, [r5, #0x18]
	LDR      r2, [r5, #0x28]
	ADD      r0, r7, #0
	CMP      r2, #0
	BNE      |loc_0801F8BC|
	MOV      r0, #0
|loc_0801F8BC|
	STR      r0, [r1, #8]
	LDR      r0, [r5, #0x1c]
	LDR      r1, [r6]
	LDR      r2, [r5, #0x28]
	SUB      r1, #1
	CMP      r1, r2
	BLE      |loc_0801F8FC|
	MOV      r1, #1
	B        |sub_0801F8FE|
|sub_0801F8CE|
|unk_0801F8CE|
		LDR r0, [r5, #0x18]
		LDR r1, [r5, #0x20]
		LDR r2, [r5, #0x24]
		ADD r1, r1, r2
		BEQ      |loc_0801F8DC|
		MOV r1, #1
		B        |loc_0801F8DE|
|loc_0801F8DC|
		MOV r1, #0
|loc_0801F8DE|
		STR r1, [r0, #8]
		LDR r0, [r5, #0x1c]
		LDR r1, [sp]
		LDR r2, [r5, #0x20]
		LDR r1, [r1]
		LDR r3, [r5, #0x24]
		SUB r1, #1
		ADD r2, r2, r3
		CMP r1, r2
		BLE      |loc_0801F8F6|
		MOV r1, #1
		B        |loc_0801F8F8|
|loc_0801F8F6|
		MOV r1, #0
|loc_0801F8F8|
		STR r1, [r0, #8]
		B        |loc_0801F90C|
|loc_0801F8FC|
|unk_0801F8FC|
		MOV r1, #0
|sub_0801F8FE|
	STR      r1, [r0, #8]
	B        |loc_0801F90C|
|loc_0801F902|
	LDR      r0, [r5, #0x18]
	MOV      r1, #0
	STR      r1, [r0, #8]
	LDR      r0, [r5, #0x1c]
	STR      r1, [r0, #8]
|loc_0801F90C|
	MOV      r3, #0x70
	MOV      r2, #0x37
	MOV      r1, #0x75
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x5058
	MOV      r0, #2
	STRB     r0, [r4, #3]
	LDR      r0, [pc, #0x234]
	STRB     r7, [r4, #2]
	STR      r0, [r4, #0x20]
	MOV      r1, #0
	STRB     r1, [r4]
	MOV      r0, #0xe
	STRB     r0, [r4, #1]
	LDR      r0, [pc, #0x22c]
	MOV      r7, #0
	LDR      r0, [r0, #8]
	STR      r0, [r4, #0xc]
|loc_0801F932|
	LDR      r0, [r5, #0x20]
	LDR      r1, [sp]
	ADD      r0, r0, r7
	LDR      r1, [r1]
	CMP      r1, r0
	BLE      |loc_0801F960|
	LSL      r1, r7, #3
	SUB      r1, r1, r7
	LSL      r1, r1, #1
	ADD      r1, #0x31
	STR      r1, [r4, #8]
	MOV      r2, #0x16
	STR      r2, [r4, #4]
	LDR      r1, [sp]
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	ADD      r0, #4
	ADD      r1, r4, #0
	BL       |sub_0801F810|
	ADD      r7, #1
	CMP      r7, #6
	BLT      |loc_0801F932|
|loc_0801F960|
	MOV      r0, #0x31
	STR      r0, [r4, #8]
	MOV      r0, #0xff
	MOV      r7, #0x8c
	LDR      r1, [pc, #0x1cc]
	STR      r7, [r4, #4]
	ADD      r0, #0x41
	LDR      r1, [r1, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r5, #0
|loc_0801F978|
	LDR      r0, [r6]
	CMP      r0, r5
	BLE      |loc_0801F99C|
	LSL      r0, r5, #3
	SUB      r0, r0, r5
	LSL      r0, r0, #1
	ADD      r0, #0x3f
	STR      r0, [r4, #8]
	LSL      r0, r5, #3
	ADD      r0, r0, r6
	ADD      r0, #4
	ADD      r1, r4, #0
	STR      r7, [r4, #4]
	BL       |sub_0801F810|
	ADD      r5, #1
	CMP      r5, #6
	BLT      |loc_0801F978|
|loc_0801F99C|
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
	BL       |sub_0801F882|
	LDR      r1, [pc, #0x194]
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LSL      r0, r2, #3
	ADD      r4, r0, r1
	LDR      r5, [r4, #4]
	ADD      r0, r4, #4
	SUB      r3, r5, r3
	STR      r3, [r4, #4]
	BNE      |loc_0801F9FC|
	LDR      r3, [r1]
	SUB      r3, #1
	STR      r3, [r1]
	SUB      r1, r3, r2
	BEQ      |loc_0801F9FC|
	LSL      r2, r1, #3
	ADD      r1, r4, #0
	ADD      r1, #0xc
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0801F9FC|
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r2, #0
	LSL      r2, r3, #3
	ADD      r4, r2, r5
	LDR      r6, [sp, #0x18]
	STR      r4, [sp]
	ADD      r7, r3, #0
	ADD      r3, r6, #0
	ADD      r4, #4
	ADD      r2, r4, #0
	BL       |sub_0801F3DC|
	CMP      r0, #0
	BEQ      |loc_0801FA3A|
	LDR      r0, [r4]
	SUB      r0, r0, r6
	STR      r0, [r4]
	BNE      |loc_0801FA3A|
	LDR      r0, [r5]
	SUB      r0, #1
	STR      r0, [r5]
	SUB      r0, r0, r7
	BEQ      |loc_0801FA3A|
	LDR      r1, [sp]
	LSL      r2, r0, #3
	ADD      r1, #0xc
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0801FA3A|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r1, [pc, #0x114]
	LDR      r0, [pc, #0x11c]
	LDR      r1, [r1, #4]
	ADD      r4, r5, #0
	ADD      r7, r1, r0
	MOV      r0, #0x5d
	LSL      r0, r0, #5
	ADD      r4, #0xff
	ADD      r4, #1
	ADD      r6, r5, r0
	CMP      r2, #0
	SUB      sp, #0xc
	BEQ      |sub_0801FA88|
	LDR      r1, [pc, #0x108]
	CMP      r2, #2
	BEQ      |loc_0801FB1C|
	CMP      r2, #3
	BNE      |loc_0801FA82|
	LDR      r0, [r6]
	LDR      r2, [r4, #0x28]
	SUB      r0, #1
	CMP      r0, r2
	BLE      |loc_0801FA7E|
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0x28]
	ADD      r0, #1
	STR      r0, [r4, #0x28]
|loc_0801FA7E|
	MOV      r2, #0
	STR      r2, [r4, #0x10]
|loc_0801FA82|
	MOV      r0, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_0801FA88|
|unk_0801FA88|
		LDR r0, [r4, #0x28]
		LSL r0, r0, #3
		ADD r0, r0, r6
		ADD r0, #4
		LDR r1, [r0]
		CMP r1, #1
		BNE      |loc_0801FA9A|
		MOV r0, #1
		B        |loc_0801FAD8|
|loc_0801FA9A|
		STR r0, [sp, #4]
		MOV r0, #0xff
		ADD r0, #0x39
		DCD     0xFD8AF01D
		CMP r0, #0
		BEQ      |loc_0801FAD4|
		LDR r1, [pc, #0xbc]
		MOV r2, #0
		STMIA r0!, {r1, r2}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r2, [r1, #0xc]
		STR r2, [r1, #8]
		STR r2, [r1, #0x10]
		LDR r1, [pc, #0xac]
		STR r1, [r0]
		LDR r3, [sp, #4]
		ADD r1, r0, #0
		LDRH r2, [r3]
		ADD r1, #0xff
		ADD r1, #0x15
		STRH r2, [r1]
		LDRH r2, [r3, #2]
		STRH r2, [r1, #2]
		LDRH r2, [r3, #4]
		STRH r2, [r1, #4]
|loc_0801FAD4|
		BL       |inc_0x03d784_0x041118| + 0x11c
|loc_0801FAD8|
		STR r0, [sp, #8]
		CMP r0, #0
		BLE      |loc_0801FA82|
		LDR r1, [pc, #0x84]
		MOV r3, #0
		MOV r2, #0x40
		ADD r1, #0xc
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r2, [sp, #8]
		ADD r1, r5, #0
		STR r2, [sp]
		ADD r1, #0xff
		ADD r1, #0x2d
		ADD r2, r6, #0
		ADD r0, r5, #0
		LDR r3, [r4, #0x28]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x360e
		LDR r1, [r6]
		LDR r0, [r4, #0x28]
		CMP r1, r0
		BGT      |loc_0801FA82|
		CMP r0, #0
		BEQ      |loc_0801FB12|
		SUB r0, #1
		STR r0, [r4, #0x28]
		B        |loc_0801FA82|
|loc_0801FB12|
		MOV r3, #0
		ADD r5, #0xff
		ADD r5, #0x11
		STRB r3, [r5, #4]
		B        |loc_0801FA82|
|loc_0801FB1C|
|unk_0801FB1C|
		LDR r0, [r4, #0x28]
		CMP r0, #0
		BEQ      |loc_0801FB32|
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0x28]
		SUB r0, #1
		STR r0, [r4, #0x28]
|loc_0801FB32|
		MOV r2, #0
		STR r2, [r4, #0x10]
		B        |loc_0801FA82|
	INCBIN  baserom.gba_0x1fb38_0x1fb3a.extracted
|sub_0801FB3A|
	LSR      r6, r0, #0x20
|loc_0801FB3C|
	LSL      r5, r4, #0
	LSL      r3, r6, #1
	LSL      r0, r4, #0
	LSL      r0, r5, #0
|loc_0801FB44|
	LSL      r5, r4, #0
	LSL      r4, r4, #1
	LSL      r1, r5, #0
	LSL      r0, r0, #0
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	BCS      |loc_0801FB44|
	LSR      r3, r7, #0x20
	DCW      0xf5a5,0x0803
	LSR      r4, r7, #0x20
	LSR      r2, r6, #1
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r4, [sp, #0x1f0]
	LSR      r1, r6, #0x20
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	POP      {r2}
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LSL      r0, r2, #3
	ADD      r4, r0, r1
	LDR      r5, [r4, #4]
	ADD      r0, r4, #4
	SUB      r3, r5, r3
	STR      r3, [r4, #4]
	BNE      |loc_0801FB94|
	LDR      r3, [r1]
	SUB      r3, #1
	STR      r3, [r1]
	SUB      r1, r3, r2
	BEQ      |loc_0801FB94|
	LSL      r2, r1, #3
	ADD      r1, r4, #0
	ADD      r1, #0xc
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0801FB94|
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, r7}
	LDRB     r6, [r2, #4]
	MOV      r7, #0
	MVN      r7, r7
	CMP      r6, #0
	BNE      |sub_0801FBAA|
	ADD      r0, r7, #0
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_0801FBAA|
|unk_0801FBAA|
		LDR r5, [r1]
		MOV r0, #0
		CMP r5, #0
		BLE      |loc_0801FBCC|
|loc_0801FBB2|
		LSL r3, r0, #3
		ADD r3, r3, r1
		ADD r3, #4
		LDRB r4, [r3, #4]
		CMP r4, r6
		BNE      |loc_0801FBC6|
		LDRB r3, [r3, #5]
		LDRB r4, [r2, #5]
		CMP r3, r4
		DCW     0xD0EF
|loc_0801FBC6|
		ADD r0, #1
		CMP r5, r0
		BGT      |loc_0801FBB2|
|loc_0801FBCC|
		ADD r0, r7, #0
		DCW     0xE7EA
|sub_0801FBD0|
	PUSH     {r4, r5, r6, r7}
	CMP      r3, #0
	BNE      |sub_0801FBDC|
	MOV      r0, #0
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_0801FBDC|
|unk_0801FBDC|
		LDRB r7, [r2, #4]
		CMP r7, #0
		BNE      |loc_0801FBE6|
		MVN r0, r7
		B        |loc_0801FC0C|
|loc_0801FBE6|
		LDR r6, [r1]
		MOV r0, #0
		CMP r6, #0
		BLE      |loc_0801FC08|
|loc_0801FBEE|
		LSL r4, r0, #3
		ADD r4, r4, r1
		ADD r4, #4
		LDRB r5, [r4, #4]
		CMP r5, r7
		BNE      |loc_0801FC02|
		LDRB r4, [r4, #5]
		LDRB r5, [r2, #5]
		CMP r4, r5
		BEQ      |loc_0801FC0C|
|loc_0801FC02|
		ADD r0, #1
		CMP r6, r0
		BGT      |loc_0801FBEE|
|loc_0801FC08|
		MOV r0, #0
		MVN r0, r0
|loc_0801FC0C|
		CMP r0, #0
		BLT      |loc_0801FC20|
		LSL r0, r0, #3
		ADD r0, r0, r1
		ADD r0, #4
		LDR r1, [r0]
		ADD r1, r1, r3
		STR r1, [r0]
		MOV r0, #1
		DCW     0xE7DB
|loc_0801FC20|
		LDR r0, [r1]
		CMP r0, #5
		BNE      |loc_0801FC2A|
		MOV r0, #0
		DCW     0xE7D6
|loc_0801FC2A|
		ADD r4, r0, #1
		LSL r0, r0, #3
		ADD r0, r0, r1
		STR r4, [r1]
		LDR r1, [r2, #4]
		ADD r0, #4
		STR r1, [r0, #4]
		STR r3, [r0]
		MOV r0, #1
		DCW     0xE7CC
|sub_0801FC3E|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r2, #0
	LSL      r2, r3, #3
	ADD      r4, r2, r5
	LDR      r6, [sp, #0x18]
	STR      r4, [sp]
	ADD      r7, r3, #0
	ADD      r3, r6, #0
	ADD      r4, #4
	ADD      r2, r4, #0
	BL       |sub_0801FBD0|
	CMP      r0, #0
	BEQ      |loc_0801FC78|
	LDR      r0, [r4]
	SUB      r0, r0, r6
	STR      r0, [r4]
	BNE      |loc_0801FC78|
	LDR      r0, [r5]
	SUB      r0, #1
	STR      r0, [r5]
	SUB      r0, r0, r7
	BEQ      |loc_0801FC78|
	LDR      r1, [sp]
	LSL      r2, r0, #3
	ADD      r1, #0xc
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0801FC78|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #1
	MOV      r7, #0
	ADD      r5, r0, #0
	CMP      r2, #0
	BEQ      |sub_0801FC9E|
	CMP      r2, #2
	BEQ      |loc_0801FD3E|
	CMP      r2, #3
	BNE      |loc_0801FD3C|
	LDR      r0, [r4, #0x24]
	CMP      r0, #5
	BGE      |sub_0801FD54|
	ADD      r0, #1
	STR      r0, [r4, #0x24]
	B        |loc_0801FD5A|
|sub_0801FC9E|
|unk_0801FC9E|
		LDR r0, [r4, #0x20]
		LDR r1, [r4, #0x24]
		ADD r6, r5, #0
		ADD r6, #0xff
		ADD r0, r0, r1
		LSL r0, r0, #3
		ADD r6, #0x2d
		ADD r0, r0, r6
		ADD r0, #4
		LDR r1, [r0]
		CMP r1, #1
		BNE      |loc_0801FCBA|
		MOV r0, #1
		B        |loc_0801FCF6|
|loc_0801FCBA|
		STR r0, [sp]
		MOV r0, #0xff
		ADD r0, #0x39
		DCD     0xFC7AF01D
		CMP r0, #0
		BEQ      |loc_0801FCF2|
		LDR r1, [pc, #0x274]
		STMIA r0!, {r1, r7}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r7, [r1, #0xc]
		STR r7, [r1, #8]
		STR r7, [r1, #0x10]
		LDR r1, [pc, #0x268]
		STR r1, [r0]
		LDR r3, [sp]
		ADD r1, r0, #0
		LDRH r2, [r3]
		ADD r1, #0xff
		ADD r1, #0x15
		STRH r2, [r1]
		LDRH r2, [r3, #2]
		STRH r2, [r1, #2]
		LDRH r2, [r3, #4]
		STRH r2, [r1, #4]
|loc_0801FCF2|
		BL       |inc_0x03d784_0x041118| + 0x11c
|loc_0801FCF6|
		ADD r2, r0, #0
		CMP r0, #0
		BLE      |loc_0801FD3A|
		STR r2, [sp]
		LDR r0, [r4, #0x20]
		LDR r1, [r4, #0x24]
		ADD r2, r6, #0
		ADD r3, r0, r1
		MOV r0, #0x5d
		LSL r0, r0, #5
		ADD r1, r5, r0
		ADD r0, r5, #0
		BL       |sub_0801FC3E|
		LDR r2, [r6]
		LDR r0, [r4, #0x20]
		LDR r1, [r4, #0x24]
		ADD r3, r0, r1
		CMP r2, r3
		BGT      |loc_0801FD3A|
		CMP r1, #0
		BEQ      |loc_0801FD28|
		SUB r1, #1
		STR r1, [r4, #0x24]
		B        |loc_0801FD3A|
|loc_0801FD28|
		CMP r0, #0
		BEQ      |loc_0801FD32|
		SUB r0, #1
		STR r0, [r4, #0x20]
		B        |loc_0801FD3A|
|loc_0801FD32|
		MOV r0, #1
		ADD r5, #0xff
		ADD r5, #0x11
		STRB r0, [r5, #4]
|loc_0801FD3A|
		STR r7, [r4, #0x10]
|loc_0801FD3C|
|unk_0801FD3C|
		DCW     0xE00E
|loc_0801FD3E|
|unk_0801FD3E|
		LDR r0, [r4, #0x24]
		CMP r0, #0
		BEQ      |loc_0801FD4A|
		SUB r0, #1
		STR r0, [r4, #0x24]
		B        |loc_0801FD50|
|loc_0801FD4A|
		LDR r0, [r4, #0x20]
		SUB r0, #1
		STR r0, [r4, #0x20]
|loc_0801FD50|
		STR r7, [r4, #0x10]
		DCW     0xE003
|sub_0801FD54|
	LDR      r0, [r4, #0x20]
	ADD      r0, #1
	STR      r0, [r4, #0x20]
|loc_0801FD5A|
	STR      r7, [r4, #0x10]
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	MOV      r6, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r2, #1
	BEQ      |sub_0801FE2C|
	CMP      r5, #7
	BNE      |loc_0801FE54|
	MOV      r0, #0xff
	ADD      r0, #0x1d
	BL       |GBARam_Malloc|
	LDR      r7, [pc, #0x1c4]
	CMP      r0, #0
	BEQ      |loc_0801FD9A|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r6, [r0, #4]
	STR      r7, [r0]
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	MOV      r2, #0xff
	ADD      r2, #0x15
	STR      r6, [r1, #0x10]
	STRB     r6, [r2, r0]
	LDR      r2, [pc, #0x1b0]
	STR      r2, [r0]
	STR      r4, [r1, #0x18]
|loc_0801FD9A|
	BL       |inc_0x03d784_0x041118| + 0x11c
	CMP      r0, #2
	BNE      |loc_0801FE5E|
	MOV      r0, #0xff
	ADD      r0, #0x21
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801FDC4|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	STR      r6, [r0, #4]
	STR      r7, [r0]
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	LDR      r2, [pc, #0x18c]
	STR      r6, [r1, #0x10]
	STR      r2, [r0]
	STR      r4, [r1, #0x14]
|loc_0801FDC4|
	BL       |inc_0x03d784_0x041118| + 0x11c
	CMP      r0, #2
	BNE      |loc_0801FE5E|
	ADD      r0, r4, #0
	BL       |loc_0801F556|
	MOV      r1, #7
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x71dc
	BL       |inc_0x03d784_0x041118| + 0x29dc
	MOV      r0, #0xff
	ADD      r0, #0x19
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801FE00|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	STR      r6, [r0, #4]
	STR      r7, [r0]
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	LDR      r2, [pc, #0x154]
	STR      r6, [r1, #0x10]
	STR      r2, [r0]
	STR      r6, [r1, #0x14]
|loc_0801FE00|
	BL       |inc_0x03d784_0x041118| + 0x11c
	MOV      r0, #0xff
	ADD      r0, #0x15
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801FE24|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	STR      r6, [r0, #4]
	STR      r7, [r0]
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	STR      r6, [r1, #0x10]
	LDR      r1, [pc, #0x130]
	STR      r1, [r0]
|loc_0801FE24|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801FE2C|
|unk_0801FE2C|
		MOV r0, #0xbf
		LSL r0, r0, #2
		DCD     0xFBC2F01D
		ADD r4, r0, #0
		BEQ      |loc_0801FE50|
		MOV r3, #1
		MOV r2, #0xd
		MOV r1, #0x5e
		ADD r0, r4, #0
		BL       |loc_08005460|
		LDR r0, [pc, #0x110]
		STR r0, [r4]
		MOV r0, #0xb
		LSL r0, r0, #6
		ADD r0, r4, r0
		STR r6, [r0, #0x38]
|loc_0801FE50|
		ADD r0, r4, #0
		DCW     0xE000
|loc_0801FE54|
|unk_0801FE54|
		B        |loc_0801FE68|
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE7E5
|loc_0801FE5E|
|unk_0801FE5E|
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x72f4
		BL       |inc_0x03d784_0x041118| + 0x29dc
|loc_0801FE68|
		MOV r0, #0xff
		ADD r0, #0x15
		LDRB r0, [r0, r4]
		CMP r0, #0
		BEQ      |loc_0801FE82|
		CMP r0, #1
		BNE      |loc_0801FE8E|
		ADD r2, r5, #0
		MOV r1, #0
		ADD r0, r4, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x364a
		DCW     0xE7D3
|loc_0801FE82|
		ADD r2, r5, #0
		MOV r1, #0
		ADD r0, r4, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x3888
		DCW     0xE7CD
|loc_0801FE8E|
		MOV r0, #0
		DCW     0xE7CB
|sub_0801FE92|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #0x11
	LDR      r3, [pc, #0xc4]
	LDRB     r2, [r4, #4]
	LDR      r6, [r3, #4]
	LDR      r1, [pc, #0xb8]
	ADD      r5, r4, #0
	ADD      r7, r6, r1
	MOV      r6, #0
	SUB      r5, #0x10
	CMP      r2, #0
	LDR      r1, [pc, #0xb4]
	BEQ      |sub_0801FEDA|
	CMP      r2, #1
	BNE      |loc_0801FED6|
	ADD      r0, #0xff
	ADD      r0, #0x2d
	LDR      r0, [r0]
	CMP      r0, #0
	BLE      |loc_0801FED6|
	LDR      r0, [r3]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1f
	BEQ      |loc_0801FED6|
	ADD      r3, r6, #0
	MOV      r2, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	STRB     r6, [r4, #4]
	STR      r6, [r5, #0x10]
|loc_0801FED6|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801FEDA|
|unk_0801FEDA|
		MOV r2, #0x5d
		LSL r2, r2, #5
		ADD r0, r0, r2
		LDR r0, [r0]
		CMP r0, #0
		BLE      |loc_0801FED6|
		LDR r0, [r3]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BEQ      |loc_0801FED6|
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #1
		STRB r0, [r4, #4]
		STR r6, [r5, #0x10]
		B        |loc_0801FED6|
|sub_0801FF02|
	LDR      r1, [pc, #0x64]
	PUSH     {r4, lr}
	LDR      r2, [r1]
	CMP      r2, #0
	BEQ      |sub_0801FF3A|
	MOV      r4, #0
	MOV      r0, #0xff
	ADD      r0, #0x15
	STR      r4, [r1]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801FF32|
	LDR      r1, [pc, #0x20]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r4, [r1, #0xc]
	STR      r4, [r1, #8]
	STR      r4, [r1, #0x10]
	LDR      r1, [pc, #0x24]
	STR      r1, [r0]
|loc_0801FF32|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r4, pc}
|sub_0801FF3A|
|unk_0801FF3A|
; cited by 0x0801FCC8 (a pc-relative load targets 0x0801FF40)
		BL       |loc_080067F4|
		POP {r4, pc}
	INCBIN  baserom.gba_0x1ff40_0x1ff4e.extracted
|sub_0801FF4E|
	LSR      r4, r0, #0x20
	LDR      r3, [sp, #0x170]
	LSR      r4, r0, #0x20
	PUSH     {r2, r3, r5, r7, lr}
	LSR      r4, r0, #0x20
	LDR      r3, [sp, #0xb0]
	LSR      r4, r0, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LSR      r4, r7, #0x20
	LSR      r2, r6, #1
	STR      r4, [sp, #0x1f0]
	LSR      r1, r6, #0x20
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	ADD      r0, #0xff
	ADD      r0, #1
	CMP      r2, #0
	BEQ      |loc_0801FF7C|
	CMP      r2, #1
	BEQ      |loc_0801FF7C|
	CMP      r2, #2
	BNE      |loc_0801FF8E|
|loc_0801FF7C|
	LDR      r1, [r0, #0x2c]
	ADD      r1, #1
	STR      r1, [r0, #0x2c]
	CMP      r1, #0x14
	BLE      |loc_0801FF8C|
	LDR      r1, [pc, #0xc]
	MOV      r0, #1
	STR      r0, [r1]
|loc_0801FF8C|
	BX       lr
|loc_0801FF8E|
	MOV      r1, #0
	STR      r1, [r0, #0x2c]
	BX       lr
|sub_0801FF94|
|unk_0801FF94|
	INCBIN	baserom.gba_0x1ff94_0x1ff96.extracted
|sub_0801FF96|
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |inc_0x0158_0x143f2| + 0x55e8
	MOV      r2, #1
	LSL      r2, r2, #0x1a
	LDRH     r0, [r2]
	MOV      r1, #0x41
	LSL      r1, r1, #6
	ORR      r0, r1
	STRH     r0, [r2]
	MOV      r0, #0xb
	LSL      r0, r0, #6
	ADD      r0, r4, r0
	LDR      r0, [r0, #0x38]
	CMP      r0, #0
	BEQ      |loc_0801FFC4|
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7394
	BL       |inc_0x03d784_0x041118| + 0x29dc
|loc_0801FFC4|
	MOV      r0, #5
	ADD      r1, r4, #0
	LSL      r0, r0, #7
	ADD      r0, r4, r0
	ADD      r1, #0xff
	ADD      r1, #0x2d
	ADD      r4, #0xff
	ADD      r4, #1
	LDR      r2, [r4, #0xc]
	LDR      r0, [r0, #0x34]
	LSL      r2, r2, #7
	LDR      r1, [r1, r2]
	STR      r1, [r0, #8]
	POP      {r4, pc}
	PUSH     {r3, lr}
	BL       |inc_0x0158_0x143f2| + 0x570c
	MOV      r2, #1
	LSL      r2, r2, #0x1a
	LDRH     r0, [r2]
	MOV      r1, #0x41
	LSL      r1, r1, #6
	BIC      r0, r1
	STRH     r0, [r2]
	POP      {r3, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r6, r0, #0
	LDR      r3, [pc, #0x28c]
	LDR      r0, [pc, #0x288]
	LDR      r1, [r3, #4]
	ADD      r4, r5, #0
	ADD      r4, #0xff
	ADD      r6, #0xff
	ADD      r0, r1, r0
	ADD      r6, #0x2d
	ADD      r4, #1
	MOV      r7, #0
	CMP      r2, #0
	LDR      r1, [pc, #0x27c]
	BEQ      |sub_08020054|
	CMP      r2, #1
	BEQ      |loc_080200FE|
	MOV      r1, #5
	LSL      r1, r1, #7
	ADD      r5, r5, r1
	LDR      r1, [pc, #0x26c]
	SUB      r1, #0xc
	CMP      r2, #2
	BEQ      |loc_08020100|
	CMP      r2, #3
	BNE      |loc_08020050|
	LDR      r2, [r4, #0xc]
	CMP      r2, #2
	BGE      |loc_08020048|
	ADD      r3, r7, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0xc]
	ADD      r0, #1
	STR      r0, [r4, #0xc]
	LSL      r0, r0, #7
	LDR      r0, [r6, r0]
	LDR      r1, [r5, #0x34]
	STR      r0, [r1, #8]
|loc_08020048|
	MOV      r0, #0
	MVN      r0, r0
	STR      r0, [r4, #0x1c]
	STR      r7, [r4, #0x10]
|loc_08020050|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08020054|
|unk_08020054|
		ADD r3, r7, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0xc]
		LSL r0, r0, #7
		LDR r0, [r6, r0]
		CMP r0, #0
		BEQ      |loc_08020050|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x24]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDR r6, [pc, #0x218]
		LDR r0, [r6, #0x14]
		BL       |inc_0x0158_0x143f2| + 0x9528
		LDR r0, [pc, #0x218]
		LDR r1, [r4, #0xc]
		STR r1, [r0]
		LDR r0, [r6, #0x10]
		BL       |loc_080048A0|
		MOV r0, #0xb
		LSL r0, r0, #6
		ADD r0, r5, r0
		LDR r0, [r0, #0x38]
		CMP r0, #0
		BNE      |loc_0802009C|
		BL       |inc_0x1c3f2_0x2ab4c| + 0x3114
		BL       |inc_0x03d784_0x041118| + 0xcc
		B        |loc_08020050|
|loc_0802009C|
		LDR r0, [r6, #8]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x24]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_080200D8|
		MOV r0, #0xff
		ADD r0, #0x3d
		DCW     0xF01D
		DCW     0xFA81
		CMP r0, #0
		BEQ      |loc_080200D0|
		LDR r1, [pc, #0x1dc]
		STMIA r0!, {r1, r7}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r7, [r1, #0xc]
		STR r7, [r1, #8]
		STR r7, [r1, #0x10]
		LDR r1, [pc, #0x1cc]
		STR r1, [r0]
|loc_080200D0|
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE7BC
|loc_080200D8|
		MOV r0, #0xff
		ADD r0, #0x1d
		DCD     0xFA6CF01D
		CMP r0, #0
		DCW     0xD011
		LDR r1, [pc, #0x1b0]
		MOV r2, #0xff
		STMIA r0!, {r1, r7}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r7, [r1, #0xc]
		STR r7, [r1, #8]
		STR r7, [r1, #0x10]
		ADD r2, #0x15
		STRB r7, [r2, r0]
		DCW     0xE001
|loc_080200FE|
|unk_080200FE|
		DCW     0xE052
|loc_08020100|
|unk_08020100|
		B        |loc_080201D8|
		LDR r2, [pc, #0x19c]
		STR r2, [r0]
		STR r7, [r1, #0x18]
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #2
		BNE      |loc_0802019A|
		LDR r0, [pc, #0x190]
		DCW     0xF01D
		DCW     0xFA51
		ADD r4, r0, #0
		BEQ      |loc_08020190|
		LDR r0, [pc, #0x17c]
		STMIA r4!, {r0, r7}
		SUB r4, #8
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #1
		STR r7, [r0, #0xc]
		STR r7, [r0, #8]
		STR r7, [r0, #0x10]
		LDR r0, [pc, #0x178]
		STR r0, [r4]
		MOV r0, #0xff
		ADD r0, #0x95
		STR r7, [r0, r4]
		LDR r0, [pc, #0x174]
		ADD r0, r4, r0
		STR r7, [r0]
		LDR r0, [pc, #0x170]
		ADD r0, r4, r0
		BL       |loc_08004838|
		LDR r0, [pc, #0x16c]
		LDR r6, [pc, #0x170]
		ADD r5, r4, r0
		ADD r1, r5, #0
		ADD r1, #0x3a
		ADD r0, r5, #0
		MOV r2, #2
		ADD r3, r6, #0
		ADD r0, #0x2e
		BL       |sub_08046FF4|
		LDR r7, [pc, #0x160]
		ADD r1, r5, #0
		ADD r1, #0x4c
		MOV r2, #4
		ADD r0, r5, #0
		ADD r3, r7, #0
		ADD r0, #0x3c
		BL       |sub_08046FF4|
		LDR r0, [pc, #0x150]
		ADD r3, r6, #0
		ADD r5, r4, r0
		ADD r1, r5, #0
		ADD r1, #0x3a
		ADD r0, r5, #0
		MOV r2, #2
		ADD r0, #0x2e
		BL       |sub_08046FF4|
		ADD r1, r5, #0
		ADD r1, #0x4c
		ADD r3, r7, #0
		MOV r2, #4
		ADD r0, r5, #0
		ADD r0, #0x3c
		BL       |sub_08046FF4|
|loc_08020190|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE75B
|loc_0802019A|
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x7394
		BL       |inc_0x03d784_0x041118| + 0x29dc
		B        |loc_08020050|
		ADD r3, r7, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #0xff
		ADD r0, #0x15
		DCW     0xF01D
		DCW     0xFA01
		CMP r0, #0
		BEQ      |loc_080201D0|
		LDR r1, [pc, #0xdc]
		STMIA r0!, {r1, r7}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r7, [r1, #0xc]
		STR r7, [r1, #8]
		STR r7, [r1, #0x10]
		LDR r1, [pc, #0xf4]
		STR r1, [r0]
|loc_080201D0|
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE73C
|loc_080201D8|
		LDR r2, [r4, #0xc]
		CMP r2, #0
		BEQ      |loc_080201F4|
		ADD r3, r7, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0xc]
		SUB r0, #1
		STR r0, [r4, #0xc]
		LSL r0, r0, #7
		LDR r0, [r6, r0]
		LDR r1, [r5, #0x34]
		STR r0, [r1, #8]
|loc_080201F4|
		MOV r0, #0
		MVN r0, r0
		STR r0, [r4, #0x1c]
		STR r7, [r4, #0x10]
		B        |loc_08020050|
|sub_080201FE|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [pc, #0x88]
	ADD      r5, r0, #0
	LDR      r1, [r1]
	LDR      r3, [pc, #0x84]
	LDRH     r1, [r1, #4]
	ADD      r5, #0xff
	ADD      r5, #0x2d
	LDR      r3, [r3, #4]
	LDR      r6, [pc, #0x7c]
	LDR      r2, [pc, #0x74]
	ADD      r4, r5, #0
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x1f
	SUB      r4, #0x2c
	SUB      r6, #0xc
	ADD      r7, r3, r2
	CMP      r1, #0
	BEQ      |loc_0802024E|
	ADD      r1, r6, #0
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0xc]
	LSL      r0, r0, #7
	ADD      r0, r0, r5
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_0802024E|
	BL       |inc_0x0158_0x143f2| + 0x4b34
	CMP      r0, #0
	BEQ      |loc_0802024E|
	MOV      r0, #0
	MVN      r0, r0
	STR      r0, [r4, #0x1c]
	MOV      r3, #0
	STR      r3, [r4, #0x10]
|loc_0802024E|
	LDR      r0, [pc, #0x3c]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1b
	LSR      r0, r0, #0x1f
	BEQ      |loc_08020282|
	ADD      r1, r6, #0
	MOV      r6, #0
	ADD      r3, r6, #0
	MOV      r2, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0xc]
	LSL      r0, r0, #7
	ADD      r0, r0, r5
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_08020282|
	BL       |inc_0x0158_0x143f2| + 0x4b88
	CMP      r0, #0
	BEQ      |loc_08020282|
	MVN      r0, r6
	STR      r0, [r4, #0x1c]
	STR      r6, [r4, #0x10]
|loc_08020282|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LSR      r4, r1, #1
	LSR      r2, r6, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	ADD      r0, r2, r4
	LSL      r0, r0, #0xc
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      r3, pc, #0x2F0
	LSR      r4, r0, #0x20
	PUSH     {r4, r6, lr}
	LSR      r4, r0, #0x20
	LSR      r4, r5, #0x1d
	LSL      r0, r0, #0
	LDMIA    r2!, {r3, r5, r7}
	LSR      r4, r0, #0x20
	LSL      r4, r0, #0x16
	LSL      r0, r0, #0
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
	PUSH     {r2, r3, r5, r7, lr}
	LSR      r4, r0, #0x20
	MOV      r1, #0xb
	LSL      r1, r1, #6
	ADD      r1, r0, r1
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r1, #0x38]
	CMP      r1, #0
	BEQ      |loc_08020328|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x2d
	ADD      r7, r2, #0
	SUB      r7, #0x2c
	LDR      r6, [r7, #0xc]
	LSL      r1, r6, #7
	LDR      r3, [r2, r1]
	CMP      r3, #0
	BEQ      |loc_08020328|
	ADD      r3, r1, r2
	ADD      r2, r3, #0
	LDR      r4, [r3, #0xc]
	ADD      r2, #0xc
	MOV      r1, #0
	CMP      r4, #0
	BLE      |loc_08020328|
	LDR      r5, [r3, #0x7c]
	LSL      r3, r1, #1
	ADD      r3, r3, r1
	LSL      r3, r3, #2
	ADD      r3, r3, r2
	LDR      r3, [r3, #0xc]
	CMP      r3, r5
	BNE      |sub_0802032A|
	LDR      r2, [r7, #0x28]
	LSL      r1, r1, #2
	SUB      r2, r6, r2
	LSL      r2, r2, #5
	ADD      r0, r2, r0
	ADD      r0, r0, r1
	MOV      r1, #5
	LSL      r1, r1, #7
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x38]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08020328|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0802032A|
|unk_0802032A|
		ADD r1, #1
		CMP r4, r1
		DCW     0xDCE4
		B        |loc_08020328|
|sub_08020332|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1f8]
	MOV      r7, #0xff
	LDR      r0, [r0]
	ADD      r7, #0x15
	MOV      r6, #0
	CMP      r0, #0
	LDR      r5, [pc, #0x1f0]
	BEQ      |sub_08020370|
	LDR      r0, [pc, #0x1e8]
	STR      r6, [r0]
	ADD      r0, r7, #0
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08020368|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	STMIA    r0!, {r5, r6}
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	STR      r6, [r1, #0x10]
	LDR      r1, [pc, #0x1d4]
	SUB      r0, #8
	STR      r1, [r0]
|loc_08020368|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08020370|
|unk_08020370|
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0x2d
		BL       |sub_08004DC0|
		CMP r0, #0
		BEQ      |loc_08020386|
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x5754
		DCW     0xE7F3
|loc_08020386|
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x5754
		MOV r0, #0xff
		ADD r0, #0x19
		DCD     0xF912F01D
		CMP r0, #0
		BEQ      |loc_080203B4|
		ADD r1, r0, #0
		ADD r1, #0xff
		STMIA r0!, {r5, r6}
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		LDR r1, [pc, #0x194]
		SUB r0, #8
		STR r1, [r0]
		MOV r1, #2
		MOV r2, #0xff
		ADD r2, #0x15
		STRB r1, [r2, r0]
|loc_080203B4|
		BL       |inc_0x03d784_0x041118| + 0x11c
		ADD r0, r7, #0
		DCW     0xF01D
		DCW     0xF8FD
		CMP r0, #0
		BEQ      |loc_080203D6|
		ADD r1, r0, #0
		ADD r1, #0xff
		STMIA r0!, {r5, r6}
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		LDR r1, [pc, #0x164]
		SUB r0, #8
		STR r1, [r0]
|loc_080203D6|
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #0
		DCW     0xE7C7
|sub_080203DE|
	ADD      r0, #0xff
	ADD      r0, #1
	CMP      r2, #0
	BEQ      |loc_080203EE|
	CMP      r2, #1
	BEQ      |loc_080203EE|
	CMP      r2, #2
	BNE      |loc_08020400|
|loc_080203EE|
	LDR      r1, [r0, #0x2c]
	ADD      r1, #1
	STR      r1, [r0, #0x2c]
	CMP      r1, #0x14
	BLE      |loc_080203FE|
	LDR      r1, [pc, #0x134]
	MOV      r0, #1
	STR      r0, [r1]
|loc_080203FE|
	BX       lr
|loc_08020400|
	MOV      r1, #0
	STR      r1, [r0, #0x2c]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	MOV      r0, #0xff
	LDR      r1, [pc, #0x130]
	ADD      r0, #0x61
	LDR      r3, [r1, r0]
	ADD      r0, #4
	LDR      r5, [r1, r0]
	LDR      r6, [pc, #0x12c]
	SUB      sp, #0x10
	LDR      r2, [r6, #0xc]
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r3, [sp]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x3c
	STR      r0, [sp, #4]
	MOV      r3, #0x14
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r6, #0xc]
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x3c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x22
	MOV      r0, #0
	STR      r5, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0xe0]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #7
	LSL      r2, r2, #0xa
	MOV      r1, #0
	LDR      r0, [pc, #0xd8]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #7
	STR      r0, [sp]
	MOV      r0, #8
	STR      r0, [sp, #4]
	MOV      r0, #0x17
	STR      r0, [sp, #8]
	MOV      r0, #0xf
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	LDR      r2, [pc, #0xc4]
	LDR      r1, [pc, #0xbc]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0xc0]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #8]
	LDRH     r1, [r0]
	LSR      r2, r0, #0x12
	ORR      r1, r2
	STRH     r1, [r0]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
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
	BEQ      |loc_080204CE|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080204CE|
	POP      {r3, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0x38
	MOV      r1, #0x80
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x4f3e
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x58]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #1
	LDR      r0, [r4, #0x14]
	CMP      r0, #0
	BNE      |loc_0802051E|
	LDR      r0, [pc, #0x44]
	LDR      r1, [r0]
	LDR      r0, [pc, #0x2c]
	LDR      r0, [r0, #0x10]
	BL       |inc_0x0158_0x143f2| + 0x47c2
|loc_0802051E|
	LDR      r0, [r4, #0x14]
	ADD      r0, #1
	STR      r0, [r4, #0x14]
	CMP      r0, #0x3c
	BLE      |sub_0802052C|
	MOV      r0, #1
	POP      {r4, pc}
|sub_0802052C|
|unk_0802052C|
; cited by 0x08020336 (a pc-relative load targets 0x08020530)
		MOV r0, #0
		POP {r4, pc}
	INCBIN  baserom.gba_0x20530_0x2054a.extracted
|sub_0802054A|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	SUB      r3, r0, #6
	LSL      r0, r0, #0
	ADD      r0, r2, r4
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, lr}
	LDR      r4, [r1, #4]
	SUB      sp, #0x14
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	LDR      r1, [r1]
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #8]
	ADD      r1, r2, #0
	STR      r2, [sp, #4]
	LDR      r2, [sp, #8]
	STR      r1, [sp, #0xc]
	STR      r2, [sp, #0x10]
	LDR      r2, [r0, #8]
	ADD      r1, r0, #0
	STR      r2, [sp]
	ADD      r2, r0, #0
	ADD      r3, r0, #0
	ADD      r3, #0xc
	ADD      r2, #0x1c
	ADD      r1, #0x14
	ADD      r5, sp, #0xc
	ADD      r0, r5, #0
|loc_08020590|
	BL       |inc_0x153f2_0x1a3f2| + 0x3edc
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r2, [r1, #4]
	LDR      r5, [r0, #0xc]
	ADD      r2, #0xff
	ADD      r2, #0xa1
	LDR      r4, [r2]
	ADD      r4, r4, r5
	STR      r4, [r2]
	LDR      r4, [r2, #4]
	LDR      r3, [r0, #0x10]
	ADD      r3, r4, r3
	STR      r3, [r2, #4]
	LDR      r3, [r0, #0x1c]
	SUB      r3, #1
	STR      r3, [r0, #0x1c]
	BNE      |loc_080205DE|
	LDR      r3, [r0, #0x14]
	LDR      r4, [r0, #0x18]
	LSL      r3, r3, #8
	STMIA    r2!, {r3}
	LSL      r4, r4, #8
	STR      r4, [r2]
	MOV      r2, #1
	STR      r2, [r0, #0x20]
	LDR      r2, [r0]
	LDR      r3, [r2, #0x14]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080205DE|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	LDR      r0, [r1, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x40]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r4, lr}
	LDR      r0, [r1, #4]
	LDR      r1, [r0]
	ADD      r4, r0, #0
	LDR      r2, [r1, #0x40]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r4, pc}
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1, #4]
	SUB      sp, #0x14
	ADD      r5, r0, #0
	ADD      r1, r5, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	LDR      r1, [r1]
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #8]
	ADD      r1, r2, #0
	STR      r2, [sp, #4]
	LDR      r2, [sp, #8]
	STR      r1, [sp, #0xc]
	STR      r2, [sp, #0x10]
	LDR      r2, [r4, #8]
	ADD      r3, r4, #0
	STR      r2, [sp]
	ADD      r2, r4, #0
	ADD      r2, #0x1c
	ADD      r3, #0xc
	ADD      r1, r4, #0
	ADD      r1, #0x14
	ADD      r0, sp, #0xc
	BL       |inc_0x153f2_0x1a3f2| + 0x3edc
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #0xc]
	ADD      r2, r0, #0
	CMP      r0, #0
	BGE      |loc_08020660|
|unk_0802065E|
	INCBIN	baserom.gba_0x2065e_0x20660.extracted
|loc_08020660|
	LDR      r1, [r4, #0x10]
	ADD      r3, r1, #0
	CMP      r1, #0
	BGE      |loc_0802066A|
|unk_08020668|
	INCBIN	baserom.gba_0x20668_0x2066a.extracted
|loc_0802066A|
	CMP      r0, r1
	BLE      |sub_0802067C|
	CMP      r2, #0
	BLT      |sub_08020676|
	MOV      r0, #3
	B        |sub_08020678|
|sub_08020676|
|unk_08020676|
		MOV r0, #2
|sub_08020678|
	STRB     r0, [r5, #0x10]
	B        |loc_0802068C|
|sub_0802067C|
|unk_0802067C|
		CMP r3, #0
		BLT      |sub_08020684|
		MOV r0, #1
		DCW     0xE000
|sub_08020684|
	MOV      r0, #0
	MOV      r1, #1
	SUB      r0, r1, r0
	STRB     r0, [r5, #0x10]
|loc_0802068C|
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	ADD      r4, #0x20
	LDRB     r1, [r4, #4]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x30]
	ADD      r3, r2, r1
	LDRB     r1, [r4, #8]
	LDR      r2, [r4, #0xc]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r4, pc}
	LSL      r0, r0, #0
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r7, [sp, #0x28]
	BNE      |sub_080206D6|
	MOV      r0, #0x54
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080206D6|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_080206D6|
|unk_080206D6|
		LDR r0, [pc, #0x3a0]
		LDR r6, [pc, #0x3a0]
		STR r0, [r4]
		MOV r0, #3
		LSL r0, r0, #8
		STRH r0, [r4, #0xe]
		ADD r1, r0, #0
		LDR r0, [r6, #4]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08020702|
		MOV r1, #3
		LSL r1, r1, #8
		LDR r0, [r6, #4]
		BL       |sub_08011732|
		MOV r1, #3
		LSL r1, r1, #8
		LDR r0, [r6, #4]
		BL       |loc_0801124C|
|loc_08020702|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x378]
		STR r0, [r4]
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x20]
		STR r2, [r4, #0x24]
		LDR r0, [sp, #0xc]
		SUB r5, #8
		STRB r0, [r4, #8]
		LDR r0, [r5, #4]
		MOV r5, #0
		STR r0, [r4, #4]
		LDR r0, [sp, #0x10]
		MOV r1, #8
		STR r0, [r4, #0x50]
		STR r5, [r4, #0x18]
		STRB r5, [r4, #0x11]
		STRB r5, [r4, #0x10]
		STR r1, [r4, #0x38]
		STR r7, [r4, #0x40]
		LDRB r0, [r0, #0x10]
		LDR r2, [pc, #0x358]
		LSR r0, r0, #1
		LDRB r0, [r7, r0]
		STRB r0, [r4, #0x12]
		LDR r1, [r7, #8]
		LDR r0, [pc, #0x34c]
		STR r1, [r4, #0x4c]
		STR r1, [r4, #0x48]
		STR r1, [r4, #0x44]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x14]
		MVN r0, r5
		STR r0, [r4, #0x1c]
		LDRH r0, [r4, #0xc]
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r2
		MOV r2, #0x40
		BL       |sub_08049138|
		ADD r3, r5, #0
		LDR r5, [pc, #0x338]
		LDR r0, [r6]
		MOV r2, #0x40
		ADD r0, r0, r5
		LDR r1, [pc, #0x32c]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		DCW     0xE7B4
		PUSH {r0, r1, r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r0, [pc, #0x310]
		SUB sp, #4
		STR r0, [r4]
		LDR r7, [pc, #0x308]
		LDRB r0, [r4, #0x10]
		LDR r2, [r7]
		LDR r6, [pc, #0x310]
		LDR r1, [pc, #0x314]
		SUB r6, #0x24
		ADD r5, r2, r1
		CMP r0, #1
		DCW     0xD30E
		ADD r1, r6, #0
		ADD r1, #0xff
		ADD r1, #0x81
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xb7e
		ADD r1, r6, #0
		ADD r1, #0xff
		ADD r1, #0x8d
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r5, #0
	INCBIN  baserom.gba_0x2079c_0x2079e.extracted
|sub_0802079E|
|unk_0802079E|
	INCBIN	baserom.gba_0x2079e_0x207a2.extracted
	ADD      r1, r6, #0
	ADD      r1, #0x24
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0xb7e
	LDR      r0, [pc, #0x2c8]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x2e0]
	CMP      r1, r0
	BEQ      |loc_080207BE|
	LDR      r0, [r7, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080207BE|
	LDR      r0, [pc, #0x2d8]
	STR      r0, [r4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_080207CE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080207CE|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, lr}
	STR      r1, [r0, #0x3c]
	LDR      r3, [r2]
	LDR      r2, [r2, #4]
	LDR      r5, [pc, #0x2b0]
	STR      r2, [r0, #0x24]
	STR      r3, [r0, #0x20]
	LDR      r1, [r0, #0x40]
	SUB      r5, #0x24
	LDR      r2, [r1, #0xc]
	LDR      r1, [r0, #0x3c]
	LSL      r3, r1, #1
	ADD      r3, r3, r1
	LSL      r3, r3, #6
	ADD      r2, r2, r3
	STR      r2, [r0, #0x4c]
	STR      r2, [r0, #0x48]
	LDR      r2, [pc, #0x2a4]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r2, [r1]
	LDR      r1, [r1, #4]
	STR      r1, [r0, #0x34]
	STR      r2, [r0, #0x30]
	MOV      r1, #1
	STRB     r1, [r0, #0x10]
	LDR      r0, [pc, #0x274]
	LDR      r2, [pc, #0x284]
	LDR      r0, [r0]
	ADD      r1, r5, #0
	ADD      r1, #0x24
	ADD      r0, r0, r2
	ADD      r4, r0, #0
	BL       |inc_0x03d784_0x041118| + 0xb7e
	ADD      r1, r5, #0
	ADD      r1, #0xff
	ADD      r1, #0x81
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	LDRB     r1, [r0, #0x10]
	CMP      r1, #0
	BEQ      |sub_08020840|
	CMP      r1, #1
	BNE      |loc_0802083E|
	MOV      r1, #2
	STRB     r1, [r0, #0x10]
	SUB      r1, #3
	STR      r1, [r0, #0x1c]
|loc_0802083E|
	POP      {r3, pc}
|sub_08020840|
|unk_08020840|
		ADD r1, r0, #0
		LDR r0, [pc, #0x238]
		LDR r0, [r0, #4]
		BL       |loc_08011944|
		B        |loc_0802083E|
|sub_0802084C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r2, [r4, #0x10]
	ADD      r0, r1, #0
	SUB      sp, #0x54
	LDR      r5, [pc, #0x230]
	CMP      r2, #0
	BEQ      |sub_08020896|
	CMP      r2, #1
	BEQ      |loc_080208CE|
	CMP      r2, #2
	BNE      |loc_08020948|
	LDR      r0, [r4, #0x30]
	LDR      r1, [r4, #0x34]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	STR      r1, [sp, #0x4c]
	STR      r0, [sp, #0x48]
	LDR      r2, [r4, #0x20]
	ADD      r0, r2, r0
	STR      r0, [r4, #0x20]
	LDR      r0, [r4, #0x24]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x38]
	SUB      r0, #3
	STR      r0, [r4, #0x38]
	BPL      |loc_08020948|
	LDR      r0, [pc, #0x1f0]
	ADD      r1, r4, #0
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x54
	POP      {r4, r5, r6, r7, pc}
|sub_08020896|
|unk_08020896|
		LDR r1, [r4, #0x18]
		ADD r1, #1
		STR r1, [r4, #0x18]
		CMP r1, #4
		DCW     0xDBF8
		LSL r1, r1, #0x1d
		LSR r1, r1, #0x1f
		LSL r3, r1, #1
		ADD r1, r3, r1
		LDR r0, [r4, #0x4c]
		LSL r1, r1, #2
		ADD r1, r0, r1
		ADD r1, #0xc
		STR r1, [r4, #0x48]
		LDR r0, [r4, #0x44]
		CMP r1, r0
		DCW     0xD0EC
		STR r1, [r4, #0x44]
		LDRB r2, [r1, #2]
		LDRB r0, [r1, #3]
		MUL r2, r0
		LDRH r0, [r4, #0xc]
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r5
		BL       |sub_08049138|
		DCW     0xE7E1
|loc_080208CE|
|unk_080208CE|
		LDR r1, [pc, #0x1ac]
		LDR r1, [r1, #8]
		ADD r6, r1, #0
		ADD r6, #0x18
		ADD r1, #0x80
		CMP r0, #0
		LDR r0, [r4, #0x38]
		LDR r2, [r4, #0x30]
		DCW     0xD072
		LDR r3, [r4, #0x34]
		MUL r2, r0
		MUL r3, r0
		ADD r0, r2, #0
		STR r2, [sp, #0x40]
		ADD r2, r3, #0
		STR r3, [sp, #0x44]
		LDR r3, [r4, #0x20]
		ADD r0, r3, r0
		LDR r3, [r4, #0x24]
		STR r0, [sp, #0x40]
		ADD r2, r3, r2
		STR r2, [sp, #0x44]
		STR r2, [sp, #0x4c]
		STR r0, [sp, #0x48]
		LDR r0, [r4, #0x50]
		ADD r3, sp, #0x20
		STR r0, [sp, #0x34]
		LDR r0, [r4, #0x3c]
		ADD r2, sp, #0x14
		STRB r0, [r3, #8]
		LDR r0, [r4, #0x40]
		LDR r3, [pc, #0x190]
		LDRB r0, [r0, #6]
		ADD r7, r2, #4
		LSL r0, r0, #3
		ADD r0, r0, r3
		STR r0, [sp, #0x30]
		LDR r0, [r4, #0x40]
		ADD r3, sp, #0
		LDRH r0, [r0, #2]
		STR r0, [sp, #0x2c]
		LDR r0, [r4, #0x50]
		ADD r0, #0xff
		ADD r0, #0xc1
		LDR r0, [r0, #0x10]
		STRB r0, [r3, #0x14]
		LDR r3, [sp, #0x48]
		LDR r0, [sp, #0x48]
		SUB r3, #8
		MOV ip, r3
		LDR r3, [sp, #0x4c]
		LDR r2, [sp, #0x4c]
		SUB r3, #8
		MOV lr, r3
		MOV r3, ip
		STR r3, [sp, #0x18]
		ADD r0, #8
		ADD r2, #8
		MOV r3, lr
		STR r4, [sp, #0x44]
		DCW     0xE000
|loc_08020948|
|unk_08020948|
; cited by 0x080206D6 (a pc-relative load targets 0x08020A78)
		B        |loc_08020B62|
		STR r0, [sp, #0x20]
		STR r3, [sp, #0x1c]
		STR r2, [sp, #0x24]
		LDR r1, [r1, #0x2c]
		ADD r0, r7, #0
		BL       |loc_08009324|
		CMP r0, #0
		BEQ      |loc_08020A36|
		LDR r0, [pc, #0x11c]
		ADD r2, sp, #0x14
		MOV r1, #0
		LDR r0, [r0, #4]
		BL       |loc_08011C0C|
		CMP r0, #0
		BEQ      |loc_08020A38|
		LDR r0, [r4, #0x30]
		LDR r1, [r4, #0x34]
		LSL r0, r0, #2
		LSL r1, r1, #2
		STR r1, [sp, #8]
		LDR r2, [sp, #0x48]
		STR r0, [sp, #4]
		ADD r0, r2, r0
		LDR r2, [sp, #0x4c]
		STR r0, [sp, #0xc]
		ADD r1, r2, r1
		STR r1, [sp, #8]
		STR r1, [sp, #0x10]
		STR r0, [sp, #4]
		LDRB r0, [r4, #0x11]
		CMP r0, #0
		BNE      |loc_08020996|
		LDR r0, [pc, #0xec]
		LDR r0, [r0, #4]
		BL       |loc_080116FC|
|loc_08020996|
		LDR r0, [pc, #0xec]
		LDR r6, [r0, #4]
		LDR r0, [r4, #0x14]
		SUB r0, r6, r0
		CMP r0, #0
		BLE      |loc_08020A26|
		MOV r0, #5
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, r6, r0
		ADD r0, #3
		STR r0, [r4, #0x14]
		LDR r7, [pc, #0xcc]
		MOV r0, #2
		LDR r6, [r7]
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0xcc]
		LSL r0, r0, #2
		SUB r1, #0x24
		B        |loc_080209C8|
		B        |loc_08020AFC|
|loc_080209C8|
		ADD r1, r0, r1
		LDR r0, [pc, #0xc4]
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r6, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r7, #4]
		BL       |loc_080116FC|
		MOV r6, #1
		LSL r6, r6, #0xa
		CMP r0, r6
		BLE      |loc_08020A26|
		MOV r0, #0x20
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [sp, #0xc]
		ADD r0, r0, r1
		SUB r0, #0x10
		STR r0, [sp, #0xc]
		MOV r0, #0x20
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [sp, #0x10]
		ADD r0, r0, r1
		SUB r0, #0x10
		STR r0, [sp, #0x10]
		LSL r0, r6, #4
		BL       |inc_0x03d784_0x041118| + 0x2348
		LSL r1, r6, #2
		ADD r0, r0, r1
		MOV r2, #0x38
		STR r2, [sp, #8]
		STR r0, [sp]
		MOV r3, #4
		MOV r0, #0
		LDR r2, [pc, #0x8c]
		ADD r1, sp, #0xc
		STR r6, [sp, #4]
		BL       |loc_0802A81C|
		ADD r1, r0, #0
		LDR r0, [r7, #4]
		BL       |sub_0801191A|
|loc_08020A26|
		LDRB r0, [r4, #0x11]
		CMP r0, #0
		BNE      |loc_08020A64|
		MOV r0, #1
		STRB r0, [r4, #0x11]
		NEG r0, r0
		STR r0, [r4, #0x1c]
		B        |loc_08020A64|
|loc_08020A36|
		B        |loc_08020A56|
|loc_08020A38|
		B        |loc_08020A3A|
|loc_08020A3A|
		LDR r0, [pc, #0x6c]
		LDR r0, [r0]
		CMP r0, #0
		BNE      |loc_08020A4E|
		ADD r0, r6, #0
		ADD r1, r7, #0
		BL       |inc_0x049120_0x055620| + 0xa1a0
		CMP r0, #0
		BEQ      |loc_08020A64|
|loc_08020A4E|
		LDR r0, [r4, #0x38]
		ADD r0, #3
		STR r0, [r4, #0x38]
		B        |loc_08020A64|
|loc_08020A56|
		LDRB r0, [r4, #0x11]
		CMP r0, #0
		BNE      |loc_08020A64|
		MOV r0, #1
		STRB r0, [r4, #0x11]
		NEG r0, r0
		STR r0, [r4, #0x1c]
|loc_08020A64|
		LDR r0, [sp, #0x48]
		LDR r2, [r4, #0x20]
		ADD r1, r4, #0
		ADD r1, #0x20
		CMP r0, r2
		ADD r6, sp, #0x48
		BGE      |loc_08020AAC|
		ADD r0, r6, #0
		B        |loc_08020AAE|
	INCBIN  baserom.gba_0x20a76_0x20a7c.extracted
		DCD     0x08725048
		DCD     0x0804AEF8
		DCD     0x03000F90
		DCD     0x06010000
		DCD     0x083192CC
		DCD     0x000005C4
	INCBIN  baserom.gba_0x20a94_0x20aa4.extracted
		DCD     0x08712FDC
		DCD     0x03002C04
|loc_08020AAC|
		ADD r0, r1, #0
|loc_08020AAE|
		LDR r0, [r0]
		LDR r3, [sp, #0x4c]
		SUB r0, #6
		STR r0, [sp, #0x18]
		ADD r0, r4, #0
		LDR r7, [r4, #0x24]
		ADD r0, #0x24
		ADD r2, r6, #4
		CMP r3, r7
		BGE      |loc_08020AC6|
		ADD r3, r2, #0
		B        |loc_08020AC8|
|loc_08020AC6|
		ADD r3, r0, #0
|loc_08020AC8|
		LDR r3, [r3]
		SUB r3, #6
		STR r3, [sp, #0x1c]
		LDR r3, [sp, #0x48]
		LDR r7, [r1]
		CMP r3, r7
		BLE      |loc_08020AD8|
		ADD r1, r6, #0
|loc_08020AD8|
		LDR r1, [r1]
		ADD r1, #6
		STR r1, [sp, #0x20]
		LDR r1, [sp, #0x4c]
		LDR r3, [r0]
		CMP r1, r3
		BLE      |loc_08020AE8|
		ADD r0, r2, #0
|loc_08020AE8|
		LDR r0, [r0]
		ADD r2, sp, #0x14
		ADD r0, #6
		STR r0, [sp, #0x24]
		LDR r0, [pc, #0x2ac]
		MOV r1, #0
		LDR r0, [r0, #4]
		BL       |loc_08011C0C|
		B        |loc_08020B62|
|loc_08020AFC|
		LDR r3, [r4, #0x34]
		MUL r2, r0
		MUL r3, r0
		ADD r0, r2, #0
		STR r2, [sp, #0x48]
		ADD r2, r3, #0
		STR r3, [sp, #0x4c]
		LDR r3, [r4, #0x20]
		ADD r0, r3, r0
		LDR r3, [r4, #0x24]
		STR r0, [sp, #0x48]
		ADD r2, r3, r2
		ADD r7, r2, #0
		ADD r3, r0, #0
		SUB r7, #8
		STR r2, [sp, #0x4c]
		ADD r2, #8
		STR r7, [sp, #0x44]
		SUB r3, #8
		ADD r0, #8
		STR r0, [sp, #0x48]
		STR r3, [sp, #0x40]
		ADD r7, sp, #0x40
		STR r2, [sp, #0x4c]
		LDR r1, [r1, #0x2c]
		ADD r0, r7, #0
		BL       |loc_08009324|
		CMP r0, #0
		BEQ      |loc_08020B54|
		LDR r0, [pc, #0x268]
		LDR r0, [r0]
		CMP r0, #0
		BNE      |loc_08020B4C|
		ADD r0, r6, #0
		ADD r1, r7, #0
		BL       |inc_0x049120_0x055620| + 0xa1a0
		CMP r0, #0
		BEQ      |loc_08020B62|
|loc_08020B4C|
		LDR r0, [r4, #0x38]
		ADD r0, #3
		STR r0, [r4, #0x38]
		B        |loc_08020B62|
|loc_08020B54|
		LDRB r0, [r4, #0x11]
		CMP r0, #0
		BNE      |loc_08020B62|
		MOV r0, #1
		STRB r0, [r4, #0x11]
		NEG r0, r0
		STR r0, [r4, #0x1c]
|loc_08020B62|
		LDR r0, [r4, #0x18]
		ADD r0, #1
		ASR r6, r0, #2
		STR r0, [r4, #0x18]
		LDR r0, [r4, #0x1c]
		CMP r0, r6
		BNE      |loc_08020B72|
|loc_08020B70|
		DCW     0xE68F
|loc_08020B72|
		STR r6, [r4, #0x1c]
		LDR r0, [r4, #0x40]
		LDRB r0, [r0, #5]
		CMP r0, #0
		BEQ      |loc_08020BD0|
		CMP r0, #1
		BEQ      |loc_08020BD0|
		CMP r0, #2
		BNE      |loc_08020C26|
		LSL r7, r6, #0x1e
		LSR r7, r7, #0x1e
		CMP r7, #3
		BNE      |loc_08020B8E|
		MOV r7, #1
|loc_08020B8E|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x4c]
		LSL r2, r7, #6
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r1, r1, r2
		STR r2, [sp, #0x50]
		MOV r2, #0x40
		BL       |sub_08049138|
		LDRB r0, [r4, #0x11]
		CMP r0, #0
		LDRH r0, [r4, #0xc]
		BEQ      |loc_08020C28|
		LSL r0, r0, #5
		MOV r2, #1
		LSL r2, r2, #9
		ADD r0, r0, r5
		ADD r0, r0, r2
		LSL r2, r7, #0x1f
		LSR r2, r2, #0x1f
		LSL r3, r2, #1
		ADD r2, r3, r2
		LDR r1, [r4, #0x4c]
		LSL r2, r2, #2
		ADD r1, r1, r2
		ADD r1, #0x80
		LDR r1, [r1]
		MOV r2, #0x80
		BL       |sub_08049138|
		B        |loc_08020C26|
|loc_08020BD0|
		LDRB r0, [r4, #0x10]
		LSL r7, r6, #0x1f
		LSR r7, r7, #0x1f
		MOV r3, #0
		CMP r0, #1
		BEQ      |loc_08020BDE|
		MOV r3, #0xd
|loc_08020BDE|
		ADD r0, r7, r3
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [r4, #0x4c]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDRB r2, [r1, #2]
		LDRB r0, [r1, #3]
		MUL r2, r0
		LDRH r0, [r4, #0xc]
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r5
		BL       |sub_08049138|
		LDRB r1, [r4, #0x11]
		MOV r0, #0xa
		CMP r1, #0
		BNE      |loc_08020C06|
		MOV r0, #7
|loc_08020C06|
		ADD r0, r7, r0
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [r4, #0x4c]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDRH r0, [r4, #0xc]
		MOV r2, #1
		LSL r2, r2, #9
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, r0, r2
		LSR r2, r2, #1
		LDR r1, [r1, #8]
		BL       |sub_08049138|
|loc_08020C26|
		B        |loc_08020C40|
|loc_08020C28|
		LSL r0, r0, #5
		MOV r2, #1
		LDR r1, [r4, #0x4c]
		LSL r2, r2, #9
		ADD r0, r0, r5
		ADD r0, r0, r2
		LDR r1, [r1, #0x5c]
		LDR r2, [sp, #0x50]
		ADD r1, r1, r2
		MOV r2, #0x40
		BL       |sub_08049138|
|loc_08020C40|
		LDR r0, [r4, #0x40]
		LDRB r0, [r0, #5]
		CMP r0, #0
		BEQ      |loc_08020C76|
		CMP r0, #1
		BEQ      |loc_08020C9A|
		CMP r0, #2
		BNE      |loc_08020B70|
		LSL r1, r6, #0x1e
		LSR r1, r1, #0x1e
		CMP r1, #3
		BNE      |loc_08020C5A|
		MOV r1, #1
|loc_08020C5A|
		LDRH r0, [r4, #0xc]
		LDR r2, [r4, #0x4c]
		LSL r1, r1, #8
		LDR r2, [r2, #0x44]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, #0xff
		ADD r1, r2, r1
		MOV r2, #0xff
		ADD r0, #1
		ADD r2, #1
		BL       |sub_08049138|
		DCW     0xE60D
|loc_08020C76|
		LSL r2, r6, #0x1f
		LSR r2, r2, #0x1f
		LDRH r0, [r4, #0xc]
		LSL r3, r2, #1
		ADD r2, r3, r2
		LDR r1, [r4, #0x4c]
		LSL r2, r2, #2
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r1, r1, r2
		ADD r0, #0xff
		ADD r0, #1
		MOV r2, #0xff
		ADD r2, #1
		LDR r1, [r1, #0x44]
		BL       |sub_08049138|
		DCW     0xE5FB
|loc_08020C9A|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x4c]
		LSL r2, r6, #0x1e
		LDR r1, [r1, #0x44]
		LSL r0, r0, #5
		ADD r0, r0, r5
		LSR r2, r2, #0x18
		ADD r1, r1, r2
		ADD r0, #0xff
		ADD r0, #1
		MOV r2, #0xff
		ADD r2, #1
		BL       |sub_08049138|
		DCW     0xE5EC
|sub_08020CB8|
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4}
	LDR      r1, [pc, #0xd4]
	LDR      r3, [r0, #0x20]
	LDR      r1, [r1, #8]
	ADD      r2, r0, #0
	ADD      r1, #0x18
	LDR      r4, [r1]
	LDR      r0, [r0, #0x24]
	LDR      r1, [r1, #4]
	SUB      r3, r3, r4
	ADD      r2, #0x28
	SUB      sp, #8
	SUB      r0, r0, r1
	STR      r0, [sp, #4]
	LDR      r1, [sp, #4]
	STR      r3, [sp]
	STR      r1, [r2, #4]
	STR      r3, [r2]
	ADD      sp, #8
	POP      {r4}
	MOV      r0, #1
	BX       lr
|loc_08020CF4|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	LSL      r3, r1, #1
	SUB      sp, #0x14
	ADD      r6, r0, #0
	LDR      r0, [sp, #0x28]
	ADD      r1, r3, r1
	ADD      r4, r2, #0
	LDR      r2, [r6, #0x4c]
	LSL      r1, r1, #2
	ADD      r5, r2, r1
	MOV      r3, #0
	LDRSB    r2, [r5, r3]
	LDR      r1, [r6, #0x28]
	MOV      r3, #1
	ADD      r1, r1, r2
	LDR      r2, [r0]
	ADD      r1, r1, r2
	STR      r1, [sp, #4]
	LDRSB    r2, [r5, r3]
	LDR      r1, [r6, #0x2c]
	LDR      r0, [r0, #4]
	ADD      r1, r1, r2
	ADD      r0, r1, r0
	STR      r0, [sp, #8]
	LDRB     r0, [r5, #2]
	LDRB     r1, [r5, #3]
	LDR      r2, [sp, #4]
	ADD      r0, r2, r0
	STR      r0, [sp, #0xc]
	LDR      r0, [sp, #8]
	ADD      r0, r0, r1
	LDR      r1, [pc, #0x68]
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	ADD      r1, #0x14
	BL       |inc_0x049120_0x055620| + 0xa1a0
	CMP      r0, #0
	BEQ      |loc_08020D9C|
	LDR      r0, [r4]
	LDR      r1, [r5, #4]
	LDR      r2, [pc, #0x5c]
	STR      r1, [r0]
	LDR      r0, [r4]
	MOV      r3, #3
	LDR      r1, [r0]
	LSL      r3, r3, #0xa
	AND      r1, r2
	LDR      r2, [sp, #4]
	LSL      r2, r2, #0x17
	LSR      r2, r2, #7
	ORR      r1, r2
	STR      r1, [r0]
	LDR      r0, [r4]
	LDR      r2, [sp, #8]
	LSR      r1, r1, #8
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x18
	LSL      r1, r1, #8
	ORR      r1, r2
	STR      r1, [r0]
	LDRH     r0, [r6, #0xc]
	ADD      r1, r0, r7
	LDR      r0, [r4]
	LSL      r1, r1, #0x16
	ADD      r0, #4
	LDR      r2, [r0]
	LSR      r1, r1, #0x16
	LSR      r2, r2, #0xa
	LSL      r2, r2, #0xa
	ORR      r1, r2
	STR      r1, [r0]
	LDRB     r0, [r6, #8]
	LDR      r2, [r4]
	BIC      r1, r3
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	ORR      r0, r1
	STR      r0, [r2, #4]
	LDR      r0, [r4]
	ADD      r0, #8
	STR      r0, [r4]
|loc_08020D9C|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_08020DA0|
|unk_08020DA0|
; cited by 0x08020AF0 (a pc-relative load targets 0x08020DA0)
	INCBIN  baserom.gba_0x20da0_0x20dac.extracted
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDRB r0, [r0, #0x10]
		ADD r6, r1, #0
		SUB sp, #0x2c
		CMP r0, #0
		BEQ      |loc_08020DF6|
		MOV r5, #0
		CMP r0, #1
		LDR r1, [pc, #0x294]
		ADD r7, sp, #0x28
		BEQ      |loc_08020E82|
		CMP r0, #2
		BNE      |loc_08020E80|
		LDR r0, [r6]
		ADD r2, r1, #0
		STR r2, [sp]
		ADD r2, r7, #0
		MOV r1, #0xd
		ADD r3, r5, #0
		STR r0, [sp, #0x28]
		ADD r0, r4, #0
		BL       |loc_08020CF4|
		LDR r0, [r4, #0x40]
		LDRB r0, [r0, #4]
		LSL r0, r0, #0x1e
		BPL      |loc_08020EAE|
		LDR r2, [pc, #0x26c]
		ADD r3, r5, #0
		STR r2, [sp]
		ADD r2, r7, #0
		MOV r1, #0xf
		ADD r0, r4, #0
		BL       |loc_08020CF4|
		B        |loc_08020EAE|
|loc_08020DF6|
		LDR r1, [r4, #0x48]
		MOV r3, #0
		LDR r0, [r4, #0x28]
		LDRSB r1, [r1, r3]
		MOV r3, #1
		SUB r0, r0, r1
		STR r0, [sp, #0x18]
		LDR r1, [r4, #0x48]
		LDR r0, [r4, #0x2c]
		LDRSB r1, [r1, r3]
		SUB r0, r0, r1
		STR r0, [sp, #0x1c]
		LDR r1, [r4, #0x48]
		LDRB r0, [r1, #2]
		LDRB r1, [r1, #3]
		LDR r2, [sp, #0x18]
		ADD r0, r2, r0
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x1c]
		ADD r0, r0, r1
		LDR r1, [pc, #0x234]
		STR r0, [sp, #0x24]
		ADD r0, sp, #0x18
		ADD r1, #0x18
		BL       |inc_0x049120_0x055620| + 0xa1a0
		CMP r0, #0
		BEQ      |loc_08020E80|
		LDR r0, [r6]
		LDR r2, [pc, #0x224]
		ADD r1, r0, #0
		ADD r1, #8
		STR r1, [r6]
		STR r0, [sp, #0x28]
		LDR r1, [r4, #0x48]
		MOV r3, #3
		LDR r1, [r1, #4]
		LSL r3, r3, #0xa
		STR r1, [r0]
		LDR r0, [sp, #0x28]
		LDR r1, [r0]
		AND r1, r2
		LDR r2, [sp, #0x18]
		LSL r2, r2, #0x17
		LSR r2, r2, #7
		ORR r1, r2
		STR r1, [r0]
		LDR r2, [sp, #0x1c]
		LSR r1, r1, #8
		LSL r2, r2, #0x18
		LSR r2, r2, #0x18
		LSL r1, r1, #8
		ORR r1, r2
		STR r1, [r0]
		LDRH r1, [r4, #0xc]
		LDR r2, [r0, #4]
		LSR r2, r2, #0xa
		LSL r1, r1, #0x16
		LSR r1, r1, #0x16
		LSL r2, r2, #0xa
		ORR r1, r2
		STR r1, [r0, #4]
		LDRB r2, [r4, #8]
		BIC r1, r3
		LSL r2, r2, #0x1a
		LSR r2, r2, #0x1e
		LSL r2, r2, #0xa
		ORR r1, r2
		STR r1, [r0, #4]
|loc_08020E80|
		DCW     0xE09D
|loc_08020E82|
		LDR r0, [r6]
		LDR r2, [pc, #0x1cc]
		ADD r3, r5, #0
		STR r2, [sp]
		ADD r2, r7, #0
		MOV r1, #0
		STR r0, [sp, #0x28]
		ADD r0, r4, #0
		BL       |loc_08020CF4|
		LDR r0, [r4, #0x40]
		LDRB r0, [r0, #4]
		LSL r0, r0, #0x1f
		BPL      |loc_08020EAE|
		LDR r2, [pc, #0x1b4]
		ADD r3, r5, #0
		STR r2, [sp]
		ADD r2, r7, #0
		MOV r1, #2
		ADD r0, r4, #0
		BL       |loc_08020CF4|
|loc_08020EAE|
		LDR r0, [r4, #0x38]
		LDR r1, [r4, #0x30]
		LDR r2, [r4, #0x34]
		MUL r1, r0
		MUL r2, r0
		ADD r0, r1, #0
		STR r0, [sp, #0x10]
		STR r2, [sp, #0xc]
		STR r2, [sp, #0x14]
		STR r1, [sp, #8]
		LDRB r0, [r4, #0x11]
		MOV r3, #0x10
		ADD r5, sp, #0x10
		CMP r0, #0
		DCW     0xD011
		ADD r2, r7, #0
		MOV r1, #0xa
		ADD r0, r4, #0
		STR r5, [sp]
		BL       |loc_08020CF4|
		LDR r0, [r4, #0x40]
		LDRB r0, [r0, #4]
		LSL r0, r0, #0x1c
		BPL      |loc_08020F14|
		MOV r3, #0x10
		ADD r2, r7, #0
		MOV r1, #0xc
		ADD r0, r4, #0
		STR r5, [sp]
	INCBIN  baserom.gba_0x20eea_0x20eec.extracted
|sub_08020EEC|
|unk_08020EEC|
	INCBIN	baserom.gba_0x20eec_0x20ef0.extracted
	MOV      r3, #0x10
	ADD      r2, r7, #0
	MOV      r1, #7
	ADD      r0, r4, #0
	STR      r5, [sp]
	BL       |loc_08020CF4|
	LDR      r0, [r4, #0x40]
	LDRB     r0, [r0, #4]
	LSL      r0, r0, #0x1d
	BPL      |loc_08020F14|
	MOV      r3, #0x10
	ADD      r2, r7, #0
	MOV      r1, #9
	ADD      r0, r4, #0
	STR      r5, [sp]
	BL       |loc_08020CF4|
|loc_08020F14|
	LDR      r0, [r4, #0x38]
	LDRB     r1, [r4, #0x12]
	ADD      r0, #7
	MOV      r5, #0
	SUB      r0, r0, r1
	CMP      r0, #0
	BLE      |loc_08020F50|
|loc_08020F22|
	LDR      r0, [r4, #0x30]
	LDR      r1, [r4, #0x34]
	MUL      r0, r5
	MUL      r1, r5
	STR      r0, [sp]
	ADD      r2, sp, #8
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	MOV      r1, #5
	ADD      r2, r7, #0
	STR      r0, [sp, #8]
	MOV      r3, #8
	ADD      r0, r4, #0
	BL       |loc_08020CF4|
	LDRB     r0, [r4, #0x12]
	LDR      r1, [r4, #0x38]
	ADD      r1, #7
	ADD      r5, r0, r5
	SUB      r0, r1, r0
	CMP      r0, r5
	BGT      |loc_08020F22|
|loc_08020F50|
	LDR      r0, [r4, #0x38]
	SUB      r0, #9
	CMP      r0, r5
	BLE      |loc_08020F86|
	LDR      r0, [r4, #0x4c]
	LDR      r1, [r0, #0x38]
	LDR      r0, [r0, #0x44]
	SUB      r0, r1, r0
	LDR      r1, [r4, #0x30]
	LDR      r2, [r4, #0x34]
	MUL      r1, r5
	MUL      r2, r5
	STR      r2, [sp, #4]
	STR      r2, [sp, #0xc]
	STR      r1, [sp]
	ADD      r2, sp, #8
	ASR      r0, r0, #5
	ADD      r3, r0, #0
	STR      r2, [sp]
	STR      r1, [sp, #8]
	MOV      r1, #4
	ADD      r2, r7, #0
	ADD      r3, #8
	ADD      r0, r4, #0
	BL       |loc_08020CF4|
	ADD      r5, #0x10
|loc_08020F86|
	LDR      r0, [r4, #0x38]
	SUB      r0, #1
	CMP      r0, r5
	BLE      |loc_08020FBA|
	LDR      r0, [r4, #0x4c]
	LDR      r1, [r0, #0x2c]
	LDR      r0, [r0, #0x44]
	SUB      r0, r1, r0
	LDR      r1, [r4, #0x30]
	LDR      r2, [r4, #0x34]
	MUL      r1, r5
	MUL      r2, r5
	STR      r2, [sp, #4]
	STR      r2, [sp, #0xc]
	STR      r1, [sp]
	ADD      r2, sp, #8
	ASR      r0, r0, #5
	ADD      r3, r0, #0
	STR      r2, [sp]
	STR      r1, [sp, #8]
	MOV      r1, #3
	ADD      r2, r7, #0
	ADD      r3, #8
	ADD      r0, r4, #0
	BL       |loc_08020CF4|
|loc_08020FBA|
	LDR      r0, [sp, #0x28]
	STR      r0, [r6]
	MOV      r0, #0
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	SUB      sp, #0x10
	CMP      r1, #0
	BEQ      |sub_08020FE6|
	CMP      r1, #0xb
	BEQ      |loc_0802104A|
	CMP      r1, #0xc
	BNE      |loc_0802104E|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0
	ADD      sp, #0x10
	POP      {r4, pc}
|sub_08020FE6|
|unk_08020FE6|
		LDR r1, [r2, #0x30]
		CMP r1, r0
		BNE      |loc_08020FF0|
		MOV r0, #0
		DCW     0xE7F8
|loc_08020FF0|
		LDRB r1, [r2, #0x14]
		LDR r3, [r0, #0x3c]
		MOV r4, #1
		EOR r3, r4
		CMP r1, r3
		BEQ      |loc_08021000|
		MOV r0, #0
		DCW     0xE7F0
|loc_08021000|
		LDR r1, [r0, #0x38]
		LDR r3, [r0, #0x30]
		LDR r4, [r0, #0x34]
		MUL r3, r1
		MUL r4, r1
		ADD r1, r3, #0
		STR r3, [sp, #8]
		ADD r3, r4, #0
		STR r4, [sp, #0xc]
		LDR r4, [r0, #0x20]
		LDR r0, [r0, #0x24]
		ADD r1, r4, r1
		ADD r0, r0, r3
		STR r0, [sp, #0xc]
		ADD r0, r1, #0
		STR r1, [sp, #8]
		LDR r1, [sp, #0xc]
		ADD r3, r0, #0
		ADD r4, r1, #0
		ADD r1, #0xc
		SUB r4, #0xc
		SUB r3, #0xc
		ADD r0, #0xc
		STR r0, [sp, #8]
		STR r1, [sp, #0xc]
		MOV r1, sp
		ADD r0, r2, #4
		STR r3, [sp]
		STR r4, [sp, #4]
		BL       |inc_0x049120_0x055620| + 0xa1a0
		CMP r0, #0
		BEQ      |loc_08021046|
		MOV r0, #1
		DCW     0xE7CD
|loc_08021046|
		MOV r0, #0
		DCW     0xE7CB
|loc_0802104A|
|unk_0802104A|
		MOV r0, #0
		DCW     0xE7C9
|loc_0802104E|
|unk_0802104E|
; cited by 0x08020DBE (a pc-relative load targets 0x08021054)
		MOV r0, #0
		DCW     0xE7C7
	INCBIN  baserom.gba_0x21052_0x2105a.extracted
|sub_0802105A|
|unk_0802105A|
	INCBIN  baserom.gba_0x2105a_0x2105c.extracted
		CMP r1, #3
	BLT      |sub_08021064|
	MOV      r0, #1
	BX       lr
|sub_08021064|
|unk_08021064|
		MOV r0, #0
		BX       lr
|sub_08021068|
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_08021078|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08021082|
|loc_08021078|
	MOV      r1, #0
	STR      r1, [r0]
	STR      r1, [r0, #0xc]
	LDR      r1, [pc, #0x98]
	STR      r1, [r0, #8]
|loc_08021082|
	POP      {r3, pc}
	ADD      r1, r0, #0
	LDR      r1, [r1, #8]
	LDR      r2, [pc, #0x8c]
	MOV      r0, #1
	CMP      r1, r2
	BNE      |loc_08021092|
	MOV      r0, #0
|loc_08021092|
	BX       lr
|loc_08021094|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #8]
	ADD      r5, r1, #0
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	STR      r5, [r4, #8]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
|loc_080210B6|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [pc, #0x50]
	STR      r0, [r4, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r4, pc}
	PUSH     {r4}
	LDR      r2, [r0, #0xc]
	ADD      r1, r0, #0
	ADD      r3, r2, #1
	LSL      r2, r2, #2
	ADD      r1, #0xc
	LDR      r4, [r0, #8]
	STR      r3, [r0, #0xc]
	ADD      r1, r2, r1
	STR      r4, [r1, #4]
	LDR      r1, [pc, #0x2c]
	STR      r1, [r0, #8]
	POP      {r4}
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r4, #0xc]
	ADD      r0, r4, #0
	SUB      r1, #1
	STR      r1, [r4, #0xc]
	LSL      r1, r1, #2
	ADD      r0, #0xc
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	STR      r0, [r4, #8]
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r4, r4, r5
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x48]
	LDR      r1, [r4, #4]
	ADD      r1, #0x80
	LDR      r1, [r1, #0x10]
	LDR      r5, [r0, #0xc]
	CMP      r1, #0
	BEQ      |sub_0802114C|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08021142|
	LDR      r1, [pc, #0x34]
	STMIA    r0!, {r1, r5}
	SUB      r0, #8
	MOV      r1, #0
	MVN      r1, r1
	STR      r1, [r0, #8]
|loc_08021142|
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |loc_08021094|
	POP      {r3, r4, r5, pc}
|sub_0802114C|
|unk_0802114C|
; cited by 0x0802111E (a pc-relative load targets 0x08021168)
		MOV r0, #8
		DCW     0xF01C
		DCW     0xFA33
		CMP r0, #0
		BEQ      |loc_0802115C|
		LDR r1, [pc, #0x18]
		STMIA r0!, {r1, r5}
		SUB r0, #8
|loc_0802115C|
		ADD r1, r0, #0
		LDR r0, [r4]
		BL       |loc_08021094|
		DCW     0xE7F1
	INCBIN  baserom.gba_0x21166_0x2116e.extracted
|sub_0802116E|
	LSR      r4, r0, #0x20
	BCC      |loc_08021174|
	LSR      r4, r0, #0x20
|loc_08021174|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r2, #0
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08021188|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080211A6|
|loc_08021188|
	LDR      r1, [pc, #0xd4]
	MOV      r3, #0
	STMIA    r0!, {r1, r3}
	LDR      r2, [pc, #0xd4]
	SUB      r0, #8
	LDR      r1, [pc, #0xd4]
	STR      r2, [r0, #8]
	STR      r1, [r0]
	ADD      r1, #0x2c
	STR      r1, [r0, #8]
	LDMIA    r4!, {r2, r4}
	ADD      r0, #0xc
	STMIA    r0!, {r2, r4, r5}
	SUB      r0, #0x18
	STR      r3, [r0, #0x2c]
|loc_080211A6|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, lr}
	LDR      r5, [pc, #0xc0]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	SUB      sp, #0x14
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r0, [r0, #4]
	STR      r1, [sp, #0xc]
	STR      r0, [sp, #0x10]
	LDR      r2, [sp, #0x10]
	LSL      r1, r1, #0xa
	STR      r1, [r4, #0x20]
	LSL      r2, r2, #0xa
	STR      r2, [r4, #0x24]
	LDR      r2, [r4, #0x14]
	ADD      r1, r4, #0
	STR      r2, [sp]
	ADD      r2, r4, #0
	ADD      r2, #0x28
	ADD      r1, #0xc
	ADD      r0, sp, #0xc
	ADD      r3, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x3edc
	LDR      r0, [sp, #4]
	MOV      r1, #0
	LSL      r0, r0, #2
	STR      r0, [r4, #0x18]
	LDR      r0, [sp, #8]
	LSL      r0, r0, #2
	STR      r0, [r4, #0x1c]
	CMP      r4, #0
	BEQ      |loc_080211F0|
	ADD      r1, r4, #0
	ADD      r1, #8
|loc_080211F0|
	LDR      r0, [r5, #4]
	BL       |loc_08021094|
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r0, #0x18
	LDMIA    r0!, {r2}
	LDR      r1, [r4, #0x20]
	ADD      r5, r4, #0
	ADD      r1, r1, r2
	STR      r1, [r4, #0x20]
	LDR      r1, [r4, #0x24]
	LDR      r0, [r0]
	ADD      r5, #0x20
	ADD      r0, r1, r0
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x28]
	ADD      r6, r5, #4
	SUB      r0, #1
	STR      r0, [r4, #0x28]
	CMP      r0, #0
	LDR      r7, [pc, #0x4c]
	BNE      |loc_08021238|
	MOV      r0, #1
	STR      r0, [r4, #0x2c]
	LDR      r0, [r7, #4]
	BL       |loc_080210B6|
	LDR      r0, [r4, #0xc]
	LDR      r1, [r4, #0x10]
	LSL      r0, r0, #0xa
	STR      r0, [r5]
	LSL      r1, r1, #0xa
	STR      r1, [r6]
|loc_08021238|
	LDR      r0, [r7]
	ADD      r0, #0x80
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |sub_08021254|
	LDR      r0, [r7]
	LDR      r1, [r5]
	STMIA    r0!, {r1}
	LDR      r1, [r6]
	STR      r1, [r0]
	LDR      r0, [r7]
	BL       |sub_0802ed98|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08021254|
|unk_08021254|
; cited by 0x08021188 (a pc-relative load targets 0x08021260)
		ADD r1, r5, #0
		LDR r0, [r7]
		BL       |loc_08009744|
		DCW     0xE7F9
	INCBIN  baserom.gba_0x2125e_0x2126a.extracted
|sub_0802126A|
	LSR      r4, r0, #0x20
	STR      r4, [r0, r2]
	LSR      r2, r6, #1
	LDR      r0, [pc, #8]
	PUSH     {r3, lr}
	LDR      r0, [r0]
	BL       |loc_080210B6|
	POP      {r3, pc}
|sub_0802127C|
|unk_0802127C|
	INCBIN	baserom.gba_0x2127c_0x2127e.extracted
|sub_0802127E|
	LSR      r2, r6, #1
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r7, r3, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r6, [sp, #0x28]
	BNE      |sub_080212A0|
	MOV      r0, #0x60
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080212A0|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_080212A0|
|unk_080212A0|
		MOV r1, #1
		LSL r1, r1, #0xc
		ADD r2, r7, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x2b8]
		STR r0, [r4]
		LDR r3, [r5]
		LDR r5, [r5, #4]
		LSL r3, r3, #8
		STR r3, [r4, #0x20]
		LSL r5, r5, #8
		STR r5, [r4, #0x24]
		STR r6, [r4, #0x5c]
		LDR r2, [sp, #0xc]
		MOV r5, #0
		STRB r2, [r4, #8]
		LDR r2, [r6, #4]
		ADD r0, r4, #0
		STR r2, [r4, #0x18]
		STR r5, [r4, #0x40]
		STR r5, [r4, #0x44]
		MOV r2, #1
		ADD r0, #0x54
		LSL r2, r2, #0xd
		STR r5, [r4, #0x48]
		STR r2, [r0]
		ADD r1, r0, #4
		LSR r0, r2, #4
		STR r0, [r1]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [pc, #0x284]
		ADD r3, r5, #0
		LDR r5, [pc, #0x288]
		LDR r0, [r0]
		MOV r2, #0x40
		ADD r0, r0, r5
		LDR r1, [pc, #0x27c]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		DCW     0xE7D0
|sub_080212FA|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x268]
	ADD      r6, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0x44]
	LDR      r5, [pc, #0x264]
	CMP      r0, #0
	BNE      |loc_08021318|
	LDR      r2, [pc, #0x264]
	LDR      r0, [r5]
	LDR      r1, [pc, #0x25c]
	ADD      r0, r0, r2
	BL       |inc_0x03d784_0x041118| + 0xb7e
|loc_08021318|
	LDR      r0, [pc, #0x25c]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x25c]
	CMP      r1, r0
	BEQ      |loc_0802132A|
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0802132A|
	LDR      r0, [pc, #0x254]
	CMP      r6, #0
	STR      r0, [r4]
	BEQ      |loc_08021338|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08021338|
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	LDR      r1, [r0, #0x40]
	LDR      r2, [r0, #0x44]
	ADD      r4, r0, #0
	ADD      r1, #1
	CMP      r2, #0
	LDR      r0, [r0, #0x5c]
	SUB      sp, #0x34
	BEQ      |loc_0802142C|
	LDR      r2, [r4, #0x48]
	CMP      r2, #0
	BEQ      |loc_08021380|
	STR      r1, [r4, #0x40]
	LDRB     r2, [r0, #2]
	ASR      r1, r1, #2
	CMP      r2, r1
	BGT      |sub_0802136C|
	LDR      r5, [pc, #0x20c]
	ADD      r1, r4, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
|sub_0802136C|
|unk_0802136C|
		LSL r3, r1, #1
		ADD r1, r3, r1
		LDR r0, [r0, #8]
		LSL r1, r1, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		DCW     0xE7F3
|loc_08021380|
|unk_08021380|
		LDR r3, [r4, #0x20]
		LDR r6, [r4, #0x4c]
		ADD r3, r3, r6
		STR r3, [r4, #0x20]
		LDR r2, [r4, #0x50]
		LDR r3, [r4, #0x24]
		ADD r2, r3, r2
		STR r2, [r4, #0x24]
		LDR r2, [r4, #0x50]
		STR r1, [r4, #0x40]
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1f
		ADD r2, #0x20
		STR r2, [r4, #0x50]
		LSL r3, r1, #1
		ADD r1, r3, r1
		LDR r0, [r0, #4]
		LSL r1, r1, #2
		ADD r0, r0, r1
		ADD r0, #0xc
		STR r0, [r4, #0x18]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [r4, #0x58]
		SUB r0, #0x20
		STR r0, [r4, #0x58]
		LDR r1, [r4, #0x54]
		ADD r0, r1, r0
		STR r0, [r4, #0x54]
		DCW     0xD5D4
		MOV r6, #0
		CMP r5, #0
		BEQ      |loc_08021424|
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		MOV r5, sp
		ADD r7, r5, #4
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x1b0]
		STR r0, [sp, #0x1c]
		LDR r0, [r4, #0x5c]
		LDRH r0, [r0]
		STR r0, [sp, #0x18]
		ADD r0, r4, #0
		ADD r0, #0x28
		LDMIA r0!, {r0, r1, r2, r3}
		STMIA r7!, {r0, r1, r2, r3}
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		ADD r0, #0xff
		ADD r0, #0xc1
		LDR r0, [r0, #0x10]
		ADD r2, r5, #0
		LDR r5, [pc, #0x178]
		STRB r0, [r3]
		STR r4, [sp, #0x30]
		LDR r0, [r5, #4]
		MOV r1, #0
		BL       |loc_08011C0C|
		CMP r0, #0
		BEQ      |loc_08021424|
		LDR r5, [r5]
		MOV r0, #3
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		LDR r1, [pc, #0x160]
		ADD r0, r3, r0
		LSL r0, r0, #2
		SUB r1, #0x24
		ADD r1, r0, r1
		LDR r0, [pc, #0x158]
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r5, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08021424|
		MOV r0, #1
		STR r0, [r4, #0x48]
		STR r6, [r4, #0x40]
		DCW     0xE79D
|loc_0802142C|
|unk_0802142C|
		B        |loc_0802142E|
|loc_0802142E|
		STR r1, [r4, #0x40]
		LSL r1, r1, #0x1b
		LSR r1, r1, #0x1e
		CMP r1, #3
		LDR r0, [r0, #4]
		BNE      |loc_08021440|
		ADD r0, #0xc
		STR r0, [r4, #0x18]
		B        |loc_0802144A|
|loc_08021440|
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r1, r1, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
|loc_0802144A|
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		DCW     0xE78A
|sub_08021452|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	MOV      r0, #1
	STR      r0, [r4, #0x44]
	LDR      r0, [r4, #0x5c]
	ADD      r5, r1, #0
	LDR      r1, [r0, #4]
	ADD      r6, r2, #0
	ADD      r1, #0x18
	STR      r1, [r4, #0x18]
	LDRB     r2, [r1, #2]
	LDRB     r0, [r1, #3]
	LDR      r3, [pc, #0x11c]
	MUL      r2, r0
	LDRH     r0, [r4, #0xc]
	LDR      r1, [r1, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	MOV      r0, #0x37
	STRB     r0, [r4, #8]
	CMP      r5, #1
	BNE      |loc_08021490|
	LDR      r1, [r4, #0x24]
	LSL      r0, r5, #0xb
	SUB      r0, r1, r0
	STR      r0, [r4, #0x24]
|loc_08021490|
	LSL      r0, r5, #3
	LDR      r1, [pc, #0xf8]
	LDR      r3, [pc, #0xf8]
	LDR      r2, [r1, r0]
	ADD      r0, r0, r1
	MUL      r2, r6
	MUL      r2, r3
	ASR      r2, r2, #8
	STR      r2, [r4, #0x4c]
	LDR      r0, [r0, #4]
	MOV      r1, #1
	MUL      r0, r6
	MUL      r0, r3
	ASR      r0, r0, #8
	LSL      r1, r1, #9
	SUB      r0, r0, r1
	STR      r0, [r4, #0x50]
	LDR      r0, [pc, #0xb8]
	LDR      r5, [pc, #0xb8]
	LDR      r2, [pc, #0xbc]
	LDR      r0, [r0]
	SUB      r5, #0x24
	ADD      r1, r5, #0
	ADD      r1, #0x24
	ADD      r0, r0, r2
	ADD      r4, r0, #0
	BL       |inc_0x03d784_0x041118| + 0xb7e
	ADD      r1, r5, #0
	ADD      r1, #0xff
	ADD      r1, #0x99
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	POP      {r4, r5, r6, pc}
	PUSH     {r0, r1, r2, r3, r4, r5, r6, lr}
	ADD      r4, r0, #0
	MOV      r0, #1
	LDR      r5, [sp, #0x20]
	STR      r0, [r4, #0x44]
	LDR      r0, [r4, #0x5c]
	ADD      r6, r1, #0
	LDR      r1, [r0, #4]
	LDR      r3, [pc, #0x9c]
	ADD      r1, #0x18
	STR      r1, [r4, #0x18]
	LDRB     r2, [r1, #2]
	LDRB     r0, [r1, #3]
	MUL      r2, r0
	LDRH     r0, [r4, #0xc]
	LDR      r1, [r1, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	MOV      r0, #0x37
	STRB     r0, [r4, #8]
	CMP      r6, #1
	BNE      |loc_08021518|
	LDR      r1, [r4, #0x24]
	LSL      r0, r6, #0xb
	SUB      r0, r1, r0
	STR      r0, [r4, #0x24]
|loc_08021518|
	LDR      r1, [sp, #8]
	LDR      r3, [pc, #0x74]
	STR      r1, [r4, #0x4c]
	LDR      r1, [sp, #0xc]
	LDR      r2, [pc, #0x50]
	STR      r1, [r4, #0x50]
	LDR      r0, [r4, #0x4c]
	MUL      r1, r5
	MUL      r0, r5
	MUL      r0, r3
	ASR      r0, r0, #0x10
	STR      r0, [r4, #0x4c]
	ADD      r0, r1, #0
	MUL      r0, r3
	MOV      r1, #1
	LSL      r1, r1, #9
	ASR      r0, r0, #0x10
	SUB      r0, r0, r1
	STR      r0, [r4, #0x50]
	LDR      r0, [pc, #0x2c]
	LDR      r5, [pc, #0x2c]
	LDR      r0, [r0]
	SUB      r5, #0x24
	ADD      r1, r5, #0
	ADD      r1, #0x24
	ADD      r0, r0, r2
	ADD      r4, r0, #0
	BL       |inc_0x03d784_0x041118| + 0xb7e
	ADD      r1, r5, #0
	ADD      r1, #0xff
	ADD      r1, #0x99
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
|sub_08021566|
	DCW      0x0000
	DCW      0xa33c,0x0804,0x5090,0x0872,0x92cc,0x0831,0x05c4,0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xe454
|sub_08021582|
	LSR      r4, r0, #0x20
	STRH     r0, [r0, #6]
	LSR      r3, r5, #1
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	MOV      r6, #0x8c
	LSR      r7, r0, #0x20
	LSL      r4, r6, #0x17
	LSL      r0, r0, #0
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_080215B0|
	MOV      r0, #0x50
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080215B0|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_080215B0|
|unk_080215B0|
		LDR r7, [pc, #0x174]
		LDRB r5, [r7]
		LDRB r0, [r7, #1]
		MUL r5, r0
		LDR r0, [pc, #0x170]
		ADD r1, r5, #0
		STR r0, [r4]
		STRH r5, [r4, #0xe]
		SUB r0, r7, #6
		LDR r0, [r0]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_080215E0|
		ADD r1, r5, #0
		SUB r0, r7, #6
		LDR r0, [r0]
		BL       |sub_08011732|
		ADD r1, r5, #0
		SUB r0, r7, #6
		LDR r0, [r0]
		BL       |loc_0801124C|
|loc_080215E0|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LDR r1, [pc, #0x148]
		STRH r0, [r4, #0xc]
		STR r1, [r4]
		LDR r1, [pc, #0x13c]
		MOV r2, #0x3a
		SUB r1, #2
		STR r1, [r4, #0x28]
		STRB r2, [r4, #8]
		LDRB r2, [r7]
		LDRB r3, [r7, #1]
		LSL r0, r0, #5
		LDR r1, [r1, #8]
		MUL r2, r3
		LDR r3, [pc, #0x134]
		ADD r0, r0, r3
		BL       |sub_08049138|
		LDR r0, [pc, #0x130]
		STR r0, [r4]
		LDR r0, [pc, #0x130]
		LDMIA r6!, {r1, r2}
		STR r0, [r4]
		STR r1, [r4, #0x2c]
		STR r2, [r4, #0x30]
		MOV r0, #0
		STR r0, [r4, #0x34]
		LDR r0, [sp, #0x10]
		MOV r1, #0x46
		STR r0, [r4, #0x44]
		MOV r0, #2
		STR r0, [r4, #0x38]
		LDR r0, [sp, #0xc]
		SUB r6, #8
		CMP r0, #2
		STR r0, [r4, #0x40]
		BLT      |loc_0802162E|
		MOV r1, #0x64
|loc_0802162E|
		STR r1, [r4, #0x3c]
		ADD r0, r4, #0
		ADD r4, #0x48
		LDMIA r6!, {r1, r2}
		STMIA r4!, {r1, r2}
		DCW     0xE7B8
		PUSH {r4, r5}
		LDR r2, [r0, #0x44]
		LDR r1, [r0, #0x34]
		LDR r3, [r0, #0x3c]
		LDR r4, [r0, #0x40]
		SUB sp, #8
		CMP r2, #0
		BEQ      |loc_080216D4|
		CMP r4, #0
		BEQ      |loc_08021668|
		CMP r4, #1
		BEQ      |loc_08021682|
		CMP r4, #2
		BEQ      |loc_0802169C|
		CMP r4, #3
		BNE      |loc_080216C0|
		LDRH r2, [r2, #2]
		LSL r5, r2, #0x1b
		LSR r5, r5, #0x1f
		BEQ      |loc_080216B6|
		ADD r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_08021668|
		LDRH r2, [r2, #2]
		LSL r5, r2, #0x18
		LSR r5, r5, #0x1f
		BEQ      |loc_08021676|
		ADD r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_08021676|
		LSL r2, r2, #0x19
		LSR r2, r2, #0x1f
		BEQ      |loc_080216C0|
		SUB r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_08021682|
		LDRH r2, [r2, #2]
		LSL r5, r2, #0x19
		LSR r5, r5, #0x1f
		BEQ      |loc_08021690|
		ADD r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_08021690|
		LSL r2, r2, #0x18
		LSR r2, r2, #0x1f
		BEQ      |loc_080216C0|
		SUB r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_0802169C|
		LDRH r2, [r2, #2]
		LSL r5, r2, #0x1a
		LSR r5, r5, #0x1f
		BEQ      |loc_080216AA|
		ADD r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_080216AA|
		LSL r2, r2, #0x1b
		LSR r2, r2, #0x1f
		BEQ      |loc_080216C0|
		SUB r1, #2
		STR r1, [r0, #0x34]
		B        |loc_080216C0|
|loc_080216B6|
		LSL r2, r2, #0x1a
		LSR r2, r2, #0x1f
		BEQ      |loc_080216C0|
		SUB r1, #2
		STR r1, [r0, #0x34]
|loc_080216C0|
		LDR r1, [r0, #0x34]
		CMP r1, #0x10
		BGE      |loc_080216CA|
		MOV r1, #0x10
		STR r1, [r0, #0x34]
|loc_080216CA|
		LDR r1, [r0, #0x34]
		CMP r1, r3
		BLE      |loc_080216F2|
		STR r3, [r0, #0x34]
		B        |loc_080216F2|
|loc_080216D4|
		LDR r2, [r0, #0x38]
		ADD r1, r1, r2
		STR r1, [r0, #0x34]
		CMP r1, r3
		BLT      |sub_080216E6|
		MOV r1, #1
		MVN r1, r1
		STR r1, [r0, #0x38]
		B        |loc_080216F2|
|sub_080216E6|
	CMP      r2, #0
	BGE      |loc_080216F2|
	CMP      r1, #0x10
	BGE      |loc_080216F2|
	MOV      r1, #2
	STR      r1, [r0, #0x38]
|loc_080216F2|
	LDR      r3, [pc, #0x34]
	LSL      r2, r4, #3
	ADD      r3, #0xa
	ADD      r2, r2, r3
	LDR      r4, [r2]
	LDR      r3, [r0, #0x34]
	LDR      r2, [r2, #4]
	MUL      r4, r3
	MUL      r2, r3
	STR      r2, [sp, #4]
	LDR      r3, [sp, #4]
	ADD      r2, r4, #0
	STR      r4, [sp]
	LDR      r4, [r0, #0x48]
	ADD      r1, r0, #0
	LDR      r0, [r0, #0x4c]
	ADD      r2, r4, r2
	ADD      r0, r0, r3
	STR      r0, [sp, #4]
	ADD      r1, #0x2c
	ADD      r0, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STMIA    r1!, {r0, r2}
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
|sub_08021728|
|unk_08021728|
	INCBIN	baserom.gba_0x21728_0x2172a.extracted
|sub_0802172A|
	LSR      r2, r6, #1
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
|unk_08021730|
	INCBIN	baserom.gba_0x21730_0x21732.extracted
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	LDMIA    r2!, {r7}
	LSR      r4, r0, #0x20
|unk_0802173C|
	INCBIN	baserom.gba_0x2173c_0x2173e.extracted
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r2, [r0, #0x28]
	CMP      r2, r1
	BEQ      |loc_08021760|
	STR      r1, [r0, #0x28]
	LDRB     r3, [r1, #2]
	LDRB     r4, [r1, #3]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r1, #8]
	MUL      r3, r4
	ADD      r2, r3, #0
	LDR      r3, [pc, #0xd0]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08021760|
	POP      {r4, pc}
|loc_08021762|
	PUSH     {r4, r5, r6}
	LDR      r1, [r0, #0x28]
	MOV      r3, #0
	LDRSB    r4, [r1, r3]
	LDR      r2, [r0, #0x20]
	MOV      r3, #1
	SUB      r2, r2, r4
	STR      r2, [r0, #0x10]
	LDRSB    r5, [r1, r3]
	LDR      r4, [r0, #0x24]
	SUB      r3, r4, r5
	STR      r3, [r0, #0x14]
	LDRB     r4, [r1, #2]
	LDRB     r1, [r1, #3]
	LDR      r5, [pc, #0xac]
	ADD      r4, r2, r4
	ADD      r1, r3, r1
	STR      r1, [r0, #0x1c]
	STR      r4, [r0, #0x18]
	LDR      r6, [r5, #8]
	CMP      r2, r6
	BGE      |loc_080217A0|
	LDR      r2, [r5]
	CMP      r2, r4
	BGE      |loc_080217A0|
	LDR      r2, [r5, #0xc]
	CMP      r3, r2
	BGE      |loc_080217A0|
	LDR      r2, [r5, #4]
	CMP      r2, r1
	BLT      |sub_080217A6|
|loc_080217A0|
	MOV      r0, #0
	POP      {r4, r5, r6}
	BX       lr
|sub_080217A6|
|unk_080217A6|
		STR r1, [r0, #4]
		MOV r0, #1
		DCW     0xE7FA
|sub_080217AC|
	PUSH     {r4}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	LDR      r4, [pc, #0x7c]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	LDR      r2, [r0, #0x28]
	LDR      r2, [r2, #4]
	STR      r2, [r1]
	LDR      r3, [r0, #0x10]
	AND      r2, r4
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x14]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRH     r2, [r0, #0xc]
	LDR      r3, [r1, #4]
	LSR      r3, r3, #0xa
	LSL      r2, r2, #0x16
	LSR      r2, r2, #0x16
	LSL      r3, r3, #0xa
	ORR      r2, r3
	STR      r2, [r1, #4]
	LDRB     r0, [r0, #8]
	MOV      r3, #3
	LSL      r3, r3, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r2, r3
	ORR      r0, r2
	STR      r0, [r1, #4]
	POP      {r4}
	MOV      r0, #0
	BX       lr
	PUSH     {r4, lr}
	CMP      r1, #0xb
	BNE      |sub_08021824|
	LDR      r1, [r0, #0x28]
	LDRH     r0, [r0, #0xc]
	LDRB     r3, [r1, #2]
	LDRB     r4, [r1, #3]
	LSL      r0, r0, #5
	LDR      r1, [r1, #8]
	MUL      r3, r4
	ADD      r2, r3, #0
	LDR      r3, [pc, #0xc]
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0
	POP      {r4, pc}
|sub_08021824|
|unk_08021824|
; cited by 0x08021756 (a pc-relative load targets 0x08021828)
		MOV r0, #0
		POP {r4, pc}
	INCBIN  baserom.gba_0x21828_0x21832.extracted
|sub_08021832|
|unk_08021832|
	INCBIN  baserom.gba_0x21832_0x21834.extracted
		PUSH {r4, lr}
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x34]
	LDR      r2, [r4, #0x2c]
	LDR      r0, [r0]
	SUB      sp, #8
	ADD      r0, #0x28
	LDR      r3, [r0]
	ADD      r1, #0x20
	SUB      r2, r2, r3
	LDR      r3, [r4, #0x30]
	LDR      r0, [r0, #4]
	STR      r2, [sp]
	SUB      r0, r3, r0
	STR      r0, [sp, #4]
	ADD      r0, r2, #0
	LDR      r2, [sp, #4]
	STMIA    r1!, {r0, r2}
	ADD      r0, r4, #0
	BL       |loc_08021762|
	CMP      r0, #0
	BNE      |sub_08021868|
	ADD      sp, #8
	POP      {r4, pc}
|sub_08021868|
|unk_08021868|
		LDR r0, [r4, #0x30]
		STR r0, [r4, #4]
		MOV r0, #1
		DCW     0xE7F9
	INCBIN  baserom.gba_0x21870_0x21872.extracted
|sub_08021872|
	LSR      r2, r6, #1
	LDR      r2, [pc, #0x33c]
	MOV      r0, #0
	STRB     r0, [r2]
	LDR      r1, [pc, #0x33c]
	STRB     r0, [r2, #1]
	LDR      r3, [r1, #0x10]
	STRH     r0, [r3, #2]
	LDR      r3, [r1, #0x10]
	STRH     r0, [r3, #4]
	LDR      r3, [r1, #0x10]
	STRH     r0, [r3, #6]
	LDR      r3, [r1, #0x10]
	ADD      r3, #0xff
	ADD      r3, #0x81
	STRH     r0, [r3, #0xc]
	LDR      r3, [r1, #0x14]
	STRH     r0, [r3, #2]
	LDR      r3, [r1, #0x14]
	STRH     r0, [r3, #4]
	LDR      r3, [r1, #0x14]
	STRH     r0, [r3, #6]
	LDR      r1, [r1, #0x14]
	ADD      r1, #0xff
	ADD      r1, #0x81
	STRH     r0, [r1, #0xc]
	MOV      r0, #1
	STR      r0, [r2, #8]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	LDR      r0, [pc, #0x300]
	MOV      r6, #1
	MOV      r4, #0
	LSL      r6, r6, #9
	SUB      sp, #0x14
	STR      r4, [r0, #8]
	ADD      r2, r6, #0
	MOV      r1, #0
	LDR      r0, [pc, #0x2f8]
	BL       |inc_0x049120_0x055620| + 0xc
	ADD      r2, r6, #0
	MOV      r1, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	LSL      r5, r6, #0x11
	STRH     r4, [r5]
	STRH     r4, [r5, #0x10]
	STRH     r4, [r5, #0x12]
	STRH     r4, [r5, #0x14]
	STRH     r4, [r5, #0x16]
	STRH     r4, [r5, #0x18]
	STRH     r4, [r5, #0x1a]
	STRH     r4, [r5, #0x1c]
	LDR      r0, [pc, #0x2d8]
	STRH     r4, [r5, #0x1e]
	STRH     r0, [r5, #0xa]
	MOV      r1, #0
	LSL      r0, r0, #0x19
	LDR      r2, [pc, #0x2d4]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0x1e
	STR      r0, [sp, #0xc]
	MOV      r0, #0x14
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	MOV      r2, #1
	STR      r4, [sp, #4]
	STR      r4, [sp, #8]
	LDR      r1, [pc, #0x2c0]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LSR      r2, r5, #0x11
	MOV      r0, #5
	LSL      r0, r0, #0x18
	STRH     r6, [r5]
	LDR      r1, [pc, #0x2b8]
	BL       |inc_0x049120_0x055620| + 0x24
	LSR      r2, r5, #0x11
	LDR      r1, [pc, #0x2b0]
	LDR      r0, [pc, #0x29c]
	BL       |inc_0x049120_0x055620| + 0x24
	LDR      r0, [pc, #0x2ac]
	STRH     r4, [r0, #0x10]
	ADD      r0, r7, #0
	BEQ      |loc_08021936|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08021936|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_0802193A|
|unk_0802193A|
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r1, [pc, #0x294]
		MOV r0, #0
		SUB sp, #0xec
		STR r0, [r1]
		LDR r1, [pc, #0x290]
		ADD r5, r4, #4
		ADD r6, r5, #4
		STR r0, [r1]
		B        |loc_08021B98|
|loc_08021950|
		MOV r0, #0x98
		ADD r3, sp, #0xc0
		STRH r0, [r3, #0x28]
		MOV r0, #0xdc
		STRH r0, [r3, #0x2a]
		LDR r0, [r7, #0x20]
		LDRB r0, [r0]
		CMP r0, #1
		BNE      |loc_080219BE|
		ADD r0, sp, #0x80
		BL       |inc_0x049120_0x055620| + 0x7244
		ADD r0, sp, #0x18
		BL       |inc_0x049120_0x055620| + 0x7244
		MOV r2, #0x68
		MOV r1, #0
		ADD r0, sp, #0x80
		BL       |sub_0804912C|
		MOV r2, #0x68
		MOV r1, #0
		ADD r0, sp, #0x18
		BL       |sub_0804912C|
		ADD r0, sp, #0x80
		LDR r1, [r7, #0x24]
		BL       |loc_0801339C|
		ADD r0, sp, #0x18
		LDR r1, [r7, #0x28]
		BL       |loc_0801339C|
		LDR r0, [r7, #0x28]
		LDR r0, [r0, #0x14]
		BL       |inc_0x0158_0x143f2|
		STR r0, [sp, #0x14]
		LDR r0, [r7, #0x24]
		LDR r0, [r0, #0x14]
		BL       |inc_0x0158_0x143f2|
		ADD r2, sp, #0x18
		ADD r1, sp, #0x80
		STR r1, [sp, #8]
		STR r2, [sp, #0xc]
		ADD r2, r0, #0
		STR r6, [sp, #4]
		STR r5, [sp]
		LDR r3, [sp, #0x14]
		LDR r0, [r7, #0x2c]
		ADD r1, sp, #0xe8
		BL       |inc_0x0158_0x143f2| + 0x8d18
		B        |loc_08021A18|
|loc_080219BE|
		ADD r0, sp, #0x80
		BL       |inc_0x049120_0x055620| + 0x7244
		ADD r0, sp, #0x18
		BL       |inc_0x049120_0x055620| + 0x7244
		ADD r1, sp, #0x80
		LDR r0, [r7, #0x24]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x65be
		ADD r1, sp, #0x18
		LDR r0, [r7, #0x28]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x65be
		ADD r3, sp, #0x20
		LDRB r0, [r3, #0xc]
		LDR r1, [pc, #0x1fc]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
		STR r0, [sp, #0x14]
		ADD r3, sp, #0x80
		LDRB r0, [r3, #0x14]
		LDR r1, [pc, #0x1e8]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
		ADD r2, sp, #0x18
		ADD r1, sp, #0x80
		STR r1, [sp, #8]
		STR r2, [sp, #0xc]
		ADD r2, r0, #0
		STR r6, [sp, #4]
		STR r5, [sp]
		LDR r3, [sp, #0x14]
		LDR r0, [r7, #0x2c]
		ADD r1, sp, #0xe8
		BL       |inc_0x0158_0x143f2| + 0x8d18
|loc_08021A18|
		LDR r7, [pc, #0x19c]
		LDR r0, [r7, #8]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x24]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_08021A30|
		LDR r0, [r4, #4]
		B        |loc_08021A32|
|loc_08021A30|
		LDR r0, [r4, #8]
|loc_08021A32|
		LDR r7, [pc, #0x180]
		STR r0, [r7, #0x14]
		LDR r0, [pc, #0x180]
		LDR r0, [r0, #8]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x24]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |sub_08021A4E|
		LDR r0, [r4, #8]
		DCW     0xE000
|sub_08021A4E|
	LDR      r0, [r4, #4]
	STR      r0, [r7, #0x18]
	LDR      r0, [pc, #0x164]
	LDR      r0, [r0, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x41a4
	LDR      r1, [pc, #0x184]
	LDR      r0, [r7, #0x14]
	BL       |inc_0x0158_0x143f2| + 0x10a60
	LDR      r1, [pc, #0x17c]
	LDR      r0, [r7, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x10a60
	LDR      r0, [r7, #0x14]
	BL       |inc_0x0158_0x143f2| + 0x104dc
	LDR      r0, [r7, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x104dc
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08021A8C|
	LDR      r1, [pc, #0x160]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #4]
	MOV      r1, #4
	STR      r1, [r0, #8]
|loc_08021A8C|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r7, [pc, #0x120]
	LDRB     r0, [r7]
	LDRB     r1, [r7, #1]
	ADD      r7, r0, r1
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08021AAC|
	ADD      r1, r7, #0
	ADD      r1, #0x6a
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x13c]
	STR      r1, [r0]
|loc_08021AAC|
	BL       |inc_0x03d784_0x041118| + 0x11c
	ADD      r2, r4, #4
	LDR      r7, [pc, #0x104]
	LDMIA    r2!, {r1, r2}
	LDR      r0, [r7, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x45ca
	MOV      r3, #0x64
	MOV      r2, #0
	MOV      r0, #0
	LDR      r1, [r4, #8]
	BL       |inc_0x153f2_0x1a3f2| + 0x41b6
	ADD      r1, r0, #0
	LDR      r0, [r7, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0xe0]
	LDRB     r0, [r1]
	LDRB     r1, [r1, #1]
	ADD      r7, r0, r1
	LDR      r1, [r4, #4]
	MOV      r0, #0x34
	STR      r1, [sp, #0xe0]
	LDR      r1, [r4, #8]
	STR      r1, [sp, #0xe4]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08021AF8|
	LDR      r1, [pc, #0x100]
	STR      r1, [r0]
	STR      r7, [r0, #0x10]
	LDR      r1, [sp, #0xe0]
	STR      r1, [r0, #8]
	LDR      r1, [sp, #0xe4]
	STR      r1, [r0, #0xc]
|loc_08021AF8|
	BL       |inc_0x03d784_0x041118| + 0x11c
	ADD      r7, r0, #0
	LDR      r0, [pc, #0xb8]
	LDR      r0, [r0, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x460c
	LDR      r0, [pc, #0xb0]
	MOV      r2, #0
	MOV      r1, #0x13
	LDR      r0, [r0, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	LDR      r0, [pc, #0xa4]
	MOV      r2, #0
	MOV      r1, #0xf
	LDR      r0, [r0, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x11ab4
	CMP      r7, #1
	BEQ      |sub_08021B4A|
	CMP      r7, #2
	BEQ      |loc_08021B54|
	CMP      r7, #3
	BEQ      |loc_08021B5C|
	CMP      r7, #0xff
	BNE      |loc_08021B5C|
	LDR      r7, [pc, #0x88]
	LDR      r0, [r7, #0x30]
	BL       |inc_0x03d784_0x041118| + 0x2a16
	BL       |inc_0x03d784_0x041118| + 0x29ca
	LDR      r1, [pc, #0xb4]
	LDR      r0, [r7, #4]
	ADD      r0, r0, r1
	BL       |inc_0x03d784_0x041118| + 0xb68
	MOV      r0, #2
	ADD      sp, #0xec
	POP      {r4, r5, r6, r7, pc}
|sub_08021B4A|
|unk_08021B4A|
		LDR r1, [pc, #0x68]
		LDRB r0, [r1, #1]
		ADD r0, #1
		STRB r0, [r1, #1]
		B        |loc_08021B5C|
|loc_08021B54|
|unk_08021B54|
		LDR r1, [pc, #0x5c]
		LDRB r0, [r1]
		ADD r0, #1
		STRB r0, [r1]
|loc_08021B5C|
|unk_08021B5C|
		MOV r0, #0xc
		DCW     0xF01B
		DCW     0xFD2B
		CMP r0, #0
		BEQ      |loc_08021B74|
		LDR r1, [pc, #0x8c]
		STR r1, [r0]
		MOV r1, #0xff
		ADD r1, #1
		STR r1, [r0, #4]
		MOV r1, #4
		STR r1, [r0, #8]
|loc_08021B74|
		BL       |inc_0x03d784_0x041118| + 0x11c
		LDR r0, [pc, #0x38]
		LDR r0, [r0, #0x14]
		BL       |inc_0x0158_0x143f2| + 0x1059e
		LDR r0, [pc, #0x30]
		LDR r0, [r0, #0x18]
		BL       |inc_0x0158_0x143f2| + 0x1059e
		LDR r0, [pc, #0x2c]
		LDR r0, [r0, #0xc]
		BL       |loc_08011B04|
		ADD r3, r7, #1
		BNE      |loc_08021B98|
		MOV r0, #1
		DCW     0xE7D6
|loc_08021B98|
		LDR r7, [pc, #0x1c]
		LDR r1, [pc, #0x18]
		LDR r0, [r7, #0x20]
		LDR r0, [r0, #4]
		LDRB r2, [r1]
		ASR r0, r0, #1
		CMP r0, r2
		BLT      |loc_08021BB0|
		LDRB r1, [r1, #1]
		CMP r0, r1
		BLT      |loc_08021BB0|
		B        |loc_08021950|
|loc_08021BB0|
		MOV r0, #1
		DCW     0xE7C8
	INCBIN  baserom.gba_0x21bb4_0x21bb6.extracted
|sub_08021BB6|
	LSL      r0, r0, #0xc
	ADD      r6, pc, #0x2D0
	LSR      r2, r6, #1
	LSL      r0, r0, #8
	LSL      r0, r0, #0x14
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0
	DCW      0xf000,0x0600
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	LSL      r0, r0, #1
	LSL      r0, r0, #0x10
	LDR      r2, [pc, #0x170]
	LSL      r0, r0, #0xc
	LDR      r2, [pc, #0x180]
	LSL      r0, r0, #0xc
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	ADD      r0, r0, #1
	LSL      r0, r0, #0xc
	STR      r5, [sp, #0x2d0]
	LSR      r4, r0, #0x20
	ADD      r0, sp, #0x2b0
	LSR      r4, r0, #0x20
	STR      r4, [sp, #0x90]
	LSR      r4, r0, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r6, [sp, #0x330]
	LSR      r4, r0, #0x20
|loc_08021BF8|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	BNE      |sub_08021C0C|
	MOV      r0, #4
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08021C0C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
|sub_08021C0C|
|unk_08021C0C|
		LDR r0, [pc, #0x2a0]
		LDR r5, [pc, #0x2a4]
		STR r0, [r4]
		LDR r0, [r5, #0x10]
		MOV r1, #1
		ADD r0, #0xff
		ADD r0, #0x81
		STRH r1, [r0, #0x10]
		STR r1, [r0, #0x14]
		MOV r1, #0
		STR r1, [r0, #0x18]
		LDR r0, [r5, #0x14]
		ADD r0, #0xff
		ADD r0, #0x91
		MOV r2, #4
		BL       |sub_08049168|
		LDR r0, [r5, #0x10]
		MOV r2, #4
		ADD r0, #0xff
		ADD r0, #0x9d
		MOV r1, #0
		BL       |sub_08049168|
		ADD r0, r4, #0
		DCW     0xE7E4
|sub_08021C40|
	PUSH     {r3, r4, r5, lr}
	MOV      r5, #0
	STR      r5, [r0, #0x2c]
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x26c]
	MOV      r1, #0xb4
	STR      r1, [r0, #4]
	MOV      r1, #0x3c
	STR      r1, [r4, #0x30]
	STR      r5, [r4, #0x18]
	STR      r5, [r0, #0xc]
	STR      r5, [r4, #0x20]
	STR      r5, [r0, #0x10]
	STR      r5, [r4, #0x28]
	MOV      r0, #0
	BL       |sub_0802e732|
	ADD      r1, r0, #0
	STR      r0, [r4, #0x1c]
	LDR      r0, [pc, #0x24c]
	LDR      r0, [r0, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r0, #0
	STR      r5, [r4, #0x24]
	BL       |loc_08021BF8|
	BL       |inc_0x03d784_0x041118| + 0x29dc
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_08021C8E|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08021C8E|
	BL       |inc_0x03d784_0x041118| + 0x29fe
	LDR      r1, [pc, #0x220]
	MOV      r0, #0
	LDR      r2, [r1, #0x10]
	STRH     r0, [r2, #2]
	LDR      r2, [r1, #0x10]
	STRH     r0, [r2, #4]
	LDR      r2, [r1, #0x10]
	STRH     r0, [r2, #6]
	LDR      r2, [r1, #0x10]
	ADD      r2, #0xff
	ADD      r2, #0x81
	STRH     r0, [r2, #0xc]
	LDR      r2, [r1, #0x14]
	STRH     r0, [r2, #2]
	LDR      r2, [r1, #0x14]
	STRH     r0, [r2, #4]
	LDR      r2, [r1, #0x14]
	STRH     r0, [r2, #6]
	LDR      r1, [r1, #0x14]
	ADD      r1, #0xff
	ADD      r1, #0x81
	STRH     r0, [r1, #0xc]
	POP      {r3, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x1f4]
	ADD      r4, r0, #0
	LDR      r0, [r7, #0xc]
	CMP      r0, #0
	BEQ      |sub_08021CD0|
	MOV      r0, #0xff
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08021CD0|
|unk_08021CD0|
; cited by 0x08021BD4 (a pc-relative load targets 0x08021D48)
		LDR r0, [r4, #0x18]
		LDR r6, [pc, #0x1e0]
		CMP r0, #0
		BEQ      |loc_08021CDE|
		LDR r0, [r4, #0x2c]
		CMP r0, #0
		BLE      |loc_08021DAC|
|loc_08021CDE|
		LDR r0, [r6, #0xc]
		BL       |sub_08011A1E|
		LDR r0, [r4, #8]
		MOV r2, #0x80
		LDR r1, [r0]
		MOV r5, #0
		LDR r2, [r2, r1]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		ADD r0, #0x16
		MOV r3, #0
		LDRSH r0, [r0, r3]
		CMP r0, #0
		BNE      |loc_08021D00|
		MOV r5, #1
|loc_08021D00|
		LDR r0, [r4, #0xc]
		MOV r2, #0x80
		LDR r1, [r0]
		LDR r2, [r2, r1]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		ADD r0, #0x16
		MOV r3, #0
		LDRSH r0, [r0, r3]
		CMP r0, #0
		BNE      |loc_08021D1C|
		MOV r0, #2
		ORR r5, r0
|loc_08021D1C|
		LDR r1, [r7, #4]
		CMP r1, #0
		BEQ      |loc_08021D3A|
		LDR r0, [r4, #0x30]
		SUB r0, #1
		STR r0, [r4, #0x30]
		BNE      |loc_08021D3A|
		MOV r0, #0x3c
		STR r0, [r4, #0x30]
		SUB r1, #1
		STR r1, [r7, #4]
		ORR r1, r5
		BNE      |loc_08021D3A|
		MOV r0, #1
		STR r0, [r7, #0x10]
|loc_08021D3A|
		MOV r1, #0xff
		LDR r0, [r4, #0x2c]
		ADD r1, #0x1d
		CMP r0, r1
		BLT      |loc_08021D48|
		MOV r0, #1
		STR r0, [r7, #0x10]
|loc_08021D48|
		LDR r0, [r7, #4]
		ORR r0, r5
		BNE      |loc_08021D52|
		MOV r5, #3
		B        |loc_08021D56|
|loc_08021D52|
		CMP r5, #0
		BEQ      |loc_08021DEA|
|loc_08021D56|
		LDR r0, [r4, #0x24]
		CMP r0, #0
		BNE      |loc_08021DC2|
		LDR r1, [pc, #0x154]
		ADD r1, #0x34
		CMP r5, #1
		BNE      |loc_08021D86|
		LDR r0, [r6, #0x20]
		LDR r0, [r0, #4]
		LDRB r2, [r7, #1]
		ASR r0, r0, #1
		ADD r2, #1
		CMP r0, r2
		BGE      |loc_08021D7C|
		MOV r0, #0x73
		BL       |sub_0802BFBC|
		STR r0, [r4, #0x24]
		B        |loc_08021DB6|
|loc_08021D7C|
		MOV r0, #0x70
		BL       |sub_0802BFBC|
		STR r0, [r4, #0x24]
		B        |loc_08021DB6|
|loc_08021D86|
		CMP r5, #2
		BNE      |loc_08021DAE|
		LDR r0, [r6, #0x20]
		LDR r0, [r0, #4]
		LDRB r2, [r7]
		ASR r0, r0, #1
		ADD r2, #1
		CMP r0, r2
		BGE      |loc_08021DA2|
		MOV r0, #0x72
		BL       |sub_0802BFBC|
		STR r0, [r4, #0x24]
		B        |loc_08021DB6|
|loc_08021DA2|
		MOV r0, #0x6f
		BL       |sub_0802BFBC|
		STR r0, [r4, #0x24]
		B        |loc_08021DB6|
|loc_08021DAC|
		B        |loc_08021E0A|
|loc_08021DAE|
		MOV r0, #0x71
		BL       |sub_0802BFBC|
		STR r0, [r4, #0x24]
|loc_08021DB6|
		LDR r1, [r4, #0x24]
		LDR r0, [r6, #0xc]
		BL       |sub_0801191A|
		MOV r0, #0x3c
		STR r0, [r4, #0x28]
|loc_08021DC2|
		LDR r0, [r4, #0x2c]
		MOV r1, #0xff
		ADD r0, #1
		ADD r1, #0x2d
		CMP r0, r1
		STR r0, [r4, #0x2c]
		BLT      |loc_08021DEE|
		LDR r1, [r4, #0x1c]
		LDR r0, [r6, #0xc]
		BL       |loc_08011944|
		LDR r0, [r4, #0x24]
		CMP r0, #0
		BEQ      |loc_08021DE6|
		ADD r1, r0, #0
		LDR r0, [r6, #0xc]
		BL       |loc_08011944|
|loc_08021DE6|
		ADD r0, r5, #0
		DCW     0xE771
|loc_08021DEA|
		MOV r0, #0
		STR r0, [r4, #0x2c]
|loc_08021DEE|
		LDR r0, [r4, #0x28]
		CMP r0, #0
		BEQ      |loc_08021DFA|
		SUB r0, #1
		STR r0, [r4, #0x28]
		B        |loc_08021E0A|
|loc_08021DFA|
		LDR r1, [r7, #0x14]
		LDR r0, [r6, #0x1c]
		BL       |loc_080126D4|
		LDR r1, [r7, #0x18]
		LDR r0, [r6, #0x1c]
		BL       |loc_080126D4|
|loc_08021E0A|
		LDR r0, [r4, #0x2c]
		CMP r0, #0
		DCW     0xD143
		LDR r0, [r6, #0x14]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1c
		LSR r1, r0, #0x1f
		BNE      |loc_08021E24|
		LDR r0, [r6, #0x10]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1c
		LSR r0, r0, #0x1f
		BEQ      |loc_08021EAA|
|loc_08021E24|
		LDR r0, [r4, #0x18]
		CMP r0, #0
		BNE      |loc_08021E50|
		MOV r1, #0
		STR r1, [r4, #0x20]
		LDR r1, [r6, #0x14]
		LDRH r1, [r1, #4]
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1f
		BEQ      |loc_08021E3C|
		MOV r1, #1
		STR r1, [r4, #0x20]
|loc_08021E3C|
		LDR r1, [r6, #0x10]
		LDRH r1, [r1, #4]
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1f
		BEQ      |loc_08021E6A|
		LDR r1, [r4, #0x20]
		MOV r2, #2
		ORR r1, r2
		STR r1, [r4, #0x20]
		B        |loc_08021E6A|
|loc_08021E50|
		CMP r1, #0
		BEQ      |loc_08021E5A|
		LDR r1, [r4, #0x20]
		LSL r1, r1, #0x1f
		BMI      |loc_08021E6A|
|loc_08021E5A|
		LDR r1, [r6, #0x10]
		LDRH r1, [r1, #4]
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1f
		BEQ      |loc_08021EAA|
		LDR r1, [r4, #0x20]
		LSL r1, r1, #0x1e
		BPL      |loc_08021EAA|
|loc_08021E6A|
		MOV r1, #1
		CMP r0, #0
		BEQ      |loc_08021E72|
		MOV r1, #0
|loc_08021E72|
		STR r1, [r4, #0x18]
		CMP r1, #0
		DCW     0xD00A
		LDR r1, [pc, #0x38]
		ADD r1, #0x3c
		MOV r0, #0x27
		BL       |sub_0802BFBC|
		ADD r1, r0, #0
		STR r0, [r4, #0x14]
		LDR r0, [r6, #0xc]
		BL       |sub_0801191A|
|loc_08021E8C|
|unk_08021E8C|
		B        |loc_08021EAA|
		LDR r1, [r4, #0x14]
		LDR r0, [r6, #0xc]
		BL       |loc_08011944|
		B        |loc_08021EAA|
		LDR r0, [r4, #0x18]
		CMP r0, #0
		BEQ      |loc_08021EAA|
		MOV r0, #0
		STR r0, [r4, #0x18]
		LDR r1, [r4, #0x14]
		LDR r0, [r6, #0xc]
		BL       |loc_08011944|
|loc_08021EAA|
		MOV r0, #0
		DCW     0xE70F
|sub_08021EAE|
	LSL      r0, r0, #0
	STR      r2, [sp, #0x350]
	LSR      r4, r0, #0x20
	ADD      r6, pc, #0x2D0
	LSR      r2, r6, #1
	CMP      r3, #0xfc
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x204]
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x10]
	MOV      r1, #0xff
	ADD      r1, #0x89
	LDR      r1, [r1, r0]
	LDR      r2, [r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r1, #0xff
	LDR      r0, [r4, #0x14]
	ADD      r1, #0x89
	LDR      r1, [r1, r0]
	LDR      r2, [r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6ee8
	POP      {r3, r4, r5, pc}
	MOV      r1, #0xff
	ADD      r1, #0x8d
	PUSH     {r3, lr}
	LDRH     r1, [r1, r0]
	BL       |inc_0x03d784_0x041118| + 0x2ab8
	POP      {r3, pc}
	MOV      r0, #0
	CMP      r1, #0
	BEQ      |loc_08021F08|
|loc_08021EFE|
	LSL      r2, r1, #0x1f
	BPL      |loc_08021F04|
	ADD      r0, #1
|loc_08021F04|
	LSR      r1, r1, #1
	BNE      |loc_08021EFE|
|loc_08021F08|
	BX       lr
|loc_08021F0A|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [pc, #0x1b8]
	LDR      r2, [r1]
	STR      r2, [sp]
	LDR      r6, [r1]
	MOV      r5, #0
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #0x81
	LDR      r7, [pc, #0x1a4]
	LDR      r0, [r7, #8]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x20]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_08021F40|
	LDR      r0, [r7, #8]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	B        |loc_08021F58|
|loc_08021F40|
	LDR      r1, [pc, #0x184]
	LDR      r0, [r1]
	CMP      r6, r0
	BEQ      |loc_08021F58|
	LDR      r6, [r1]
	LDR      r0, [r7, #8]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_08021F58|
	LDR      r1, [r4, #0x1c]
	LDR      r3, [pc, #0x16c]
	LDR      r0, [sp]
	LDR      r2, [r3]
	CMP      r0, r2
	BEQ      |loc_08021F82|
	LDR      r0, [r3]
	ADD      r5, #1
	CMP      r5, #0x3c
	STR      r0, [sp]
	BNE      |loc_08021F82|
	LDR      r0, [pc, #0x15c]
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |sub_08021F7E|
	MOV      r0, #0
	STRH     r0, [r4, #0xc]
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08021F7E|
|unk_08021F7E|
		MOV r0, #0
		DCW     0xE7FC
|loc_08021F82|
|unk_08021F82|
		LSL r0, r1, #0x1e
		LSR r0, r0, #0x1e
		CMP r0, #1
		DCW     0xD1C8
		LSL r0, r1, #1
		LSL r2, r1, #0x1c
		LSR r3, r2, #0x1e
		LSR r0, r0, #0x1e
		CMP r0, r3
		DCW     0xD1C2
		LSL r0, r1, #8
		LSR r0, r0, #8
		MOV r2, #0
		CMP r0, #0
		BEQ      |loc_08021FAA|
|loc_08021FA0|
		LSL r7, r0, #0x1f
		BPL      |loc_08021FA6|
		ADD r2, #1
|loc_08021FA6|
		LSR r0, r0, #1
		BNE      |loc_08021FA0|
|loc_08021FAA|
		LSL r0, r1, #3
		LSR r0, r0, #0x1b
		CMP r2, r0
		DCW     0xD1B4
		LDRH r0, [r4, #0x10]
		CMP r3, r0
		BNE      |loc_08021FC0|
		LSL r0, r1, #8
		LSR r0, r0, #0x16
		STRH r0, [r4, #0xc]
		B        |loc_08021FD0|
|loc_08021FC0|
		ADD r0, #1
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1e
		CMP r0, r3
		DCW     0xD1A8
		LSL r0, r1, #0x12
		LSR r0, r0, #0x16
		STRH r0, [r4, #0xc]
|loc_08021FD0|
		LDRH r0, [r4, #0x10]
		ADD r0, #1
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1e
		STRH r0, [r4, #0x10]
		MOV r0, #1
		DCW     0xE7CE
|sub_08021FDE|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #0x81
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x18]
	CMP      r0, #0
	BNE      |loc_080220AA|
	LDR      r0, [r4, #0x14]
	LDR      r7, [pc, #0xd8]
	CMP      r0, #0
	BNE      |sub_08022006|
	ADD      r0, r5, #0
	BL       |loc_08021F0A|
	CMP      r0, #0
	BNE      |sub_08022006|
	MOV      r1, #1
	STR      r1, [r7, #0xc]
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08022006|
|unk_08022006|
		LDR r6, [pc, #0xbc]
		LDR r3, [pc, #0xc4]
		LDR r0, [r6, #0x14]
		ADD r0, #0xff
		ADD r0, #0x81
		LDR r1, [r0, #0x10]
		LSL r2, r1, #8
		LSR r2, r2, #0x16
		STRH r2, [r0, #0xc]
		LSL r2, r2, #4
		AND r1, r3
		ORR r1, r2
		LDR r2, [r7, #0x10]
		LDR r3, [pc, #0xb0]
		CMP r2, #0
		BNE      |loc_08022034|
		LDR r2, [r6]
		AND r1, r3
		LDRH r2, [r2, #2]
		LSL r2, r2, #0x16
		LSR r2, r2, #8
		ORR r1, r2
		B        |loc_08022036|
|loc_08022034|
		AND r1, r3
|loc_08022036|
		LSR r1, r1, #2
		LSL r1, r1, #2
		ADD r1, #1
		ADD r3, r1, #0
		MOV r2, #0xc
		ADD r1, #4
		AND r1, r2
		BIC r3, r2
		ORR r1, r3
		ADD r3, r1, #0
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1e
		LSL r1, r1, #2
		BIC r3, r2
		ORR r1, r3
		LSL r3, r2, #0x1b
		ADD r2, r1, #0
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1e
		LSL r1, r1, #0x1d
		BIC r2, r3
		ORR r2, r1
		ADD r3, r2, #0
		LSL r1, r3, #8
		LSR r1, r1, #8
		MOV r2, #0
		CMP r1, #0
		BEQ      |loc_08022078|
|loc_0802206E|
		LSL r7, r1, #0x1f
		BPL      |loc_08022074|
		ADD r2, #1
|loc_08022074|
		LSR r1, r1, #1
		BNE      |loc_0802206E|
|loc_08022078|
		MOV r1, #0x1f
		LSL r1, r1, #0x18
		BIC r3, r1
		LSL r1, r2, #0x1b
		LSR r1, r1, #3
		ORR r1, r3
		STR r1, [r0, #0x10]
		LDR r0, [r6, #8]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x20]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_080220A6|
		LDR r0, [r6, #8]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x14]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
|loc_080220A6|
		MOV r0, #0
		STR r0, [r4, #0x14]
|loc_080220AA|
|unk_080220AA|
; cited by 0x08021EBE (a pc-relative load targets 0x080220C4)
		LDR r0, [r4, #0x18]
		MOV r1, #1
		CMP r0, #4
		BLT      |loc_080220B4|
		SUB r1, #5
|loc_080220B4|
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		LDRH r1, [r4, #0xc]
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0x2ab8
		DCW     0xE7A0
	INCBIN  baserom.gba_0x220c2_0x220d8.extracted
|sub_080220D8|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_080220F8|
	MOV      r0, #1
	LSL      r0, r0, #9
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080220F8|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_080220F8|
|unk_080220F8|
		LDR r0, [pc, #0x1dc]
		MOV r1, #0xff
		STR r0, [r4]
		MOV r0, #0
		STR r0, [r4, #0xc]
		ADD r1, #0xd1
		STR r6, [r1, r4]
		ADD r6, r4, #0
		ADD r5, r4, #0
		ADD r5, #0xc
		ADD r6, #0xff
		ADD r6, #0xd5
		STR r0, [r6]
		STR r7, [r4, #4]
		LDR r1, [sp, #8]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x607e
		LDR r7, [pc, #0x1c0]
		ADD r1, r0, #0
		STR r0, [r4, #8]
		LDR r0, [r7, #4]
		BL       |sub_0801191A|
		LDR r0, [r6]
		LDR r2, [r4, #8]
		ADD r1, r0, #1
		LSL r0, r0, #2
		ADD r0, r0, r6
		STR r1, [r6]
		STR r2, [r0, #4]
		ADD r2, r5, #0
		MOV r1, #0x19
		LDR r0, [r7, #4]
		BL       |loc_08011C0C|
		ADD r1, r5, #0
		LDR r0, [r7, #8]
		BL       |sub_08012846|
		ADD r0, r4, #0
		DCW     0xE7D4
		BX       lr
|sub_0802214C|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r5, #0xff
	ADD      r5, #0xd5
	ADD      r6, r0, #0
	LDR      r0, [r5]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08022174|
	LDR      r7, [pc, #0x17c]
|loc_08022160|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r1, [r0, #4]
	LDR      r0, [r7, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r0, [r5]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08022160|
|loc_08022174|
	ADD      r0, r6, #0
	BEQ      |loc_08022184|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08022184|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08022186|
|unk_08022186|
		PUSH {r4, r5, r6, r7, lr}
|loc_08022188|
|unk_08022188|
		ADD r4, r0, #0
		ADD r5, r4, #0
		ADD r5, #0xff
		LDR r0, [r0, #4]
		ADD r5, #0xd5
		CMP r0, #0
		SUB sp, #0x1c
		BEQ      |loc_0802227C|
		LDR r0, [r4, #8]
		ADD r2, sp, #0x14
		LDR r1, [r0, #0x2c]
		LDR r0, [r0, #0x30]
		STR r1, [sp, #0x14]
		STR r0, [sp, #0x18]
		LDR r3, [r4, #0xc]
		MOV r0, #0
		CMP r3, #0
		MOV ip, r3
		BLE      |loc_0802227C|
		ADD r6, r4, #0
		ADD r6, #0xc
		LDR r1, [r2]
		MOV lr, r6
|loc_080221B6|
|unk_080221B6|
		LSL r3, r0, #3
		SUB r3, r3, r0
		LSL r3, r3, #2
		ADD r3, lr
		ADD r3, #4
		LDR r6, [r3]
		CMP r1, r6
		BLT      |loc_0802228E|
		LDR r6, [r3, #8]
		CMP r1, r6
		BGE      |loc_0802228E|
		LDR r6, [r2, #4]
		LDR r7, [r3, #4]
		CMP r6, r7
		BLT      |loc_0802228E|
		LDR r7, [r3, #0xc]
		CMP r6, r7
		BGE      |loc_0802228E|
		LDR r6, [r3, #0x10]
		CMP r6, #0
		BNE      |loc_0802228E|
		MOV r0, #1
		STR r0, [r3, #0x10]
		MOV r0, #0xff
		ADD r0, #0xd1
		LDR r0, [r0, r4]
		LDR r2, [r0]
		ADD r6, r2, #1
		STR r6, [r0]
		LSL r2, r2, #3
		ADD r0, r2, r0
		LDR r1, [r3, #0x18]
		ADD r0, #4
		LDR r2, [r3, #0x14]
		STR r1, [r0, #4]
		STR r2, [r0]
		ADD r0, r3, #0
		LDR r2, [r3]
		LDR r6, [r3, #8]
		LDR r3, [r3, #4]
		ADD r0, #8
		LDR r0, [r0, #4]
		ADD r2, r2, r6
		STR r2, [sp, #4]
		ASR r2, r2, #1
		ADD r0, r3, r0
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x10]
		MOV r0, #0
		STR r2, [sp, #4]
		STR r2, [sp, #0xc]
		ADD r1, sp, #0xc
		BL       |loc_080222E0|
		ADD r6, r0, #0
		BL       |sub_08022368|
		LDR r7, [pc, #0xac]
		ADD r1, r6, #0
		LDR r0, [r7, #4]
		BL       |sub_0801191A|
		LDR r0, [r5]
		ADD r1, r0, #1
		LSL r0, r0, #2
		ADD r0, r0, r5
		STR r1, [r5]
		STR r6, [r0, #4]
		LDR r0, [r4, #4]
		SUB r0, #1
		STR r0, [r4, #4]
		BNE      |loc_0802227C|
		LDR r2, [r5]
		CMP r2, #0
		BLE      |loc_08022262|
		LDR r3, [r4, #8]
|loc_08022252|
		LSL r1, r0, #2
		ADD r1, r1, r5
		LDR r1, [r1, #4]
		CMP r1, r3
		BEQ      |loc_08022266|
		ADD r0, #1
		CMP r2, r0
		BGT      |loc_08022252|
|loc_08022262|
		MOV r0, #0
		MVN r0, r0
|loc_08022266|
		LDR r1, [r5]
		SUB r1, #1
		STR r1, [r5]
		SUB r1, r1, r0
		BEQ      |loc_08022284|
		LSL r0, r0, #2
		ADD r0, r0, r5
		LSL r2, r1, #2
		ADD r1, r0, #0
		ADD r1, #8
		B        |loc_0802227E|
|loc_0802227C|
		DCW     0xE00B
|loc_0802227E|
		ADD r0, #4
		BL       |sub_08049138|
|loc_08022284|
		LDR r1, [r4, #8]
		LDR r0, [r7, #4]
		BL       |loc_08011944|
		DCW     0xE003
|loc_0802228E|
		B        |sub_08022290|
|sub_08022290|
	ADD      r0, #1
	CMP      ip, r0
	BGT      |loc_080221B6|
	LDR      r0, [r5]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_080222B6|
|loc_0802229E|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r5]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_0802229E|
|loc_080222B6|
	LDR      r7, [pc, #0x24]
	LDR      r0, [r7, #4]
	BL       |inc_0x0158_0x143f2| + 0x11458
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x14]
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x11426
	LDR      r0, [r4]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x1e
	ASR      r0, r0, #0x1f
	ADD      r0, #1
	POP      {r4, pc}
	BCS      |loc_0802239C|
	LSR      r4, r0, #0x20
	ADD      r6, pc, #0x3E0
	LSR      r2, r6, #1
|loc_080222E0|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r4, r0, #0
	BNE      |sub_080222F8|
	MOV      r0, #0x3c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080222F8|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_080222F8|
|unk_080222F8|
		LDR r6, [pc, #0x304]
		LDR r7, [pc, #0x30c]
		LDRB r5, [r6]
		LDRB r0, [r6, #1]
		MUL r5, r0
		LDR r0, [pc, #0x300]
		ADD r1, r5, #0
		STR r0, [r4]
		STRH r5, [r4, #0xe]
		LDR r0, [r7, #4]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08022324|
		ADD r1, r5, #0
		LDR r0, [r7, #4]
		BL       |sub_08011732|
		ADD r1, r5, #0
		LDR r0, [r7, #4]
		BL       |loc_0801124C|
|loc_08022324|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LDR r1, [pc, #0x2e0]
		STRH r0, [r4, #0xc]
		STR r1, [r4]
		LDR r1, [pc, #0x2d0]
		MOV r2, #8
		SUB r1, #2
		STR r1, [r4, #0x28]
		STRB r2, [r4, #8]
		LDRB r2, [r6]
		LDRB r3, [r6, #1]
		LSL r0, r0, #5
		LDR r1, [r1, #8]
		MUL r2, r3
		LDR r3, [pc, #0x2cc]
		ADD r0, r0, r3
		BL       |sub_08049138|
		LDR r0, [pc, #0x2c8]
		STR r0, [r4]
		LDR r1, [sp, #8]
		LDR r0, [pc, #0x2c4]
		LDR r2, [r1]
		LDR r1, [r1, #4]
		STR r0, [r4]
		STR r1, [r4, #0x30]
		STR r2, [r4, #0x2c]
		LDR r0, [r4, #0x28]
		STR r0, [r4, #0x34]
		MOV r0, #0
		STR r0, [r4, #0x38]
		ADD r0, r4, #0
		DCW     0xE7C5
|sub_08022368|
	LDR      r1, [pc, #0x2b0]
	STR      r1, [r0, #0x34]
	BX       lr
	LDR      r1, [pc, #0x290]
	SUB      r1, #2
	STR      r1, [r0, #0x34]
	BX       lr
	LDR      r1, [pc, #0x2a8]
	STR      r1, [r0, #0x34]
	BX       lr
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x38]
	ADD      r1, #1
	STR      r1, [r0, #0x38]
	LSL      r1, r1, #0x1c
	LSR      r2, r1, #0x1e
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LDR      r1, [r0, #0x34]
	LSL      r2, r2, #2
	ADD      r1, r1, r2
	LDR      r2, [r0, #0x28]
	CMP      r2, r1
	BEQ      |loc_080223B0|
	STR      r1, [r0, #0x28]
	LDRB     r3, [r1, #2]
|loc_0802239C|
	LDRB     r4, [r1, #3]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r1, #8]
	MUL      r3, r4
	ADD      r2, r3, #0
	LDR      r3, [pc, #0x268]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080223B0|
	POP      {r4, pc}
	LDR      r2, [pc, #0x254]
	PUSH     {r4, r5, r6}
	LDR      r2, [r2, #8]
	LDR      r4, [r0, #0x2c]
	ADD      r2, #0x18
	LDR      r5, [r2]
	SUB      sp, #8
	SUB      r4, r4, r5
	LDR      r5, [r0, #0x30]
	LDR      r2, [r2, #4]
	STR      r4, [sp]
	SUB      r2, r5, r2
	STR      r2, [sp, #4]
	ADD      r2, r4, #0
	ADD      r3, r0, #0
	ADD      r3, #0x20
	LDR      r4, [sp, #4]
	STMIA    r3!, {r2, r4}
	LDR      r4, [r0, #0x28]
	MOV      r3, #0
	LDRSB    r5, [r4, r3]
	LDR      r2, [r0, #0x20]
	MOV      r3, #1
	SUB      r2, r2, r5
	STR      r2, [r0, #0x20]
	LDRSB    r5, [r4, r3]
	LDR      r2, [r0, #0x24]
	MOV      r6, #3
	SUB      r2, r2, r5
	STR      r2, [r0, #0x24]
	LDR      r2, [r1]
	LDR      r4, [r4, #4]
	LDR      r5, [pc, #0x230]
	STR      r4, [r2]
	LDR      r3, [r0, #0x20]
	AND      r4, r5
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r3, r4
	STR      r3, [r2]
	LDR      r4, [r0, #0x24]
	LSR      r3, r3, #8
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
	LSL      r3, r3, #8
	ORR      r3, r4
	STR      r3, [r2]
	LDRH     r3, [r0, #0xc]
	LDR      r4, [r2, #4]
	LSL      r6, r6, #0xa
	LSR      r4, r4, #0xa
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	LSL      r4, r4, #0xa
	ORR      r3, r4
	BIC      r3, r6
	STR      r3, [r2, #4]
	LDR      r3, [r0, #0x28]
	MOV      r4, #1
	LDR      r3, [r3, #4]
	LSL      r4, r4, #0x1d
	ORR      r3, r4
	ADD      r2, #8
	STR      r3, [r2]
	LDR      r4, [r0, #0x20]
	AND      r3, r5
	LSL      r4, r4, #0x17
	LSR      r4, r4, #7
	ORR      r3, r4
	STR      r3, [r2]
	LDR      r5, [r0, #0x28]
	LDR      r4, [r0, #0x24]
	LDRB     r5, [r5, #3]
	LSR      r3, r3, #8
	LSL      r3, r3, #8
	ADD      r4, r4, r5
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
	ORR      r3, r4
	STR      r3, [r2]
	LDRH     r0, [r0, #0xc]
	LDR      r3, [r2, #4]
	LSR      r3, r3, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r3, r3, #0xa
	ORR      r0, r3
	BIC      r0, r6
	STR      r0, [r2, #4]
	ADD      r2, #8
	STR      r2, [r1]
	ADD      sp, #8
	POP      {r4, r5, r6}
	MOV      r0, #0
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_08022488|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08022488|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08022488|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_080222E0|
	LDR      r0, [pc, #0x194]
	MOV      r1, #0
	STR      r0, [r4]
	LDR      r2, [r5]
	LDR      r5, [r5, #4]
	LSL      r2, r2, #8
	STR      r1, [r4, #0x44]
	LSL      r5, r5, #8
	STR      r2, [r4, #0x3c]
	ADD      r0, r4, #0
	ADD      r0, #0x44
	STR      r5, [r4, #0x40]
	STR      r1, [r4, #0x48]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x38]
	SUB      sp, #0x1c
	ADD      r0, #1
	STR      r0, [r4, #0x38]
	LSL      r0, r0, #0x1c
	LSR      r1, r0, #0x1e
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r0, [r4, #0x34]
	LSL      r1, r1, #2
	ADD      r1, r0, r1
	LDR      r0, [r4, #0x28]
	CMP      r0, r1
	BEQ      |loc_080224E4|
	STR      r1, [r4, #0x28]
	LDRB     r2, [r1, #2]
	LDRB     r0, [r1, #3]
	LDR      r3, [pc, #0x138]
	MUL      r2, r0
	LDRH     r0, [r4, #0xc]
	LDR      r1, [r1, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080224E4|
	LDR      r0, [r4, #0x44]
	LDR      r1, [r4, #0x48]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	ADD      r5, r4, #0
	ADD      r5, #0x44
	ADD      r6, r5, #4
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #8
	LSL      r0, r0, #8
	ASR      r0, r0, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #8]
	STR      r1, [sp, #0x10]
	LSL      r1, r0, #8
	STR      r0, [sp, #4]
	STR      r0, [sp, #0xc]
	MOV      r0, #1
	LSL      r0, r0, #0xa
	BL       |inc_0x046118_0x049114| + 0xd40
	ADD      r7, r0, #0
	LDR      r0, [sp, #0x10]
	LSL      r1, r0, #8
	MOV      r0, #1
	LSL      r0, r0, #0xa
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [sp, #8]
	LDR      r1, [sp, #8]
	STR      r7, [sp, #4]
	STR      r7, [sp, #0x14]
	STR      r1, [sp, #0x18]
	STR      r7, [r5]
	LDR      r0, [sp, #0x18]
	LDR      r1, [pc, #0xd8]
	STR      r0, [r6]
	LDR      r0, [r1]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1f
	BEQ      |loc_08022542|
	LDR      r0, [r4, #0x44]
	SUB      r0, #0xff
	SUB      r0, #1
	STR      r0, [r4, #0x44]
|loc_08022542|
	LDR      r0, [r1]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x1b
	LSR      r0, r0, #0x1f
	BEQ      |loc_08022554|
	LDR      r0, [r4, #0x44]
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r0, [r4, #0x44]
|loc_08022554|
	LDR      r0, [r1]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x19
	LSR      r0, r0, #0x1f
	BEQ      |loc_08022566|
	LDR      r0, [r4, #0x48]
	SUB      r0, #0xff
	SUB      r0, #1
	STR      r0, [r4, #0x48]
|loc_08022566|
	LDR      r0, [r1]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1f
	BEQ      |loc_08022578|
	LDR      r0, [r4, #0x48]
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r0, [r4, #0x48]
|loc_08022578|
	LDR      r0, [r1, #8]
	LDR      r7, [r5]
	ADD      r3, r0, #0
	ADD      r3, #0x18
	ADD      r3, r3, #4
	LDMIA    r3!, {r1, r2, r3}
	LDR      r0, [r0, #0x18]
	MOV      ip, r3
	LDR      r3, [r4, #0x3c]
	ADD      r3, r3, r7
	STR      r3, [r4, #0x3c]
	LDR      r3, [r4, #0x40]
	LDR      r6, [r6]
	ADD      r3, r3, r6
	STR      r3, [r4, #0x40]
	ADD      r3, r4, #0
	ADD      r3, #0x2c
	STR      r3, [sp, #0x18]
	LDR      r6, [r4, #0x3c]
	ADD      r3, #0x10
	MOV      lr, r3
	LDR      r3, [r4, #0x40]
	ASR      r6, r6, #8
	ASR      r3, r3, #8
	STR      r3, [sp, #0x14]
	LDR      r3, [sp, #0x18]
	LDR      r7, [sp, #0x14]
	STR      r6, [sp, #0x10]
	STMIA    r3!, {r6, r7}
	LDR      r6, [r4, #0x2c]
	MOV      r3, #0
	CMP      r6, r0
	BGE      |loc_080225C4|
	STR      r0, [r4, #0x2c]
	LSL      r0, r0, #8
	MOV      r6, lr
	STR      r0, [r6]
	STR      r3, [r5]
|loc_080225C4|
	LDR      r0, [r4, #0x2c]
	CMP      r0, r2
	BLE      |loc_080225D4|
	MOV      r6, lr
	LSL      r0, r2, #8
	STR      r2, [r4, #0x2c]
	STR      r0, [r6]
	STR      r3, [r5]
|loc_080225D4|
	ADD      r0, r4, #0
	ADD      r2, r4, #0
	LDR      r5, [r4, #0x30]
	ADD      r2, #0x40
	ADD      r0, #0x48
	CMP      r5, r1
	BGE      |loc_080225EA|
	STR      r1, [r4, #0x30]
	LSL      r1, r1, #8
	STR      r1, [r2]
	STR      r3, [r0]
|loc_080225EA|
	LDR      r1, [r4, #0x30]
	CMP      r1, ip
	BLE      |loc_080225FA|
	MOV      r5, ip
	LSL      r1, r5, #8
	STR      r5, [r4, #0x30]
	STR      r1, [r2]
	STR      r3, [r0]
|loc_080225FA|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|sub_080225FE|
	DCW      0x0000
	DCW      0xbf06,0x0872,0x9680,0x0804,0xbf94,0x0872,0xba50,0x0804
	DCW      0x0000,0x0601,0xca80,0x0804,0xe120,0x0804,0xbf34,0x0872
	DCW      0xbf64,0x0872,0xffff
|sub_08022626|
|unk_08022626|
	INCBIN	baserom.gba_0x22626_0x2262a.extracted
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	LDR      r1, [r2]
	ADD      r0, r2, #0
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	LSR      r0, r0, #0x1f
	POP      {r3, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x2c]
	ADD      r4, r1, #0
	LDR      r6, [r7]
	ADD      r1, r2, #0
	LDR      r2, [r4]
	ADD      r6, #0xc0
	LDR      r5, [r6, #8]
	LDR      r3, [r2, #4]
	ADD      r0, r4, #0
	ADD      r3, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r0, [r6, #8]
	CMP      r0, r5
	BNE      |loc_0802266C|
	ADD      r1, r4, #0
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x12532
|loc_0802266C|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0802266E|
|unk_0802266E|
	INCBIN	baserom.gba_0x2266e_0x22672.extracted
|sub_08022672|
	LSL      r0, r0, #0
|unk_08022674|
	INCBIN	baserom.gba_0x22674_0x22676.extracted
	LSR      r2, r6, #1
	CMP      r7, #0x4c
	LSL      r0, r0, #0xc
	SUB      sp, #4
	MOV      r2, #0xff
	ADD      r2, #0x15
	ADD      r3, sp, #0
	LDRH     r3, [r3]
	LDRB     r2, [r2, r0]
	ADD      r0, #0xff
	LSR      r3, r3, #3
	LSL      r2, r2, #0x1d
	LSR      r2, r2, #0x1d
	LSL      r3, r3, #3
	ORR      r2, r3
	ADD      r3, sp, #0
	STRH     r2, [r3]
	ADD      r0, #1
	LDR      r0, [r0, #0x18]
	MOV      r3, #0xff
	LSL      r3, r3, #3
	BIC      r2, r3
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x15
	ORR      r0, r2
	MOV      r2, #1
	LSL      r2, r2, #0xb
	ADD      r3, sp, #0
	STRH     r0, [r3]
	LSL      r1, r1, #0x1f
	LSR      r1, r1, #0x14
	BIC      r0, r2
	ORR      r0, r1
	STRH     r0, [r3]
	LDRH     r0, [r3]
	ADD      sp, #4
	BX       lr
|sub_080226C0|
|unk_080226C0|
		PUSH {r0, r1, r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		ADD r4, #0xff
		ADD r4, #1
		ADD r6, r0, #0
		LDR r0, [r4, #0x1c]
		SUB sp, #0xc
		CMP r0, #0
		BNE      |loc_080226E2|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x18]
		ADD r2, r2, r1
		ADD r1, r6, #4
		BL       |loc_08046AA4|
		STR r0, [r4, #0x20]
|loc_080226E2|
		MOV r5, #2
		LDR r7, [pc, #0x214]
		B        |loc_08022702|
|loc_080226E8|
		LDR r0, [r4, #0x1c]
		LDR r1, [r4, #0x20]
		CMP r0, r1
		BHS      |loc_080226FA|
		ADD r1, r0, #1
		STR r1, [r4, #0x1c]
		ADD r0, r0, r6
		LDRB r0, [r0, #4]
		B        |loc_080226FC|
|loc_080226FA|
		MOV r0, #0
|loc_080226FC|
		ADD r1, sp, #8
		STRB r0, [r1, r5]
		ADD r5, #1
|loc_08022702|
		LDR r0, [r7]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x1c]
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		CMP r0, r5
		BGT      |loc_080226E8|
		LDR r0, [r4, #0x1c]
		LDR r1, [r4, #0x20]
		CMP r0, r1
		BNE      |sub_08022720|
		MOV r0, #1
		DCW     0xE000
|sub_08022720|
	MOV      r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x11
	ADD      r3, sp, #0
	LDRH     r2, [r3, #4]
	LDRB     r1, [r6, #4]
	LSL      r0, r0, #0x1f
	LSR      r2, r2, #3
	LSL      r1, r1, #0x1d
	LSR      r1, r1, #0x1d
	LSL      r2, r2, #3
	ORR      r1, r2
	STRH     r1, [r3, #4]
	LDRH     r2, [r3, #4]
	MOV      r3, #0xff
	LDR      r1, [r4, #0x18]
	LSL      r3, r3, #3
	BIC      r2, r3
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x15
	ORR      r1, r2
	MOV      r2, #1
	ADD      r3, sp, #0
	STRH     r1, [r3, #4]
	LSL      r2, r2, #0xb
	BIC      r1, r2
	LSR      r0, r0, #0x14
	ORR      r0, r1
	STRH     r0, [r3, #4]
	STRH     r0, [r3, #8]
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x10]
	STR      r0, [r1]
	LDR      r0, [r4, #0x18]
	ADD      r0, #1
	STR      r0, [r4, #0x18]
	LDR      r0, [r4, #0x1c]
	LDR      r1, [r4, #0x20]
	CMP      r0, r1
	BNE      |loc_08022776|
	MOV      r0, #0
	STR      r0, [r4, #0x1c]
	STR      r0, [r4, #0x18]
|loc_08022776|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0x1c
	STR      r0, [sp, #8]
	ADD      r3, sp, #0
	LDRH     r0, [r3, #8]
	ADD      r1, r6, #0
	ADD      r1, #0xff
	STRH     r0, [r3, #0xc]
	ADD      r2, r6, #0
	ADD      r2, #0xff
	ADD      r1, #0x21
	STR      r1, [sp, #0x18]
	ADD      r2, #5
	LDRB     r1, [r1, #8]
	STR      r2, [sp, #0x14]
	SUB      r7, r2, #4
	SUB      r2, #0x80
	LSL      r0, r0, #0x1d
	LSR      r0, r0, #0x1d
	CMP      r0, r1
	STR      r2, [sp, #0x10]
	BEQ      |loc_080227D0|
	MOV      r2, #0x80
	MOV      r1, #0
	MVN      r1, r1
	LDR      r0, [sp, #0x10]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	LDR      r0, [sp, #0x14]
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0x13c]
	ADD      r3, sp, #0
	STR      r0, [r7, #0x24]
	LDRH     r0, [r3, #0xc]
	LDR      r1, [sp, #0x18]
	LSL      r0, r0, #0x1d
	LSR      r0, r0, #0x1d
	STRB     r0, [r1, #8]
|loc_080227D0|
	LDR      r5, [pc, #0x128]
	LDR      r0, [r5]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r3, sp, #0
	LDRH     r1, [r3, #0xc]
	SUB      r0, #2
	LSL      r1, r1, #0x15
	LSR      r1, r1, #0x18
	MUL      r0, r1
	ADD      r4, r0, #0
	LDR      r0, [r5]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r0, r0, r4
	CMP      r0, #0x80
	BLT      |sub_08022820|
	MOV      r2, #0x80
	MOV      r1, #0
	MVN      r1, r1
	LDR      r0, [sp, #0x10]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	LDR      r0, [sp, #0x14]
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0xe4]
	STR      r0, [r7, #0x24]
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|sub_08022820|
|unk_08022820|
; cited by 0x080226E4 (a pc-relative load targets 0x080228FC)
		MOV r5, #2
		B        |loc_0802284A|
|loc_08022824|
		ASR r0, r4, #3
		ADD r0, r0, r6
		ADD r0, #0xff
		ADD r0, #1
		LSL r3, r4, #0x1d
		LSR r3, r3, #0x1d
		LDRB r1, [r0, #4]
		MOV r2, #2
		LSL r2, r3
		ORR r1, r2
		STRB r1, [r0, #4]
		ADD r0, sp, #8
		LDRB r1, [r0, r5]
		ADD r0, r4, #0
		ADD r0, r0, r6
		ADD r0, #0x80
		ADD r4, #1
		ADD r5, #1
		STRB r1, [r0, #4]
|loc_0802284A|
		LDR r0, [pc, #0xb0]
		LDR r0, [r0]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x1c]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, r5
		BGT      |loc_08022824|
		ADD r3, sp, #0
		LDRH r0, [r3, #0xc]
		LSL r0, r0, #0x14
		BPL      |loc_08022870|
		LDRH r0, [r3, #0xc]
		LSL r0, r0, #0x15
		LSR r0, r0, #0x18
		ADD r0, #1
		STR r0, [r7, #0x24]
|loc_08022870|
		LDR r1, [pc, #0x8c]
		LDR r0, [r7, #0x24]
		CMP r0, r1
		DCW     0xD0D1
		MOV r4, #0
		STR r4, [sp, #4]
		CMP r0, #0
		BLS      |loc_080228CC|
|loc_08022880|
		MOV r0, #0
		STR r0, [sp]
		MOV r5, #2
		B        |loc_080228A6|
|loc_08022888|
		ASR r0, r4, #3
		ADD r0, r0, r6
		ADD r0, #0xff
		ADD r0, #1
		LSL r2, r4, #0x1d
		LSR r2, r2, #0x1d
		LDRB r0, [r0, #4]
		MOV r1, #2
		LSL r1, r2
		AND r0, r1
		BEQ      |loc_080228A2|
		MOV r0, #1
		STR r0, [sp]
|loc_080228A2|
		ADD r4, #1
		ADD r5, #1
|loc_080228A6|
		LDR r0, [pc, #0x54]
		LDR r0, [r0]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x1c]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, r5
		BGT      |loc_08022888|
		LDR r0, [sp]
		CMP r0, #0
		DCW     0xD0AD
		LDR r1, [sp, #4]
		ADD r1, #1
		STR r1, [sp, #4]
		LDR r0, [r7, #0x24]
		CMP r0, r1
		BHI      |loc_08022880|
|loc_080228CC|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x1c]
		ADD r3, r2, r1
		LDR r1, [sp, #0x18]
		LDRB r2, [r1, #8]
		LDR r1, [sp, #0x10]
		BL       |inc_0x046118_0x049114| + 0x98e
		MOV r2, #0x80
		MOV r1, #0
		MVN r1, r1
		LDR r0, [sp, #0x10]
		BL       |sub_0804912C|
		MOV r2, #0x10
		MOV r1, #0
		LDR r0, [sp, #0x14]
		BL       |sub_0804912C|
		LDR r1, [pc, #8]
		STR r1, [r7, #0x24]
		DCW     0xE790
	INCBIN  baserom.gba_0x228fa_0x228fc.extracted
		DCD     0x0872BFA4
	INCBIN  baserom.gba_0x22900_0x22902.extracted
|sub_08022902|
	LSL      r0, r0, #0
	MOV      r3, #0
	STRB     r3, [r1]
	LDR      r2, [r0, #4]
	STRH     r2, [r1, #2]
	LDR      r2, [r0, #8]
	STRH     r2, [r1, #4]
	LDR      r2, [r0, #0xc]
	STRB     r2, [r1, #6]
	LDR      r2, [r0, #0x10]
	STRB     r2, [r1, #7]
	LDR      r2, [r0, #0x14]
	STRB     r2, [r1, #8]
	LDR      r2, [r0, #0x18]
	STRB     r2, [r1, #9]
	MOV      r2, #0x2d
	STRB     r2, [r1, #0xa]
	MOV      r2, #1
	STRB     r2, [r1, #0xb]
	MOV      r2, #7
	STRB     r2, [r1, #0xc]
	STRB     r3, [r1, #0xd]
	LDRH     r0, [r0]
	STR      r0, [r1, #0x14]
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	BL       |inc_0x0158_0x143f2| + 0x1347a
	STRB     r0, [r5]
	LDRB     r0, [r4, #0xc]
	STRB     r0, [r5, #1]
	LDRB     r0, [r4, #0x15]
	STRB     r0, [r5, #2]
	MOV      r0, #0
|loc_0802294C|
	ADD      r1, r4, r0
	LDRB     r2, [r1, #0xd]
	ADD      r1, r5, r0
	STRB     r2, [r1, #3]
	LSL      r2, r0, #1
	ADD      r2, r2, r4
	ADD      r2, #0x2e
	LDRB     r2, [r2]
	ADD      r0, #1
	CMP      r0, #6
	STRB     r2, [r1, #9]
	BLT      |loc_0802294C|
	LDRB     r0, [r4, #0x14]
	STRB     r0, [r5, #0xf]
	ADD      r0, r4, #0
	ADD      r0, #0x18
	LDRH     r0, [r0]
	STRH     r0, [r5, #0x10]
	ADD      r0, r4, #0
	ADD      r0, #0x1c
	LDRH     r0, [r0]
	STRH     r0, [r5, #0x12]
	ADD      r0, r4, #0
	ADD      r0, #0x28
	LDRB     r0, [r0]
	STRB     r0, [r5, #0x14]
	ADD      r0, r4, #0
	ADD      r0, #0x29
	LDRB     r0, [r0]
	STRB     r0, [r5, #0x15]
	ADD      r0, r4, #0
	ADD      r0, #0x2a
	LDRB     r0, [r0]
	STRB     r0, [r5, #0x16]
	ADD      r0, r4, #0
	ADD      r0, #0x2b
	LDRB     r0, [r0]
	STRB     r0, [r5, #0x17]
	MOV      r0, #0
|loc_0802299A|
	LSL      r1, r0, #2
	ADD      r1, r1, r4
	ADD      r1, #0x3c
	LDR      r1, [r1]
	LSL      r2, r0, #1
	ADD      r2, r2, r5
	ADD      r0, #1
	CMP      r0, #4
	STRH     r1, [r2, #0x18]
	BLT      |loc_0802299A|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x68
	ADD      r5, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0xba4
	MOV      r0, #2
	STRB     r0, [r4]
	SUB      r0, #3
	STR      r0, [r4, #8]
	ADD      r6, r4, #0
	ADD      r6, #0x24
	LDRB     r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x13220
|loc_080229D0|
	STR      r0, [r6]
	LDR      r1, [r6]
	CMP      r1, r0
	BNE      |loc_080229D0|
	LDRB     r0, [r5, #1]
	MOV      r1, #0
	STRB     r0, [r4, #0xc]
	LDRB     r0, [r5, #2]
	STRB     r0, [r4, #0x15]
|loc_080229E2|
	ADD      r2, r5, r1
	LDRB     r0, [r2, #3]
	ADD      r3, r4, r1
	STRB     r0, [r3, #0xd]
	LSL      r0, r1, #1
	LDRB     r2, [r2, #9]
	ADD      r0, r0, r4
	ADD      r0, #0x2e
	ADD      r6, r2, #0
|loc_080229F4|
	STRB     r2, [r0]
	LDRB     r3, [r0]
	CMP      r3, r2
	BNE      |loc_080229F4|
|loc_080229FC|
	STRB     r6, [r0, #1]
	LDRB     r2, [r0, #1]
	CMP      r2, r6
	BNE      |loc_080229FC|
	ADD      r1, #1
	CMP      r1, #6
	BLT      |loc_080229E2|
	MOV      r3, #0x10
	LDRSH    r6, [r5, r3]
	ADD      r0, r4, #0
	ADD      r0, #0x16
	ADD      r1, r6, #0
|loc_08022A14|
	STRH     r1, [r0]
	MOV      r3, #0
	LDRSH    r2, [r0, r3]
	CMP      r2, r1
	BNE      |loc_08022A14|
	LSL      r1, r6, #0x10
	ASR      r1, r1, #0x10
|loc_08022A22|
	STRH     r1, [r0, #2]
	MOV      r3, #2
	LDRSH    r2, [r0, r3]
	CMP      r2, r1
	BNE      |loc_08022A22|
	MOV      r3, #0x12
	LDRSH    r6, [r5, r3]
	ADD      r0, r4, #0
	ADD      r0, #0x1a
	ADD      r1, r6, #0
|loc_08022A36|
	STRH     r1, [r0]
	MOV      r3, #0
	LDRSH    r2, [r0, r3]
	CMP      r2, r1
	BNE      |loc_08022A36|
	LSL      r1, r6, #0x10
	ASR      r1, r1, #0x10
|loc_08022A44|
	STRH     r1, [r0, #2]
	MOV      r3, #2
	LDRSH    r2, [r0, r3]
	CMP      r2, r1
	BNE      |loc_08022A44|
	LDRB     r1, [r5, #0x14]
	ADD      r0, r4, #0
	ADD      r0, #0x28
|loc_08022A54|
	STRB     r1, [r0]
	LDRB     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08022A54|
	LDRB     r1, [r5, #0x15]
	ADD      r0, r4, #0
	ADD      r0, #0x29
|loc_08022A62|
	STRB     r1, [r0]
	LDRB     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08022A62|
	LDRB     r1, [r5, #0x16]
	ADD      r0, r4, #0
	ADD      r0, #0x2a
|loc_08022A70|
	STRB     r1, [r0]
	LDRB     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08022A70|
	LDRB     r1, [r5, #0x17]
	ADD      r0, r4, #0
	ADD      r0, #0x2b
|loc_08022A7E|
	STRB     r1, [r0]
	LDRB     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08022A7E|
	LDRB     r0, [r5, #0xf]
	STRB     r0, [r4, #0x14]
	MOV      r0, #0
|loc_08022A8C|
	LSL      r1, r0, #2
	ADD      r1, r1, r4
	ADD      r1, #0x3c
	LSL      r2, r0, #1
	ADD      r2, r2, r5
	MOV      r3, #0x18
	LDRSH    r2, [r2, r3]
|loc_08022A9A|
	STR      r2, [r1]
	LDR      r3, [r1]
	CMP      r3, r2
	BNE      |loc_08022A9A|
	ADD      r0, #1
	CMP      r0, #4
	BLT      |loc_08022A8C|
	LDRB     r0, [r4, #0x14]
	LDR      r1, [pc, #0x288]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0]
	LSL      r0, r0, #0x1e
	LSR      r2, r0, #0x1f
	ADD      r0, r4, #0
	ADD      r0, #0x1c
	CMP      r2, #0
	BEQ      |loc_08022AD2|
	LDRH     r3, [r0]
	ADD      r2, r0, #4
	LSL      r3, r3, #0x10
	LSR      r3, r3, #0x10
|loc_08022ACA|
	STRH     r3, [r2]
	LDRH     r5, [r2]
	CMP      r5, r3
	BNE      |loc_08022ACA|
|loc_08022AD2|
	LDRB     r2, [r4, #0x14]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LSL      r2, r2, #3
	ADD      r1, r2, r1
	LDRB     r1, [r1]
	LSL      r1, r1, #0x1f
	BEQ      |loc_08022AF4|
	LDRH     r0, [r0]
	ADD      r1, r4, #0
	ADD      r1, #0x1e
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
|loc_08022AEC|
	STRH     r0, [r1]
	LDRH     r2, [r1]
	CMP      r2, r0
	BNE      |loc_08022AEC|
|loc_08022AF4|
	POP      {r4, r5, r6, pc}
|loc_08022AF6|
	PUSH     {r4, r5, lr}
	LDR      r4, [pc, #0x23c]
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x1c]
	SUB      sp, #0x14
	BL       |inc_0x0158_0x143f2| + 0x119ac
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11458
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11426
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x224]
	LDR      r0, [pc, #0x228]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x220]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x15
	LSL      r2, r2, #7
	MOV      r1, #0
	LDR      r0, [pc, #0x218]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0xc
	STR      r0, [sp, #4]
	MOV      r0, #9
	STR      r0, [sp, #8]
	MOV      r0, #0x12
	STR      r0, [sp, #0xc]
	MOV      r0, #0x10
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	LDR      r2, [pc, #0x204]
	LDR      r1, [pc, #0x1f8]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0x200]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #0xa]
	ADD      r1, #0xfd
	STRH     r1, [r0, #8]
	MOV      r1, #0x4d
	LSL      r1, r1, #6
	STRH     r1, [r0]
	MOV      r0, #1
	ADD      r5, #0xff
	ADD      r5, #0x41
	STRB     r0, [r5]
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1e4]
	LDR      r5, [pc, #0x1c4]
	SUB      sp, #0x14
	LDR      r2, [pc, #0x1dc]
	ADD      r0, r4, r0
	LDR      r1, [r5, #0xc]
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [r5, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x41a4
	MOV      r0, #0xff
	LDR      r7, [pc, #0x1d0]
	ADD      r0, #0xa1
	LDR      r3, [r7, r0]
	LDR      r2, [r5, #8]
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r3, [sp]
	MOV      r0, #0x75
	STR      r2, [sp, #0xc]
	MOV      r2, #0x78
	STR      r0, [sp, #4]
	MOV      r3, #0x26
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0xff
	ADD      r0, #0xa5
	LDR      r3, [r7, r0]
	LDR      r2, [r5, #8]
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r3, [sp]
	MOV      r0, #0x75
	STR      r2, [sp, #0xc]
	MOV      r2, #0x78
	STR      r0, [sp, #4]
	MOV      r3, #0x82
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r0, [r7, #0x68]
	LDR      r6, [r7, #0x5c]
	STR      r0, [sp, #0x10]
	LDR      r0, [r5, #8]
	ADD      r1, r6, #0
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
	LDR      r2, [r5, #8]
	STR      r6, [sp]
	MOV      r6, #0x90
	MOV      r1, #0
	STR      r1, [sp, #8]
	ADD      r3, r6, #0
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
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
	LDR      r2, [r5, #8]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	LDR      r2, [sp, #0x10]
	STR      r1, [sp, #8]
	STR      r2, [sp]
	ADD      r2, r7, #0
	ADD      r2, #0x10
	MOV      r0, #5
	ADD      r3, r6, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	STR      r2, [sp, #0xc]
	MOV      r2, #0x56
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #4
	STR      r0, [sp, #4]
	MOV      r2, #4
	ADD      r1, r4, #0
	MOV      r3, #0xb
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r6, r4, #0
	ADD      r6, #0xff
	ADD      r6, #1
	STR      r0, [r6, #0x14]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	STR      r2, [sp, #0xc]
	MOV      r2, #0x56
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #5
	STR      r0, [sp, #4]
	MOV      r2, #5
	ADD      r1, r4, #0
	MOV      r3, #0xd6
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	STR      r0, [r6, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r0, r4, #0
	BL       |loc_08022AF6|
	MOV      r0, #0
	STR      r0, [r6, #0x1c]
	STR      r0, [r6, #0x28]
	LDR      r0, [r5, #0x10]
	LDRB     r0, [r0]
	CMP      r0, #0
	BNE      |loc_08022D24|
	LDR      r0, [pc, #0x80]
	MOV      r5, #0
	ADD      r7, r4, r0
|loc_08022CE4|
	MOV      r0, #0x68
	MUL      r0, r5
	LDR      r1, [pc, #0x78]
	ADD      r0, r0, r4
	ADD      r0, r0, r1
	LDRB     r1, [r0]
	LSL      r2, r1, #0x1f
	BEQ      |loc_08022D1E|
	LSL      r1, r1, #0x1e
	LSR      r1, r1, #0x1f
	BEQ      |loc_08022D1E|
	LDR      r1, [r7]
	ADD      r2, r1, #1
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #2
	ADD      r6, r1, r7
	ADD      r6, #4
	STR      r2, [r7]
	STR      r5, [r6, #8]
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x24]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	STR      r0, [r6]
|loc_08022D1E|
	ADD      r5, #1
	CMP      r5, #9
	BLT      |loc_08022CE4|
|loc_08022D24|
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7500
	BL       |inc_0x03d784_0x041118| + 0x29dc
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_08022D32|
	DCW      0x0000
	DCW      0x82ec,0x086b,0xbfa8,0x0872,0x652c,0x0805,0x0200,0x0500
	DCW      0xf800
|sub_08022D46|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	LSR      r0, r5, #2
	LSL      r0, r0, #0
	LSL      r4, r6, #0x17
	LSL      r0, r0, #0
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	LSL      r4, r0, #0x16
	LSL      r0, r0, #0
	LSR      r4, r5, #0xb
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	MOV      r2, #1
	LSL      r2, r2, #0x1a
	ADD      r4, r0, #0
	LDRH     r0, [r2]
	LSR      r1, r2, #0x12
	LDR      r5, [pc, #0x310]
	BIC      r0, r1
	STRH     r0, [r2]
	LDR      r0, [r5, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x119ac
	LDR      r0, [r5, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11458
	LDR      r0, [r5, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11426
	LDR      r0, [pc, #0x300]
	LDR      r2, [pc, #0x2fc]
	ADD      r1, r4, r0
	LDR      r0, [r5, #0xc]
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r0, r4, #0
	BEQ      |loc_08022DA8|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08022DA8|
	POP      {r3, r4, r5, pc}
|loc_08022DAA|
	LDR      r2, [pc, #0x2dc]
	PUSH     {r4, lr}
	LDR      r2, [r2, #0x10]
	LDR      r4, [pc, #0x2e0]
	LDRB     r2, [r2]
	CMP      r2, #0
	BEQ      |loc_08022DD8|
	CMP      r2, #1
	BNE      |sub_08022DF0|
	LSL      r0, r1, #3
	SUB      r0, r0, r1
	LDR      r1, [pc, #0x2c4]
	LSL      r0, r0, #2
	ADD      r1, #0x24
	LDRH     r0, [r1, r0]
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	ADD      r2, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xea08
	POP      {r4, pc}
|loc_08022DD8|
	LDR      r2, [pc, #0x2bc]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #2
	ADD      r0, r0, r2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	ADD      r2, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xea08
	POP      {r4, pc}
|sub_08022DF0|
|unk_08022DF0|
		MOV r0, #0
		POP {r4, pc}
|sub_08022DF4|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x290]
	ADD      r5, r0, #0
	LDR      r1, [r6, #0x10]
	MOV      r0, #0x20
	LDRB     r1, [r1]
	SUB      sp, #0xc
	CMP      r1, #1
	BEQ      |loc_08022E0C|
	LDR      r0, [pc, #0x290]
	ADD      r0, r5, r0
	LDR      r0, [r0]
|loc_08022E0C|
	STR      r0, [sp]
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #0x41
	STR      r0, [sp, #8]
	LDRB     r0, [r0]
	ADD      r4, r5, #0
	ADD      r4, #0xff
	ADD      r4, #1
	CMP      r0, #0
	BEQ      |sub_08022E8C|
	CMP      r0, #1
	BEQ      |loc_08022EF2|
	CMP      r0, #2
	BEQ      |loc_08022EF4|
	CMP      r0, #3
	BNE      |loc_08022EAC|
	LDR      r0, [r4, #0x3c]
	CMP      r0, #0
	BEQ      |loc_08022E3C|
	ADD      r1, r0, #0
	LDR      r0, [r6, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08022E3C|
	LDR      r0, [r4, #0x38]
	STR      r0, [r4, #0x3c]
	LDR      r0, [r4, #0x34]
	STR      r0, [r4, #0x38]
	LDR      r0, [r4, #0x30]
	STR      r0, [r4, #0x34]
	LDR      r1, [r4, #0x2c]
	STR      r1, [r4, #0x30]
	MOV      r1, #0
	STR      r1, [r4, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #0x38]
	CMP      r0, #0
	BEQ      |loc_08022E6E|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08022E6E|
	LDR      r0, [r4, #0x1c]
	CMP      r0, #2
	BMI      |loc_08022E86|
	SUB      r1, r0, #2
	ADD      r0, r5, #0
	BL       |loc_08022DAA|
	ADD      r1, r0, #0
	STR      r0, [r4, #0x2c]
	LDR      r0, [r6, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08022E86|
	MOV      r0, #0
	MOV      r6, #0x6a
	B        |sub_0802304E|
|sub_08022E8C|
|unk_08022E8C|
		LDR r0, [r4, #0x34]
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		CMP r0, #0
		DCW     0xD107
		LDR r0, [r4, #0x34]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
|loc_08022EAC|
|unk_08022EAC|
		DCW     0xE086
		LDR r0, [r4, #0x30]
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_08022ED0|
		LDR r0, [r4, #0x30]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		B        |loc_08022FBC|
|loc_08022ED0|
		LDR r0, [r4, #0x38]
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		DCW     0xD109
		LDR r0, [r4, #0x38]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		B        |loc_08022FBC|
|loc_08022EF2|
|unk_08022EF2|
		DCW     0xE022
|loc_08022EF4|
|unk_08022EF4|
		B        |loc_08022FBE|
		LDR r0, [r4, #0x2c]
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_08022F18|
		LDR r0, [r4, #0x2c]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		B        |loc_08022FBC|
|loc_08022F18|
		LDR r0, [r4, #0x3c]
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_08022FBC|
		LDR r0, [r4, #0x3c]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		B        |loc_08022FBC|
		LDR r7, [r4, #0x1c]
		LDR r6, [pc, #0x148]
		SUB r7, #2
		LDR r0, [r6, #0x1c]
		BL       |loc_08011B04|
		MOV r6, #0
|loc_08022F48|
		CMP r7, #0
		BLT      |loc_08022FA8|
		LDR r0, [sp]
		CMP r7, r0
		BGE      |loc_08022FA8|
		ADD r1, r7, #0
		ADD r0, r5, #0
		BL       |loc_08022DAA|
		LSL r1, r6, #2
		ADD r1, r1, r5
		ADD r1, #0xff
		ADD r1, #1
		STR r1, [sp, #4]
		STR r0, [r1, #0x2c]
		LDR r1, [r4, #0x1c]
		CMP r1, r7
		BNE      |loc_08022F78|
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
|loc_08022F78|
		LDR r1, [sp, #4]
		MOV r3, #0x2a
		LDR r1, [r1, #0x2c]
		MUL r3, r6
		ADD r0, r1, #0
		LDR r1, [r1, #0x58]
		ADD r3, #0x23
		LDRB r2, [r1, #8]
		LDRB r1, [r1, #9]
		ADD r0, #0x6c
		LSR r2, r2, #1
		SUB r2, r3, r2
		MOV r3, #0x6a
		LSR r1, r1, #1
		SUB r1, r3, r1
		STR r1, [r0, #4]
		STR r2, [r0]
		LDR r1, [sp, #4]
		LDR r0, [pc, #0xe8]
		LDR r1, [r1, #0x2c]
		LDR r0, [r0, #0x1c]
		BL       |sub_0801191A|
		B        |loc_08022FB4|
|loc_08022FA8|
		LSL r0, r6, #2
		ADD r0, r0, r5
		ADD r0, #0xff
		MOV r1, #0
		ADD r0, #1
		STR r1, [r0, #0x2c]
|loc_08022FB4|
		ADD r7, #1
		ADD r6, #1
		CMP r6, #5
		BLT      |loc_08022F48|
|loc_08022FBC|
		DCW     0xE05F
|loc_08022FBE|
		LDR r0, [r4, #0x2c]
		CMP r0, #0
		BEQ      |loc_08022FCC|
		ADD r1, r0, #0
		LDR r0, [r6, #0x1c]
		BL       |loc_08011944|
|loc_08022FCC|
		LDR r0, [r4, #0x30]
		STR r0, [r4, #0x2c]
		LDR r0, [r4, #0x34]
		STR r0, [r4, #0x30]
		LDR r1, [r4, #0x38]
		STR r1, [r4, #0x34]
		LDR r1, [r4, #0x3c]
		STR r1, [r4, #0x38]
		MOV r1, #0
		STR r1, [r4, #0x3c]
		CMP r0, #0
		BEQ      |loc_08022FF0|
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
|loc_08022FF0|
		LDR r0, [r4, #0x34]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		LDR r1, [r4, #0x1c]
		LDR r0, [sp]
		ADD r1, #2
		CMP r1, r0
		BGE      |loc_08023018|
		ADD r0, r5, #0
		BL       |loc_08022DAA|
		ADD r1, r0, #0
		STR r0, [r4, #0x3c]
		LDR r0, [r6, #0x1c]
		BL       |sub_0801191A|
|loc_08023018|
		MOV r0, #0
		MOV r6, #0x6a
|loc_0802301C|
		LSL r1, r0, #2
		ADD r1, r1, r5
		ADD r1, #0xff
		ADD r1, #1
		LDR r2, [r1, #0x2c]
		CMP r2, #0
		BEQ      |loc_08023046|
		ADD r1, r2, #0
		LDR r2, [r2, #0x58]
		ADD r1, #0x6c
		LDRB r3, [r2, #8]
		LDRB r2, [r2, #9]
		LSR r4, r3, #1
		MOV r3, #0x2a
		MUL r3, r0
		ADD r3, #0x23
		SUB r3, r3, r4
		LSR r2, r2, #1
		SUB r2, r6, r2
		STR r2, [r1, #4]
		STR r3, [r1]
|loc_08023046|
		ADD r0, #1
		CMP r0, #5
		BLT      |loc_0802301C|
		DCW     0xE017
|sub_0802304E|
	LSL      r1, r0, #2
	ADD      r1, r1, r5
	ADD      r1, #0xff
	ADD      r1, #1
	LDR      r2, [r1, #0x2c]
	CMP      r2, #0
	BEQ      |loc_08023078|
	ADD      r1, r2, #0
	LDR      r2, [r2, #0x58]
	ADD      r1, #0x6c
	LDRB     r3, [r2, #8]
	LDRB     r2, [r2, #9]
	LSR      r4, r3, #1
	MOV      r3, #0x2a
	MUL      r3, r0
	ADD      r3, #0x23
	SUB      r3, r3, r4
	LSR      r2, r2, #1
	SUB      r2, r6, r2
	STR      r2, [r1, #4]
	STR      r3, [r1]
|loc_08023078|
	ADD      r0, #1
	CMP      r0, #5
	BLT      |sub_0802304E|
	LDR      r0, [sp, #8]
	MOV      r1, #0
	STRB     r1, [r0]
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_08023088|
|unk_08023088|
; cited by 0x08022D74 (a pc-relative load targets 0x08023088)
	INCBIN  baserom.gba_0x23088_0x2309c.extracted
		PUSH {r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		LDR r0, [pc, #0x3e0]
		ADD r4, r5, #0
		LDR r0, [r0, #0x10]
		ADD r4, #0xff
		LDR r2, [pc, #0x3dc]
		LDRB r1, [r0]
		ADD r4, #1
		MOV r3, #1
		ADD r6, r5, r2
		CMP r1, #0
		LDR r0, [r4, #0x1c]
		SUB sp, #0x7c
		BEQ      |loc_080230CC|
		CMP r1, #1
		BNE      |loc_080230DE|
		ADD r1, r3, #0
		CMP r0, #0x1f
		LDR r2, [r4, #0x18]
		BLT      |loc_080230C8|
		MOV r1, #0
|loc_080230C8|
		STR r1, [r2, #8]
		B        |loc_080230DE|
|loc_080230CC|
		LDR r1, [r4, #0x18]
		LDR r2, [r6]
		SUB r2, #1
		CMP r2, r0
		BLE      |loc_080230DA|
		MOV r0, #1
		B        |loc_080230DC|
|loc_080230DA|
		MOV r0, #0
|loc_080230DC|
		STR r0, [r1, #8]
|loc_080230DE|
		LDR r0, [r4, #0x14]
		LDR r2, [r4, #0x1c]
		MOV r1, #1
		CMP r2, #0
		BGT      |loc_080230EA|
		MOV r1, #0
|loc_080230EA|
		STR r1, [r0, #8]
		MOV r1, #0xf0
		MOV r2, #0xa0
		ADD r7, sp, #0x48
		ADD r0, r7, #0
		BL       |loc_0803F540|
		MOV r3, #1
		MOV r2, #0x5f
		ADD r0, r5, #0
		ADD r1, sp, #0x48
		BL       |loc_08006718|
		MOV r0, #1
		ADD r3, sp, #0x40
		STRB r0, [r3, #8]
		MOV r0, #0x78
		STR r0, [sp, #0x4c]
		MOV r0, #0x30
		STR r0, [sp, #0x50]
		LDR r0, [pc, #0x370]
		LDR r0, [r0, #0x10]
		LDRB r1, [r0]
		LDR r0, [pc, #0x370]
		CMP r1, #1
		LDR r1, [r4, #0x1c]
		DCW     0xD107
		ADD r1, #0x74
		LSL r1, r1, #2
		LDR r2, [r0, r1]
		ADR      r1, |loc_08023490|
		ADD r0, r7, #0
	INCBIN  baserom.gba_0x2312a_0x2312c.extracted
|sub_0802312C|
|unk_0802312C|
	INCBIN	baserom.gba_0x2312c_0x23130.extracted
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #2
	ADD      r1, r1, r6
	LDR      r1, [r1, #0xc]
	ADD      r1, #0x9e
	LSL      r1, r1, #2
	LDR      r2, [r0, r1]
	ADD      r1, pc, #0x34C
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x512
	LDR      r1, [pc, #0x34c]
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r2, #0x38
	MOV      r1, #0x30
	ADD      r4, sp, #0x14
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r0, #0
	STR      r0, [sp, #4]
	STR      r0, [sp, #8]
	MOV      r0, #0x30
	STR      r0, [sp, #0xc]
	MOV      r0, #0x38
	STR      r0, [sp, #0x10]
	MOV      r2, #0
	ADD      r0, r4, #0
	ADD      r1, sp, #4
	BL       |inc_0x03d784_0x041118| + 0x21f0
	MOV      r0, #0xa
	STR      r0, [sp, #4]
	MOV      r0, #2
	STR      r0, [sp, #8]
	MOV      r0, #0x25
	STR      r0, [sp, #0xc]
	MOV      r0, #0x2c
	STR      r0, [sp, #0x10]
	ADD      r0, r4, #0
	ADD      r1, sp, #4
	BL       |inc_0x0158_0x143f2| + 0x4df8
	LDR      r1, [pc, #0x30c]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	ADD      r0, r5, #0
	BL       |sub_08022DF4|
	MOV      r1, #0
	ADD      r0, sp, #0x14
	BL       |inc_0x03d784_0x041118| + 0x1e08
	MOV      r1, #0
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x7c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x2d0]
	ADD      r5, r0, #0
	LDR      r0, [r6, #0xc]
	LDR      r1, [pc, #0x2e8]
	MOV      r2, #0
	ADD      r0, r0, r1
	SUB      sp, #0xc
	STR      r0, [sp, #8]
	LDR      r0, [r0]
	MOV      r1, #0xb
	LSL      r1, r1, #7
	ADD      r1, r5, r1
	STR      r1, [sp, #4]
	STR      r0, [r1]
	CMP      r0, #0
	BEQ      |loc_080231D2|
	MOV      r2, #1
|loc_080231D2|
	MOV      r0, #0
|loc_080231D4|
	LDR      r1, [r6, #0xc]
	ADD      r3, r5, r0
	ADD      r1, r1, r0
	LDRB     r1, [r1, #2]
	ADD      r3, #0xff
	ADD      r3, #0x41
	STRB     r1, [r3, #1]
	CMP      r1, #0
	BEQ      |loc_080231E8|
	MOV      r2, #1
|loc_080231E8|
	ADD      r0, #1
	CMP      r0, #0x53
	BLT      |loc_080231D4|
	LDR      r1, [r6, #0xc]
	ADD      r4, r5, #0
	ADD      r1, #0xe4
	LDR      r3, [r1]
	ADD      r4, #0xff
	ADD      r4, #0x95
	MOV      r0, #0
	CMP      r3, #0
	BLE      |sub_08023220|
|loc_08023200|
	LSL      r2, r0, #2
	ADD      r2, r2, r1
	LDR      r2, [r2, #4]
	ADD      r0, #1
	LSL      r3, r2, #4
	LDR      r2, [r4]
	LSR      r3, r3, #4
	ADD      r7, r2, #1
	LSL      r2, r2, #2
	ADD      r2, r2, r4
	STR      r7, [r4]
	STR      r3, [r2, #4]
	LDR      r2, [r1]
	CMP      r2, r0
	BGT      |loc_08023200|
	B        |sub_08023224|
|sub_08023220|
|unk_08023220|
		CMP r2, #0
		DCW     0xD03B
|sub_08023224|
	LDR      r0, [pc, #0x280]
	LDR      r2, [pc, #0x27c]
	ADD      r1, r5, r0
	ADD      r7, r1, #0
	LDR      r0, [r6, #0xc]
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [sp, #4]
	LDR      r1, [r0]
	LDR      r0, [sp, #8]
	LDR      r2, [r0]
	ADD      r1, r2, r1
|loc_0802323C|
	STR      r1, [r0]
	LDR      r2, [r0]
	CMP      r2, r1
	BNE      |loc_0802323C|
	MOV      r0, #0
|loc_08023246|
	ADD      r2, r5, r0
	ADD      r2, #0xff
	LDR      r1, [r6, #0xc]
	ADD      r2, #0x41
	LDRB     r2, [r2, #1]
	ADD      r1, r1, r0
	LDRB     r3, [r1, #2]
	ADD      r2, r3, r2
	MOV      r3, #0xff
	ADD      r3, #1
	CMP      r2, r3
	BGE      |loc_08023262|
	STRB     r2, [r1, #2]
	B        |loc_08023266|
|loc_08023262|
	MOV      r2, #0xff
	STRB     r2, [r1, #2]
|loc_08023266|
	ADD      r0, #1
	CMP      r0, #0x53
	BLT      |loc_08023246|
	LDR      r0, [r4]
	MOV      r5, #0
	CMP      r0, #0
	BLE      |loc_08023288|
|loc_08023274|
	LSL      r0, r5, #2
	ADD      r0, r0, r4
	LDR      r1, [r0, #4]
	LDR      r0, [r6, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x42f0
	LDR      r0, [r4]
	ADD      r5, #1
	CMP      r0, r5
	BGT      |loc_08023274|
|loc_08023288|
	LDR      r2, [pc, #0x218]
	ADD      r0, r7, #0
	LDR      r1, [r6, #0xc]
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [pc, #0x218]
	LDR      r1, [r0]
	LDR      r0, [r6, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x489a
	LDR      r0, [r6, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x41a4
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_080232A6|
|unk_080232A6|
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		LDR r7, [pc, #0x1d8]
		LDR r0, [pc, #0x204]
		ADD r4, r5, #0
		LDR r3, [r7]
		ADD r4, #0xff
		ADD r4, #1
		MOV r6, #0
		ADD r0, r3, r0
		CMP r2, #0
		LDR r1, [pc, #0x1f0]
		BEQ      |loc_0802336E|
		CMP r2, #1
		BEQ      |sub_080232FA|
		ADD r5, #0xff
		ADD r5, #0x41
		SUB r1, #0xc
		CMP r2, #4
		BEQ      |loc_080232E6|
		CMP r2, #5
		DCW     0xD174
		ADD r3, r6, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0x1c]
		ADD r0, #1
		STR r0, [r4, #0x1c]
		MOV r0, #2
		STRB r0, [r5]
		DCW     0xE06A
|loc_080232E6|
		ADD r3, r6, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0x1c]
		SUB r0, #1
		STR r0, [r4, #0x1c]
		MOV r0, #3
		STRB r0, [r5]
		DCW     0xE060
|sub_080232FA|
	ADD      r3, r6, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r7, #4]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |sub_0802333E|
	MOV      r0, #0xff
	ADD      r0, #0x3d
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08023336|
	LDR      r1, [pc, #0x194]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	STR      r6, [r1, #0x10]
	LDR      r1, [pc, #0x188]
	STR      r1, [r0]
|loc_08023336|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0802333E|
|unk_0802333E|
; cited by 0x080230A0 (a pc-relative load targets 0x08023484)
		MOV r0, #0xbf
		LSL r0, r0, #2
		DCW     0xF01A
		DCW     0xF939
		ADD r4, r0, #0
		BEQ      |loc_08023364|
		MOV r5, #1
		ADD r3, r5, #0
		MOV r2, #0xd
		MOV r1, #0x5e
		ADD r0, r4, #0
		BL       |loc_08005460|
		LDR r0, [pc, #0x164]
		STR r0, [r4]
		MOV r0, #0xb
		LSL r0, r0, #6
		ADD r0, r4, r0
		STR r5, [r0, #0x38]
|loc_08023364|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE7E6
|loc_0802336E|
		ADD r3, r6, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [pc, #0x10c]
		LDR r0, [r0, #0x10]
		LDRB r0, [r0]
		CMP r0, #1
		BNE      |loc_08023464|
		LDR r0, [r7, #0x1c]
		BL       |loc_08011B04|
		LDR r0, [r7, #0x1c]
		BL       |loc_080115B0|
		LDR r0, [r7, #0x1c]
		BL       |loc_0801157E|
		MOV r2, #1
		LSL r2, r2, #0x1a
		LDRH r0, [r2]
		LSR r1, r2, #0x12
		BIC r0, r1
		STRH r0, [r2]
		LDR r2, [r4, #0x1c]
		MOV r0, #0xff
		ADD r0, #0x31
		STR r2, [sp]
		DCW     0xF01A
		DCW     0xF907
		CMP r0, #0
		BEQ      |loc_080233D8|
		LDR r1, [pc, #0x108]
		STMIA r0!, {r1, r6}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		B        |loc_080233BE|
		B        |loc_08023616|
|loc_080233BE|
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		MOV r2, #0xff
		ADD r2, #0x15
		STR r6, [r1, #0x10]
		STRB r6, [r2, r0]
		LDR r2, [pc, #0xf8]
		STR r2, [r0]
		MOV r2, #1
		STR r2, [r1, #0x28]
		STR r6, [r1, #0x1c]
		LDR r2, [sp]
		STR r2, [r1, #0x18]
|loc_080233D8|
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #2
		BNE      |loc_08023464|
		LDR r0, [pc, #0xe4]
		LDR r0, [r0]
		STR r0, [r4, #0x20]
		LDR r0, [r7, #0xc]
		BL       |loc_0800432C|
		LDR r0, [r4, #0x1c]
		LDR r1, [pc, #0x94]
		LSL r3, r0, #3
		SUB r0, r3, r0
		LSL r0, r0, #2
		ADD r1, #0x24
		ADD r0, r0, r1
		LDR r1, [r7, #0x14]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x6512
		LDR r0, [r4, #0x20]
		LDR r1, [pc, #0x80]
		LSL r3, r0, #3
		SUB r0, r3, r0
		LSL r0, r0, #2
		ADD r1, #0x24
		ADD r0, r0, r1
		LDR r1, [r7, #0x18]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x6512
		LDR r0, [r7, #0xc]
		MOV r3, #0x68
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		LDRB r0, [r0, #0x14]
		LDR r1, [pc, #0xa4]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		BL       |inc_0x153f2_0x1a3f2| + 0x1d2a
		BL       |inc_0x03d784_0x041118| + 0x2a3e
		LDR r0, [pc, #0x94]
		DCW     0xF01A
		DCW     0xF8BD
		ADD r4, r0, #0
		BEQ      |loc_08023456|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x22ba
		LDR r0, [pc, #0x88]
		MOV r1, #0x10
		STR r0, [r4]
		LSL r0, r1, #6
		ADD r0, r4, r0
		STR r1, [r0, #8]
		STR r6, [r0, #4]
|loc_08023456|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0x11c
		MOV r0, #0xc
		DCW     0xF01A
		DCW     0xF8AB
		B        |loc_08023466|
|loc_08023464|
		DCW     0xE045
|loc_08023466|
		CMP r0, #0
		BEQ      |loc_0802346E|
		LDR r1, [pc, #0x6c]
		STR r1, [r0]
|loc_0802346E|
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #1
		BNE      |loc_080234EE|
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x7500
		BL       |inc_0x03d784_0x041118| + 0x29dc
		B        |loc_080234DC|
	INCBIN  baserom.gba_0x23482_0x23484.extracted
		DCD     0x0872BFA8
		DCD     0x00000584
		DCD     0x0806BCE8
|loc_08023490|
|unk_08023490|
; cited by 0x08023148 (a pc-relative load targets 0x08023498)
	INCBIN  baserom.gba_0x23490_0x234dc.extracted
|loc_080234DC|
		ADD r0, r5, #0
		BL       |loc_08022AF6|
		ADD r0, r5, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x6dbc
		LDR r0, [r7, #0x20]
		BL       |inc_0x03d784_0x041118| + 0x2a16
|loc_080234EE|
		MOV r0, #0
		DCW     0xE724
		LDR r0, [r7, #0x10]
		LDRB r0, [r0]
		CMP r0, #0
		BNE      |loc_080235DE|
		LDR r0, [r7, #0x1c]
		BL       |loc_08011B04|
		LDR r0, [r7, #0x1c]
		BL       |loc_080115B0|
		LDR r0, [r7, #0x1c]
		BL       |loc_0801157E|
		MOV r2, #1
		LSL r2, r2, #0x1a
		LDRH r0, [r2]
		LSR r1, r2, #0x12
		BIC r0, r1
		STRH r0, [r2]
		LDR r1, [r4, #0x1c]
		LDR r0, [pc, #0x288]
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r1, r1, #2
		ADD r0, r5, r0
		ADD r0, r1, r0
		LDR r0, [r0, #0xc]
		MOV r3, #0x68
		MUL r0, r3
		LDR r1, [pc, #0x278]
		ADD r0, r0, r5
		ADD r1, r0, r1
		LDR r0, [r7, #0x14]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x6542
		LDR r2, [r7, #0x14]
		MOV r0, #0xff
		STR r2, [sp]
		LDR r4, [r7, #0x18]
		ADD r0, #0x31
		DCW     0xF01A
		DCW     0xF839
		CMP r0, #0
		BEQ      |loc_08023570|
		LDR r1, [pc, #0x260]
		MOV r2, #0xff
		STMIA r0!, {r1, r6}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		ADD r2, #0x15
		STRB r6, [r2, r0]
		LDR r2, [pc, #0x24c]
		STR r2, [r0]
		STR r6, [r1, #0x28]
		STR r6, [r1, #0x1c]
		LDR r2, [sp]
		ADD r1, #0x20
		STMIA r1!, {r2, r4}
|loc_08023570|
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #2
		BNE      |loc_080235DE|
		LDR r0, [r7, #0xc]
		BL       |loc_0800432C|
		LDR r0, [r7, #0xc]
		MOV r3, #0x68
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		LDRB r0, [r0, #0x14]
		LDR r1, [pc, #0x220]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		BL       |inc_0x153f2_0x1a3f2| + 0x1d2a
		BL       |inc_0x03d784_0x041118| + 0x2a3e
		LDR r0, [pc, #0x214]
		DCD     0xF808F01A
		ADD r4, r0, #0
		BEQ      |loc_080235C0|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x22ba
		LDR r0, [pc, #0x208]
		MOV r1, #0x10
		STR r0, [r4]
		LSL r0, r1, #6
		ADD r0, r4, r0
		STR r1, [r0, #8]
		STR r6, [r0, #4]
|loc_080235C0|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0x11c
		MOV r0, #0xc
		DCD     0xFFF6F019
		CMP r0, #0
		BEQ      |loc_080235D4|
		LDR r1, [pc, #0x1ec]
		STR r1, [r0]
|loc_080235D4|
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #1
		BNE      |loc_080235FC|
		B        |loc_080235E0|
|loc_080235DE|
		B        |loc_08023600|
|loc_080235E0|
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x7500
		BL       |inc_0x03d784_0x041118| + 0x29dc
		ADD r0, r5, #0
		BL       |loc_08022AF6|
		ADD r0, r5, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x6dbc
		LDR r0, [r7, #0x20]
		BL       |inc_0x03d784_0x041118| + 0x2a16
|loc_080235FC|
		MOV r0, #0
		DCW     0xE69D
|loc_08023600|
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x7500
		BL       |inc_0x03d784_0x041118| + 0x29dc
		ADD r0, r5, #0
		BL       |loc_08022AF6|
		LDR r0, [r7, #0x20]
		BL       |inc_0x03d784_0x041118| + 0x2a16
|loc_08023616|
		MOV r0, #0
		DCW     0xE690
|sub_0802361A|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1a4]
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11458
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x667e
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r4, [pc, #0x190]
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11426
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x118c6
	LDR      r0, [pc, #0x184]
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_0802372C|
	MOV      r1, #0
	STR      r1, [r0]
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x119ac
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11458
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11426
	MOV      r4, #1
	LSL      r4, r4, #0x1a
	LDRH     r0, [r4]
	LSR      r1, r4, #0x12
	BIC      r0, r1
	STRH     r0, [r4]
	MOV      r0, #0xff
	ADD      r0, #0x1d
	BL       |GBARam_Malloc|
	LDR      r1, [pc, #0x138]
	CMP      r0, #0
	BEQ      |loc_08023696|
	MOV      r2, #0
	STMIA    r0!, {r1, r2}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r2, [r1, #0xc]
	STR      r2, [r1, #8]
	MOV      r3, #0xff
	ADD      r3, #0x15
	STR      r2, [r1, #0x10]
	STRB     r2, [r3, r0]
	LDR      r3, [pc, #0x138]
	STR      r3, [r0]
	STR      r2, [r1, #0x18]
|loc_08023696|
	BL       |inc_0x03d784_0x041118| + 0x11c
	CMP      r0, #2
	BEQ      |sub_080236D8|
	LDRH     r0, [r4]
	MOV      r1, #0x11
	LSL      r1, r1, #8
	ORR      r0, r1
	STRH     r0, [r4]
	MOV      r0, #0xbf
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_080236CE|
	MOV      r5, #1
	ADD      r3, r5, #0
	MOV      r2, #0xd
	MOV      r1, #0x5e
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x5308
	LDR      r0, [pc, #0x10c]
	STR      r0, [r4]
	MOV      r0, #0xb
	LSL      r0, r0, #6
	ADD      r0, r4, r0
	STR      r5, [r0, #0x38]
|loc_080236CE|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_080236D8|
|unk_080236D8|
		LDR r0, [pc, #0xf8]
		DCW     0xF019
		DCW     0xFF6D
		ADD r4, r0, #0
		DCW     0xD03D
		LDR r0, [pc, #0xc8]
		ADD r1, r4, #0
		STR r0, [r4]
		MOV r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r0, [r4, #4]
		STR r0, [r1, #0xc]
		STR r0, [r1, #8]
		STR r0, [r1, #0x10]
		LDR r1, [pc, #0xe0]
		STR r1, [r4]
		MOV r1, #0xff
		ADD r1, #0x95
		STR r0, [r1, r4]
		LDR r1, [pc, #0xa0]
		ADD r1, r4, r1
		STR r0, [r1]
		LDR r0, [pc, #0xd4]
		ADD r0, r4, r0
		BL       |loc_08004838|
		LDR r0, [pc, #0xd0]
		LDR r6, [pc, #0xd0]
		ADD r5, r4, r0
		ADD r1, r5, #0
		ADD r1, #0x3a
		ADD r0, r5, #0
		MOV r2, #2
		ADD r3, r6, #0
		ADD r0, #0x2e
		BL       |sub_08046FF4|
		LDR r7, [pc, #0xc0]
		ADD r3, r7, #0
		MOV r2, #4
		DCW     0xE000
|loc_0802372C|
|unk_0802372C|
		B        |loc_08023768|
		ADD r1, r5, #0
		ADD r1, #0x4c
		ADD r0, r5, #0
		ADD r0, #0x3c
		BL       |sub_08046FF4|
		LDR r0, [pc, #0xb0]
		ADD r3, r6, #0
		ADD r5, r4, r0
		ADD r1, r5, #0
		ADD r1, #0x3a
		ADD r0, r5, #0
		MOV r2, #2
		ADD r0, #0x2e
		BL       |sub_08046FF4|
		ADD r1, r5, #0
		ADD r1, #0x4c
		ADD r3, r7, #0
		MOV r2, #4
		ADD r0, r5, #0
		ADD r0, #0x3c
		BL       |sub_08046FF4|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #0
		DCW     0xE7B6
|loc_08023768|
		ADD r0, r5, #0
		BL       |loc_080067F4|
		DCW     0xE7B2
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
|sub_08023AE4|
|unk_08023AE4|
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		LDR r2, [r1, #0xc]
		CMP r2, #0xa
		BHS      |loc_08023B50|
		ADR      r3, |loc_08023AF8|
		LDRB r3, [r3, r2]
		LSL r3, r3, #1
		ADD pc, r3
|loc_08023AF8|
		LSL r4, r0, #0x10
		CMP r3, #0x18
		CMP r3, #0x18
		CMP r3, #0x18
		CMP r4, #0x2b
		LDR r3, [r1, #0x14]
		MOV r2, #0
		STR r2, [r3, #0x38]
		LDR r3, [r1, #0x18]
		STR r2, [r3, #0x38]
		LDR r2, [r1, #0xc]
		LSL r2, r2, #2
		ADD r0, r2, r0
		ADD r0, #0xff
		ADD r0, #1
		LDR r0, [r0, #0x14]
		STR r5, [r0, #0x38]
		LDR r0, [r1, #0xc]
		CMP r0, #0
		BEQ      |loc_08023B22|
		MOV r5, #0
|loc_08023B22|
		LDR r0, [pc, #0x160]
		LDR r0, [r0, #4]
		STRB r5, [r0]
		B        |loc_08023B50|
	INCBIN  baserom.gba_0x23b2a_0x23b50.extracted
|loc_08023B50|
|unk_08023B50|
		B        |loc_08023C1C|
	INCBIN  baserom.gba_0x23b52_0x23c1c.extracted
|loc_08023C1C|
		MOV r0, #0
		DCW     0xE760
|sub_08023C20|
	LDR      r1, [pc, #0x8c]
	PUSH     {r4, lr}
	LDR      r2, [r1]
	CMP      r2, #0
	BEQ      |sub_08023C58|
	MOV      r4, #0
	MOV      r0, #0xff
	ADD      r0, #0x15
	STR      r4, [r1]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08023C50|
	LDR      r1, [pc, #0x4c]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r4, [r1, #0xc]
	STR      r4, [r1, #8]
	STR      r4, [r1, #0x10]
	LDR      r1, [pc, #0x64]
	STR      r1, [r0]
|loc_08023C50|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r4, pc}
|sub_08023C58|
|unk_08023C58|
	INCBIN	baserom.gba_0x23c58_0x23c5a.extracted
|sub_08023C5A|
|unk_08023C5A|
	INCBIN	baserom.gba_0x23c5a_0x23c5e.extracted
	CMP      r2, #8
	BCS      |loc_08023C7A|
	ADD      r3, pc, #0x8
	LDRB     r3, [r3, r2]
	LSL      r3, r3, #1
	ADD      pc, r3
	LSL      r0, r0, #0
|loc_08023C6C|
	LSL      r4, r0, #0x10
	LSL      r4, r0, #0x1c
	LSL      r7, r0, #0x1c
	LSL      r7, r0, #0x1c
	LDR      r1, [pc, #0x38]
	MOV      r0, #1
	STR      r0, [r1]
|loc_08023C7A|
	BX       lr
|sub_08023C7C|
|unk_08023C7C|
; cited by 0x08023A96 (a pc-relative load targets 0x08023C7C)
	INCBIN  baserom.gba_0x23c7c_0x23cb8.extracted
		PUSH {r4, r5, r6, r7, lr}
		LDR r5, [r1, #4]
		ADD r4, r0, #0
		ADD r1, r5, #0
		ADD r1, #0xff
		ADD r1, #0xa1
		LDR r0, [r1]
		LDR r3, [r1, #4]
		SUB sp, #0x24
		ASR r3, r3, #8
		STR r3, [sp, #0x20]
		ASR r0, r0, #8
		STR r0, [sp, #0x1c]
		STR r3, [sp, #0x18]
		LDR r3, [sp, #0x1c]
		LDR r6, [sp, #0x20]
		STR r0, [sp, #0x14]
		LSL r3, r3, #8
		STR r3, [r4, #0x10]
		LSL r6, r6, #8
		STR r6, [r4, #0x14]
		LDR r0, [r1]
		ADD r2, r1, #4
		LDR r1, [r2]
		ASR r0, r0, #8
		ASR r1, r1, #8
		STR r1, [sp, #0x10]
		STR r1, [sp, #0x18]
		STR r0, [sp, #0xc]
		STR r0, [sp, #0x14]
		LDR r0, [r4, #0x18]
		LDR r1, [sp, #0x14]
		ADD r7, r4, #0
		SUB r0, r0, r1
		LDR r1, [r4, #0x1c]
		LDR r2, [sp, #0x18]
		STR r0, [sp, #0xc]
		SUB r1, r1, r2
		STR r1, [sp, #0x10]
		LSL r1, r1, #8
		LSL r0, r0, #8
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x18]
		LDR r0, [r4, #0x38]
		ADD r7, #8
		LSL r6, r0, #8
		LDR r0, [sp, #0x14]
		LSL r1, r0, #8
		ADD r0, r6, #0
		BL       |sub_08046E58|
		STR r0, [sp]
		LDR r0, [sp, #0x18]
		LSL r1, r0, #8
		ADD r0, r6, #0
		BL       |sub_08046E58|
		LDR r1, [sp]
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		STR r0, [r7]
		LDR r1, [sp, #0x10]
		STR r1, [r7, #4]
		LDR r0, [r4, #8]
		ADD r2, r0, #0
		CMP r0, #0
		BGE      |loc_08023D48|
		NEG r0, r0
|loc_08023D48|
		LDR r1, [r4, #0xc]
		ADD r3, r1, #0
		CMP r1, #0
		BGE      |loc_08023D52|
		NEG r1, r1
|loc_08023D52|
		MOV r6, #0
		CMP r0, r1
		BLE      |loc_08023D66|
		CMP r2, #0
		BLT      |loc_08023D60|
		MOV r0, #3
		B        |loc_08023D62|
|loc_08023D60|
		MOV r0, #2
|loc_08023D62|
		STRB r0, [r5, #0x10]
		DCW     0xE007
|loc_08023D66|
		CMP r3, #0
		BLT      |sub_08023D6E|
		MOV r0, #1
		DCW     0xE000
|sub_08023D6E|
	MOV      r0, #0
	MOV      r1, #1
	SUB      r0, r1, r0
	STRB     r0, [r5, #0x10]
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r1, [r0, #0x78]
	LDR      r0, [r0, #0x7c]
	STR      r0, [r4, #0x24]
	STR      r6, [r4, #0x28]
	STR      r1, [r4, #0x20]
	STR      r6, [r4, #0x2c]
	STR      r6, [r4, #0x30]
	LDR      r0, [r4, #0x38]
	LSL      r0, r0, #2
	STR      r0, [r4, #0x34]
	LDR      r1, [r4, #0xc]
	SUB      r0, r1, r0
	STR      r0, [r4, #0xc]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x30]
	ADD      r3, r2, r1
	MOV      r2, #0
	MOV      r1, #0xe
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #0x24
	STRB     r0, [r5, #8]
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
|loc_08023DBA|
	PUSH     {r4}
	LDR      r2, [r0, #0x34]
	SUB      sp, #0x10
	SUB      r2, #8
	STR      r2, [r0, #0x34]
	LDR      r3, [r0, #0x28]
	LDR      r4, [r0, #0x30]
	ADD      r3, r3, r4
	STR      r3, [r0, #0x28]
	LDR      r3, [r0, #0x2c]
	ADD      r2, r3, r2
	STR      r2, [r0, #0x2c]
	LDR      r2, [r0, #0xc]
	ADD      r2, #8
	STR      r2, [r0, #0xc]
	LDR      r3, [r0, #0x10]
	LDR      r4, [r0, #8]
	ADD      r3, r3, r4
	STR      r3, [r0, #0x10]
	LDR      r3, [r0, #0x14]
	ADD      r2, r3, r2
	STR      r2, [r0, #0x14]
	ADD      r2, r1, #0
	ADD      r2, #0xff
	LDR      r4, [r0, #0x10]
	ADD      r2, #0xa1
	STMIA    r2!, {r4}
	LDR      r3, [r0, #0x14]
	STR      r3, [r2]
	ADD      r3, r2, #0
	LDR      r2, [r0, #0x28]
	LDR      r1, [r0, #0x2c]
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #4]
	ADD      r1, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STR      r1, [sp, #8]
	STR      r2, [sp, #0xc]
	LDR      r1, [r0, #0x20]
	LDR      r2, [sp, #8]
	LDR      r0, [r0, #0x24]
	ADD      r1, r1, r2
	LDR      r2, [sp, #0xc]
	SUB      r3, #0x2c
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	STR      r1, [sp]
	LDR      r1, [sp, #4]
	STMIA    r3!, {r0, r1}
	ADD      sp, #0x10
	POP      {r4}
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #0x3c]
	LDR      r4, [r1, #4]
	ADD      r0, #1
	STR      r0, [r5, #0x3c]
	CMP      r0, #8
	BLT      |loc_08023E54|
	CMP      r0, #8
	BNE      |sub_08023E56|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x30]
	ADD      r3, r2, r1
	MOV      r2, #1
	MOV      r1, #0xe
	BL       |inc_0x046118_0x049114| + 0x98e
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |loc_08023DBA|
|loc_08023E54|
	POP      {r3, r4, r5, pc}
|sub_08023E56|
|unk_08023E56|
		LDR r1, [r5, #0x38]
		LSR r2, r1, #0x1f
		ADD r2, r2, r1
		ASR r2, r2, #1
		ADD r2, #8
		CMP r2, r0
		BLE      |loc_08023E6E|
		ADD r1, r4, #0
		ADD r0, r5, #0
		BL       |loc_08023DBA|
		B        |loc_08023E54|
|loc_08023E6E|
		ADD r2, r1, #0
		ADD r2, #8
		CMP r0, r2
		BGE      |loc_08023EA2|
		LDR r3, [r4, #0x50]
		MOV r2, #2
		LDR r3, [r3]
		CMP r3, #4
		BNE      |loc_08023E8A|
		SUB r0, r0, r1
		ADD r0, #8
		LSL r0, r0, #0x1c
		LSR r2, r0, #0x1f
		ADD r2, #2
|loc_08023E8A|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r3, [r1, #0x30]
		ADD r3, r3, r1
		MOV r1, #0xe
		BL       |inc_0x046118_0x049114| + 0x98e
		ADD r1, r4, #0
		ADD r0, r5, #0
		BL       |loc_08023DBA|
		B        |loc_08023E54|
|loc_08023EA2|
		CMP r2, r0
		BNE      |loc_08023EC4|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x30]
		ADD r3, r2, r1
		MOV r2, #0
		MOV r1, #0xe
		BL       |inc_0x046118_0x049114| + 0x98e
		ADD r5, #0x20
		ADD r4, #0xff
		ADD r4, #1
		ADD r4, #0x78
		LDMIA r5!, {r0, r1}
		STMIA r4!, {r0, r1}
		B        |loc_08023E54|
|loc_08023EC4|
		ADD r1, #0x10
		CMP r0, r1
		BLT      |loc_08023E54|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x40]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
	INCBIN  baserom.gba_0x23ee0_0x23ee2.extracted
|sub_08023EE2|
|unk_08023EE2|
	INCBIN	baserom.gba_0x23ee2_0x23ee6.extracted
	ADD      r0, #0x38
	LDMIA    r0!, {r0, r1}
	ADD      r0, #0x10
	CMP      r1, r0
	BLT      |sub_08023EF4|
	MOV      r0, #1
	BX       lr
|sub_08023EF4|
|unk_08023EF4|
		MOV r0, #0
		BX       lr
|sub_08023EF8|
	PUSH     {r3, lr}
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	ADD      r0, r1, #0
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	STRB     r2, [r0, #0x11]
	MOV      r1, #0x12
	BL       |inc_0x0158_0x143f2| + 0xeb82
	POP      {r3, pc}
	PUSH     {lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x1c
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x80
	BCC      |sub_08023F32|
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x1c
	POP      {pc}
|sub_08023F32|
|unk_08023F32|
		CMP r0, #4
		BHS      |loc_08023F3C|
		MOV r0, #0
		STRB r0, [r1, #0x11]
		DCW     0xE7F8
|loc_08023F3C|
		LSL r0, r0, #0x1c
		LSR r0, r0, #0x1e
		STRB r0, [r1, #0x11]
		BNE      |loc_08023F48|
		MOV r0, #2
		STRB r0, [r1, #0x11]
|loc_08023F48|
		ADD r0, r1, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r2}
		LDR r0, [r0]
		ASR r2, r2, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r2, #0
		STR r2, [sp, #4]
		LDR r2, [sp, #8]
		STR r0, [sp, #0xc]
		STR r2, [sp, #0x10]
		LDRB r0, [r1, #0x10]
		LDR r2, [pc, #0xc4]
		LSL r0, r0, #3
		ADD r0, r0, r2
		LDR r2, [sp, #0xc]
		LDR r3, [r0]
		ADD r2, r2, r3
		LDR r3, [sp, #0x10]
		LDR r0, [r0, #4]
		STR r2, [sp, #4]
		ADD r0, r3, r0
		STR r0, [sp, #8]
		ADD r0, r2, #0
		LDR r2, [sp, #8]
		STR r0, [sp, #0x14]
		ADD r0, sp, #0x14
		STR r2, [sp, #0x18]
	INCBIN  baserom.gba_0x23f84_0x23f86.extracted
|sub_08023F86|
|unk_08023F86|
	INCBIN	baserom.gba_0x23f86_0x23f8a.extracted
	LDR      r0, [pc, #0xa0]
	PUSH     {r4, lr}
	MOV      r1, #0xbd
	LDR      r2, [pc, #0x9c]
	LSL      r1, r1, #2
	SUB      r0, #4
	LDR      r0, [r0]
	ADD      r1, r1, r2
	LDR      r4, [pc, #0x98]
	MOV      r2, #0x40
	MOV      r3, #0
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xba8
	POP      {r4, pc}
	PUSH     {r4, r5, lr}
	LDR      r0, [pc, #0x8c]
	SUB      sp, #0xc
	MOV      r5, #0
	LDR      r0, [r0]
	ADD      r4, r1, #0
	LDR      r2, [pc, #0x84]
	ADD      r1, r5, #0
	CMP      r4, #0
	STR      r5, [sp, #4]
	STR      r0, [sp, #8]
	STR      r2, [sp]
	BEQ      |loc_08023FC8|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_08023FC8|
	MOV      r0, sp
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x68]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x4c]
	MOV      r1, #0xbd
	LDR      r2, [pc, #0x4c]
	LSL      r1, r1, #2
	SUB      r0, #4
	LDR      r0, [r0]
	ADD      r1, r1, r2
	LDR      r4, [pc, #0x44]
	MOV      r2, #0x40
	ADD      r3, r5, #0
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [pc, #0x48]
	STR      r0, [sp]
	LDR      r0, [sp, #4]
	CMP      r0, #0
	BEQ      |loc_0802400E|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802400E|
	ADD      sp, #0xc
	POP      {r4, r5, pc}
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0x28]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_08024020|
	MOV      r0, #0
|loc_08024020|
	SUB      r0, r2, r0
	BX       lr
	LDR      r0, [pc, #0x18]
	ADD      r0, #4
	BX       lr
	LSL      r0, r0, #0
	STMIA    r3!, {r3, r4, r6}
	LSR      r2, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	CMP      r7, #0xa8
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	BL       |loc_08024120|
	ADD      r4, #0xff
	ADD      r4, #0x11
	MOV      r0, #0xff
	ADD      r0, #0x35
	LDRB     r7, [r4, #0xc]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_080240A8|
	LDR      r0, [pc, #0xa8]
	ADD      r5, r4, #0
	STR      r0, [r4]
	MOV      r0, #0xff
	ADD      r0, #0x15
	STRB     r7, [r0, r4]
	ADD      r5, #0xff
	MOV      r6, #0
	ADD      r5, #1
	STR      r6, [r5, #0x1c]
	STR      r6, [r5, #0x20]
	MVN      r1, r6
	ADD      r0, r4, #0
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0x7c]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x7c]
	STR      r6, [r0]
	LDR      r0, [pc, #0x7c]
	STR      r6, [r0]
	LDR      r0, [pc, #0x7c]
	STR      r0, [r4]
	MOV      r0, #0xff
	ADD      r0, #0x31
	STR      r6, [r5, #0x2c]
	STRB     r7, [r0, r4]
|loc_080240A8|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x29dc
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	BL       |sub_0802426E|
	POP      {r3, pc}
	LDR      r1, [pc, #0x5c]
	PUSH     {r3, lr}
	LDR      r1, [r1]
	CMP      r1, #0
	BEQ      |sub_080240DA|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	LDR      r2, [r1, #0x18]
	ADD      r2, #1
	STR      r2, [r1, #0x18]
	CMP      r2, #0xa
	BLE      |sub_080240DA|
	BL       |inc_0x03d784_0x041118| + 0x29fe
	MOV      r0, #2
	POP      {r3, pc}
|sub_080240DA|
|unk_080240DA|
		BL       |loc_080067F4|
		DCW     0xE7FB
|sub_080240E0|
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r0, [r0, #0x2c]
	STRB     r0, [r1]
	MOV      r0, #1
	BX       lr
	MOV      r1, #0xff
	ADD      r1, #0x31
	LDRB     r1, [r1, r0]
	CMP      r1, r2
	BNE      |loc_0802410A|
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r1, [r0, #0x2c]
	ADD      r1, #1
	STR      r1, [r0, #0x2c]
	CMP      r1, #4
	BLE      |loc_0802410A|
	LDR      r1, [pc, #0x10]
	MOV      r0, #1
	STR      r0, [r1]
|loc_0802410A|
	BX       lr
|sub_0802410C|
	DCW      0x92ec
	DCW      0x0804,0xffff
|sub_08024112|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x270]
	LSR      r4, r0, #0x20
|loc_08024120|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r5, [pc, #0x1b4]
	SUB      sp, #0x14
	LDR      r7, [r5, #0x68]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r1, #1
	MOV      r2, #0x1c
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r4, r0, #0
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r3, #0xc
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r6, [pc, #0x18c]
	MOV      r1, #0
	LDR      r2, [r6]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x28
	MOV      r0, #0
	STR      r7, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0xff
	ADD      r0, #0x15
	LDRB     r0, [r0, r4]
	MOV      r3, #0x10
	CMP      r0, #0
	BEQ      |sub_080241F6|
	CMP      r0, #1
	BEQ      |loc_0802421E|
	CMP      r0, #2
	BEQ      |loc_08024246|
	CMP      r0, #3
	BNE      |loc_080241AE|
	MOV      r0, #0xff
	ADD      r0, #0x75
	LDR      r5, [r5, r0]
	LDR      r2, [r6]
	MOV      r1, #0
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x10
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r0, #0
	STR      r5, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
|loc_080241AE|
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x128]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x77
	LSL      r2, r2, #6
	MOV      r1, #0
	LDR      r0, [pc, #0x120]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #7
	STR      r0, [sp, #4]
	MOV      r0, #8
	STR      r0, [sp, #8]
	MOV      r0, #0x18
	STR      r0, [sp, #0xc]
	MOV      r0, #0xf
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	LDR      r2, [pc, #0x10c]
	LDR      r1, [pc, #0x104]
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
	POP      {r4, r5, r6, r7, pc}
|sub_080241F6|
|unk_080241F6|
		MOV r0, #0xff
		ADD r0, #0x69
		LDR r5, [r5, r0]
		LDR r2, [r6]
		MOV r1, #0
		STR r1, [sp, #8]
		MOV r0, #5
		STR r2, [sp, #0xc]
		MOV r2, #0x10
		STR r0, [sp, #4]
		ADD r1, r4, #0
		MOV r0, #0
		STR r5, [sp]
		BL       |loc_08014124|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		B        |loc_080241AE|
|loc_0802421E|
|unk_0802421E|
		MOV r0, #0xff
		ADD r0, #0x71
		LDR r5, [r5, r0]
		LDR r2, [r6]
		MOV r1, #0
		STR r1, [sp, #8]
		MOV r0, #5
		STR r2, [sp, #0xc]
		MOV r2, #0x10
		STR r0, [sp, #4]
		ADD r1, r4, #0
		MOV r0, #0
		STR r5, [sp]
		BL       |loc_08014124|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		B        |loc_080241AE|
|loc_08024246|
|unk_08024246|
		MOV r0, #0xff
		ADD r0, #0x6d
		LDR r5, [r5, r0]
		LDR r2, [r6]
		MOV r1, #0
		STR r1, [sp, #8]
		MOV r0, #5
		STR r2, [sp, #0xc]
		MOV r2, #0x10
		STR r0, [sp, #4]
		ADD r1, r4, #0
		MOV r0, #0
		STR r5, [sp]
		BL       |loc_08014124|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800664E|
		B        |loc_080241AE|
|sub_0802426E|
	PUSH     {r3, lr}
	MOV      r3, #1
	LSL      r3, r3, #0x1a
	LDRH     r1, [r3]
	LSR      r2, r3, #0x12
	BIC      r1, r2
	STRH     r1, [r3]
	CMP      r0, #0
	BEQ      |loc_0802428C|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802428C|
	POP      {r3, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0x38
	MOV      r1, #0x88
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x4f3e
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
	PUSH     {r3, lr}
	CMP      r2, #1
	BNE      |sub_080242D2|
	MOV      r0, #1
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r3, pc}
|sub_080242D2|
|unk_080242D2|
; cited by 0x08024122 (a pc-relative load targets 0x080242D8)
		MOV r0, #0
		DCW     0xE7FC
	INCBIN  baserom.gba_0x242d6_0x242e2.extracted
|sub_080242E2|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0xc
	ADD      r4, r0, #0
	BL       |loc_08024120|
	ADD      r6, r4, #0
	ADD      r6, #0xff
	ADD      r6, #1
	LDR      r1, [r6, #0x28]
	MOV      r0, #0xff
	ADD      r0, #0x45
	MOV      r5, #7
	MOV      r7, #0
	CMP      r1, #0
	BEQ      |sub_0802437A|
	CMP      r1, #1
	BNE      |loc_08024374|
	LDR      r1, [r6, #0x18]
	STR      r1, [sp, #8]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_0802436E|
	LDR      r0, [pc, #0x23c]
	MOV      r1, #0xff
	STR      r0, [r4]
	ADD      r1, #0x15
	STRB     r5, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	STR      r7, [r5, #0x1c]
	STR      r7, [r5, #0x20]
	MVN      r1, r7
	ADD      r0, r4, #0
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r7, [r5, #0x18]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0x214]
	LDR      r1, [pc, #0x220]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x210]
	STR      r7, [r0]
	LDR      r0, [pc, #0x210]
	STR      r7, [r0]
	LDR      r0, [pc, #0x210]
	STR      r0, [r4]
	MOV      r0, #1
	STR      r0, [r5, #0x38]
|unk_0802435C|
	INCBIN	baserom.gba_0x2435c_0x2435e.extracted
	STR      r0, [r1]
	LDR      r0, [sp, #8]
	STR      r0, [r5, #0x2c]
	MOV      r0, #0xff
	ADD      r0, #0x41
	STR      r7, [r5, #0x3c]
	STR      r7, [r0, r4]
	STR      r7, [r1, #4]
|loc_0802436E|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x29dc
|loc_08024374|
	STR      r7, [r6, #0x2c]
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_0802437A|
|unk_0802437A|
		LDR r1, [r6, #0x20]
		STR r1, [sp, #4]
		LDR r1, [r6, #0x24]
		STR r1, [sp, #8]
		DCW     0xF019
		DCW     0xF919
		ADD r4, r0, #0
		BEQ      |loc_080243E4|
		LDR r0, [pc, #0x1cc]
		MOV r1, #0xff
		STR r0, [r4]
		ADD r1, #0x15
		STRB r5, [r1, r4]
		ADD r5, r4, #0
		ADD r5, #0xff
		ADD r5, #1
		STR r7, [r5, #0x1c]
		MOV r1, #0
		MVN r1, r1
		STR r7, [r5, #0x20]
		ADD r0, r4, #0
		MOV r2, #0x80
		ADD r0, #0x84
		STR r7, [r5, #0x18]
		BL       |sub_0804912C|
		MOV r2, #0x10
		MOV r1, #0
		ADD r0, r5, #4
		BL       |sub_0804912C|
		LDR r0, [pc, #0x1a0]
		LDR r1, [pc, #0x1b0]
		STR r0, [r5, #0x24]
		LDR r0, [pc, #0x1a0]
		STR r7, [r0]
		LDR r0, [pc, #0x1a0]
		STR r7, [r0]
		LDR r0, [pc, #0x1a0]
		STR r0, [r4]
		MOV r0, #0
		MVN r0, r0
		STR r7, [r5, #0x38]
		STR r0, [r1]
		LDR r0, [sp, #4]
		STR r0, [r5, #0x30]
		LDR r0, [sp, #8]
		STR r0, [r5, #0x34]
		MOV r0, #0xff
		ADD r0, #0x41
		STR r7, [r5, #0x3c]
		STR r7, [r0, r4]
		STR r7, [r1, #4]
|loc_080243E4|
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x243e6_0x243e8.extracted
|sub_080243E8|
|unk_080243E8|
	INCBIN	baserom.gba_0x243e8_0x243ec.extracted
	PUSH     {r3, lr}
	BL       |sub_0802426E|
	POP      {r3, pc}
	LDR      r1, [pc, #0x168]
	PUSH     {r3, lr}
	LDR      r2, [r1]
	CMP      r2, #0
	BEQ      |sub_08024406|
	MOV      r0, #0
	STR      r0, [r1]
	MOV      r0, #1
	POP      {r3, pc}
|sub_08024406|
|unk_08024406|
		LDR r1, [pc, #0x164]
		LDR r1, [r1, #4]
		CMP r1, #0
		BEQ      |loc_08024426|
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		LDR r2, [r1, #0x1c]
		ADD r2, #1
		STR r2, [r1, #0x1c]
		CMP r2, #0x1e
		BLE      |loc_08024426|
		BL       |inc_0x03d784_0x041118| + 0x29fe
		MOV r0, #2
		DCW     0xE7EE
|loc_08024426|
		BL       |loc_080067F4|
		DCW     0xE7EB
|sub_0802442C|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	ADD      r5, #0xff
	ADD      r5, #1
	ADD      r4, r1, #0
	LDR      r1, [r5, #0x38]
	CMP      r1, #0
	BNE      |loc_08024484|
	ADD      r0, #0xff
	ADD      r0, #0x41
	LDR      r1, [r0]
	MOV      r6, #0
	CMP      r1, #0
	BEQ      |loc_08024462|
	CMP      r1, #1
	BEQ      |loc_08024462|
	MOV      r0, #1
	CMP      r1, #2
	BEQ      |loc_08024478|
	CMP      r1, #3
	BNE      |loc_08024484|
	STRB     r0, [r4]
	STRB     r0, [r4, #1]
	LDR      r0, [r5, #0x3c]
	STRB     r0, [r4, #3]
	MOV      r0, #4
	POP      {r4, r5, r6, pc}
|loc_08024462|
	MOV      r2, #0x20
	ADD      r0, r4, #4
	LDR      r1, [r5, #0x30]
	BL       |inc_0x049120_0x055620| + 0x18
	STRB     r6, [r4]
	STRB     r6, [r4, #1]
	LDR      r0, [r5, #0x3c]
	STRB     r0, [r4, #3]
	MOV      r0, #0x24
	POP      {r4, r5, r6, pc}
|loc_08024478|
	STRB     r0, [r4]
	STRB     r6, [r4, #1]
	LDR      r0, [r5, #0x3c]
	STRB     r0, [r4, #3]
	MOV      r0, #4
	POP      {r4, r5, r6, pc}
|loc_08024484|
	LDR      r0, [r5, #0x2c]
	STRB     r0, [r4]
	LDR      r0, [r5, #0x3c]
	STRB     r0, [r4, #1]
	MOV      r0, #2
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r1, #0
	SUB      r1, r2, #3
	CMP      r1, #5
	BCS      |loc_080244BC|
	ADD      r3, pc, #0x8
	LDRB     r3, [r3, r1]
	LSL      r3, r3, #1
	ADD      pc, r3
	LSL      r0, r0, #0
|loc_080244A4|
	LSR      r5, r1, #0x14
	LSL      r5, r1, #0xc
	LSL      r3, r3, #0
	MOV      r2, #0xff
	ADD      r2, #0x3d
	MOV      r1, #0
	STR      r1, [r2, r0]
	ADD      r0, #0xff
	ADD      r0, #0x41
	STR      r1, [r0]
	LDR      r0, [pc, #0xb0]
	STR      r1, [r0, #4]
|loc_080244BC|
	POP      {r4, r5, r6, pc}
	LDR      r0, [pc, #0xb0]
	LDR      r0, [r0]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BNE      |loc_080244BC|
	LDR      r1, [pc, #0x8c]
	MOV      r0, #1
	STR      r0, [r1]
	POP      {r4, r5, r6, pc}
|sub_080244DA|
|unk_080244DA|
	INCBIN	baserom.gba_0x244da_0x244ec.extracted
|sub_080244EC|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x41
	LDR      r0, [r6]
	CMP      r0, #0
	BEQ      |sub_08024528|
	CMP      r0, #1
	BEQ      |loc_08024532|
	CMP      r0, #2
	BEQ      |loc_08024548|
	CMP      r0, #3
	BNE      |loc_08024512|
	LDRB     r1, [r4, #1]
	MOV      r0, #1
	CMP      r1, #0
	BNE      |loc_0802450E|
	MOV      r0, #0
|loc_0802450E|
	LDR      r1, [pc, #0x5c]
	STR      r0, [r1, #4]
|loc_08024512|
	LDRB     r0, [r4]
	LDR      r1, [pc, #0x54]
	STR      r0, [r1]
	MOV      r0, #1
	STR      r0, [r5, #0x3c]
	LDRB     r2, [r4, #1]
	CMP      r2, #0
	BNE      |loc_08024524|
	MOV      r0, #0
|loc_08024524|
	STR      r0, [r1, #4]
	POP      {r4, r5, r6, pc}
|sub_08024528|
|unk_08024528|
		MOV r2, #0x20
		ADD r1, r4, #4
		LDR r0, [r5, #0x34]
		BL       |sub_08049138|
|loc_08024532|
|unk_08024532|
		LDR r1, [pc, #0x38]
		MOV r0, #0
		STR r0, [r1]
		MOV r0, #1
		STR r0, [r5, #0x3c]
		LDRB r1, [r4, #3]
		CMP r1, #0
		BEQ      |loc_08024544|
		MOV r0, #2
|loc_08024544|
		STR r0, [r6]
		B        |loc_08024512|
|loc_08024548|
|unk_08024548|
; cited by 0x0802431A (a pc-relative load targets 0x08024558)
		LDRB r1, [r4]
		MOV r0, #2
		CMP r1, #0
		BEQ      |loc_08024552|
		MOV r0, #3
|loc_08024552|
		STR r0, [r6]
		B        |loc_08024512|
	INCBIN  baserom.gba_0x24556_0x2455e.extracted
|sub_0802455E|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	LDR      r6, [sp, #0x190]
	LSR      r4, r0, #0x20
	CMP      r7, #0xb0
	LSL      r0, r0, #0xc
	STMIA    r3!, {r3, r7}
	LSR      r2, r6, #1
	PUSH     {r4, r5, r6, lr}
	BL       |loc_08024120|
	MOV      r0, #0xff
	ADD      r0, #0x2d
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_080245C8|
	LDR      r0, [pc, #0x114]
	MOV      r1, #0xff
	STR      r0, [r4]
	MOV      r0, #5
	ADD      r1, #0x15
	STRB     r0, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	MOV      r6, #0
	STR      r6, [r5, #0x1c]
	SUB      r1, r0, #6
	ADD      r0, r4, #0
	STR      r6, [r5, #0x20]
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0xe8]
	LDR      r1, [pc, #0xec]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0xe4]
	STR      r6, [r0]
	LDR      r0, [pc, #0xe8]
	STR      r6, [r1]
	STR      r0, [r4]
	STR      r6, [r1]
|loc_080245C8|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x29dc
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	BL       |sub_0802426E|
	POP      {r3, pc}
	LDR      r1, [pc, #0xcc]
	PUSH     {r3, lr}
	LDR      r1, [r1]
	CMP      r1, #0
	BEQ      |sub_080245FA|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	LDR      r2, [r1, #0x18]
	ADD      r2, #1
	STR      r2, [r1, #0x18]
	CMP      r2, #0xa
	BLE      |sub_080245FA|
	BL       |inc_0x03d784_0x041118| + 0x29fe
	MOV      r0, #2
	POP      {r3, pc}
|sub_080245FA|
|unk_080245FA|
		BL       |loc_080067F4|
		DCW     0xE7FB
|sub_08024600|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0xac]
	ADD      r4, r1, #0
	LDR      r0, [r5]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |sub_08024626|
	MOV      r2, #0x10
	ADD      r0, r4, #0
	LDR      r1, [r5, #4]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r0, #0x10
	POP      {r3, r4, r5, pc}
|sub_08024626|
|unk_08024626|
		LDR r0, [pc, #0x80]
		LDR r0, [r0]
		STRB r0, [r4]
		MOV r0, #1
		DCW     0xE7F9
|sub_08024630|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	SUB      r0, r2, #3
	CMP      r0, #5
	BCS      |loc_08024664|
	ADD      r3, pc, #0x8
	LDRB     r3, [r3, r0]
	LSL      r3, r3, #1
	ADD      pc, r3
	LSL      r0, r0, #0
|loc_08024644|
	ASR      r0, r2, #0x20
	LSL      r1, r2, #0xc
	LSL      r3, r0, #0
	LDR      r0, [pc, #0x64]
	LDR      r0, [r0]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BNE      |loc_08024664|
	LDR      r1, [pc, #0x48]
	MOV      r0, #1
	STR      r0, [r1]
|loc_08024664|
	POP      {r3, r4, r5, pc}
|sub_08024666|
|unk_08024666|
; cited by 0x08024586 (a pc-relative load targets 0x0802469C)
	INCBIN	baserom.gba_0x24666_0x246a2.extracted
|sub_080246A2|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	ADD      r1, pc, #0x3D0
	LSR      r4, r0, #0x20
	STMIA    r3!, {r2, r3, r7}
	LSR      r2, r6, #1
|loc_080246B4|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080246CE|
	MOV      r0, #0x58
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080246CE|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_080246CE|
|unk_080246CE|
		ADD r2, r6, #0
		MOV r1, #0x40
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x264]
		STR r0, [r4]
		ADD r0, r4, #0
		BL       |sub_08011568|
		LDR r7, [pc, #0x260]
		LDRB r0, [r7]
		ADD r1, r0, #1
		STRB r1, [r7]
		CMP r0, #0
		BNE      |loc_08024710|
		LDR r0, [pc, #0x258]
		MOV r1, #0x13
		LSL r1, r1, #8
		LDR r0, [r0]
		BL       |loc_0801124C|
		LSL r0, r0, #0x10
		ASR r0, r0, #0x10
		STRH r0, [r7, #2]
		LDR r1, [pc, #0x248]
		LSL r0, r0, #5
		ADD r0, r0, r1
		MOV r2, #0x13
		LSL r2, r2, #8
		LDR r1, [pc, #0x244]
		BL       |sub_08049138|
|loc_08024710|
		LDR r1, [r5]
		LDR r2, [r5, #4]
		LDRB r6, [r6, #0x10]
		MOV r0, #0
		STR r0, [r4, #0x50]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		MOV r1, #0x44
		STRB r0, [r1, r4]
		STR r0, [r4, #0x40]
		LSL r0, r6, #4
		SUB r0, r0, r6
		LDR r1, [pc, #0x224]
		LSL r0, r0, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x54]
		STR r0, [r4, #0x18]
		MOV r0, #0xc0
		BL       |inc_0x03d784_0x041118| + 0x2348
		LSL r5, r6, #3
		LDR r6, [pc, #0x208]
		ADD r6, #4
		LDR r1, [r6, r5]
		ADD r0, r0, r1
		SUB r0, #0x60
		STR r0, [r4, #0x48]
		MOV r0, #0xc0
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r1, r5, r6
		LDR r1, [r1, #4]
		ADD r0, r0, r1
		SUB r0, #0x60
		STR r0, [r4, #0x4c]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		DCW     0xE7B1
|sub_08024768|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1d0]
	SUB      sp, #4
	LDR      r5, [pc, #0x1d0]
	STR      r0, [r4]
	LDRB     r0, [r5]
	LDR      r7, [pc, #0x1d0]
	LDR      r6, [pc, #0x1dc]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r5]
	BNE      |loc_0802479A|
	LDRH     r0, [r5, #2]
	CMP      r0, r6
	BEQ      |loc_0802479A|
	MOV      r3, #2
	LDRSH    r1, [r5, r3]
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x112d2
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r5, #2]
|loc_0802479A|
	LDR      r0, [pc, #0x1c0]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	CMP      r1, r6
	BEQ      |loc_080247AA|
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080247AA|
	LDR      r0, [pc, #0x1b4]
	STR      r0, [r4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_080247BA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080247BA|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	ADD      r0, #0x48
	ADD      r5, r1, #0
	LDR      r1, [r4, #0x20]
	LDMIA    r0!, {r2}
	SUB      sp, #0x48
	ADD      r1, r1, r2
	STR      r1, [r4, #0x20]
	LDR      r1, [r4, #0x24]
	LDR      r0, [r0]
	ADD      r0, r1, r0
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x50]
	ADD      r0, #1
	STR      r0, [r4, #0x50]
	ASR      r0, r0, #2
	LSL      r1, r0, #0x18
	LSR      r1, r1, #0x18
	MOV      r0, #0x44
	STRB     r1, [r0, r4]
	CMP      r1, #4
	BLS      |sub_080247FA|
	LDR      r0, [pc, #0x158]
	ADD      r1, r4, #0
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x48
	POP      {r4, r5, r6, pc}
|sub_080247FA|
|unk_080247FA|
		LSL r3, r1, #1
		ADD r1, r3, r1
		LDR r0, [r4, #0x54]
		LSL r1, r1, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		CMP r5, #0
		DCW     0xD0F2
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		DCW     0xD0EF
		LDR r0, [r4, #0x40]
		CMP r0, #0
		DCW     0xD1EC
		LDR r0, [pc, #0x144]
		LDR r5, [r0]
		CMP r5, #0
		DCW     0xD0E8
		MOV r0, #0xff
		ADD r0, #0xcd
		LDR r0, [r0, r5]
		CMP r0, #0
		DCW     0xD0E3
		LDR r0, [r4, #0x20]
		LDR r1, [r4, #0x24]
		ASR r0, r0, #8
		SUB r0, #8
		STR r0, [sp, #0x18]
		ASR r1, r1, #8
		SUB r1, #8
		ADD r0, #0x10
		STR r0, [sp, #0x20]
		ADD r0, r1, #0
		ADD r0, #0x10
		STR r0, [sp, #0x24]
		STR r1, [sp, #0x1c]
		ADD r1, r5, #0
		ADD r0, sp, #4
		ADD r6, sp, #0x28
		BL       |loc_0800FE78|
		LDR r0, [sp, #4]
		LDR r1, [sp, #0x20]
		CMP r0, r1
		DCW     0xDACD
		LDR r0, [sp, #0x18]
		LDR r1, [sp, #0xc]
		CMP r0, r1
		DCW     0xDAC9
		LDR r0, [sp, #8]
		LDR r1, [sp, #0x24]
		CMP r0, r1
		DCW     0xDAC5
		LDR r0, [sp, #0x1c]
		LDR r1, [sp, #0x10]
		CMP r0, r1
		DCW     0xDAC1
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0x20
		STR r0, [sp, #0x34]
		LDRB r0, [r4, #0x10]
		STRB r0, [r3, #8]
		LDR r0, [pc, #0xe8]
		STR r0, [sp, #0x30]
		LDR r0, [pc, #0xe8]
		BL       |sub_08054A64|
		STR r0, [sp, #0x2c]
		LDRB r0, [r4, #0x11]
		ADD r3, sp, #0
		LDR r1, [pc, #0xb4]
		STRB r0, [r3, #0x14]
		STR r4, [sp, #0x44]
		MOV r0, #1
		STR r0, [r4, #0x40]
		LDR r0, [pc, #0xd8]
		LDR r0, [r0, #4]
		LDR r2, [r1, #4]
		SUB r2, r0, r2
		CMP r2, #0x80
		BLE      |loc_080248A4|
		STR r0, [r1, #4]
|loc_080248A4|
		ADD r1, r6, #0
		ADD r0, r5, #0
		BL       |sub_0800E9D8|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x5c]
		ADD r2, r2, r1
		ADD r1, r6, #0
		BL       |loc_08046AA4|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #0x17
		BL       |loc_08046AA4|
		CMP r0, #0
		DCW     0xD094
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		DCW     0xE78C
|sub_080248DC|
	PUSH     {r4}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	LDR      r4, [pc, #0x90]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	LDR      r2, [r0, #0x18]
	LDR      r2, [r2, #4]
	STR      r2, [r1]
	LDR      r3, [r0, #0x38]
	AND      r2, r4
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x3c]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x18]
	LDR      r2, [pc, #0x34]
	LDR      r4, [pc, #0x40]
	LDR      r3, [r3, #8]
	LDRH     r2, [r2, #2]
	SUB      r3, r3, r4
	ASR      r3, r3, #5
	ADD      r2, r2, r3
	LDR      r3, [r1, #4]
	LSL      r2, r2, #0x16
	LSR      r3, r3, #0xa
	LSL      r3, r3, #0xa
	LSR      r2, r2, #0x16
	ORR      r2, r3
	STR      r2, [r1, #4]
	LDRB     r0, [r0, #8]
	MOV      r3, #3
	LSL      r3, r3, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r2, r3
	ORR      r0, r2
	STR      r0, [r1, #4]
	POP      {r4}
	MOV      r0, #0
	BX       lr
|sub_08024940|
	DCW      0xbfcc
	DCW      0x0804,0x2fb8,0x0300,0xc394,0x0872,0x0000,0x0601,0xc3b8
	DCW      0x0872,0xd6b8,0x0872,0xffff,0x0000,0x9680,0x0804,0xe454
	DCW      0x0804,0x1c34,0x0300,0x80a8,0x086b,0xcccd,0x424c,0x0f90
	DCW      0x0300,0xffff
|sub_08024976|
|unk_08024976|
	INCBIN  baserom.gba_0x24976_0x24978.extracted
		PUSH {r3, r4, r5, lr}
	LDR      r4, [pc, #0xa0]
	LDR      r5, [pc, #0x98]
	CMP      r1, #0xa
	LDRB     r3, [r4]
	BEQ      |sub_080249B4|
	CMP      r1, #0xb
	BNE      |loc_080249DA|
	ADD      r0, r3, #1
	STRB     r0, [r4]
	CMP      r3, #0
	BNE      |loc_080249B0|
	MOV      r1, #0x13
	LSL      r1, r1, #8
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x110f4
	LSL      r0, r0, #0x10
	ASR      r0, r0, #0x10
	STRH     r0, [r4, #2]
	LDR      r1, [pc, #0x7c]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	MOV      r2, #0x13
	LSL      r2, r2, #8
	LDR      r1, [pc, #0x78]
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080249B0|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
|sub_080249B4|
|unk_080249B4|
		ADD r3, #0xff
		LSL r0, r3, #0x18
		LSR r0, r0, #0x18
		STRB r0, [r4]
		BNE      |loc_080249D6|
		LDRH r0, [r4, #2]
		LDR r1, [pc, #0x64]
		CMP r0, r1
		BEQ      |loc_080249D6|
		MOV r3, #2
		LDRSH r1, [r4, r3]
		LDR r0, [r5]
		BL       |loc_0801142A|
		MOV r0, #0
		MVN r0, r0
		STRH r0, [r4, #2]
|loc_080249D6|
		MOV r0, #0
		DCW     0xE7EB
|loc_080249DA|
|unk_080249DA|
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		DCW     0xE7E8
|sub_080249E0|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r4, [pc, #0x30]
	ADD      r6, r1, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #5
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_08024A14|
	LDR      r0, [r4]
	MOV      r1, #0x80
	LDR      r0, [r0, #4]
	SUB      r0, r1, r0
	CMP      r0, #4
	BLT      |loc_08024A14|
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |loc_080246B4|
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08024A14|
	POP      {r4, r5, r6, pc}
|sub_08024A16|
	DCW      0x0000
	DCW      0xc394,0x0872,0x2fb8,0x0300,0x0000,0x0601,0xc3b8,0x0872
	DCW      0xffff
|sub_08024A2A|
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08024A44|
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08024A44|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
|sub_08024A44|
|unk_08024A44|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x9994
		LDR r0, [pc, #0x28]
		STR r0, [r4]
		ADD r0, r4, #0
		DCW     0xE7F6
|sub_08024A54|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08024A66|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
|sub_08024A66|
|unk_08024A66|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x9994
		LDR r0, [pc, #8]
		STR r0, [r4]
		ADD r0, r4, #0
		DCW     0xE7F6
|sub_08024A76|
	LSL      r0, r0, #0
	LDR      r1, [sp, #0x350]
	LSR      r4, r0, #0x20
|loc_08024A7C|
	PUSH     {r3, lr}
	CMP      r0, #0
|loc_08024A80|
	BNE      |loc_08024A8C|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08024A9A|
|loc_08024A8C|
	LDR      r1, [pc, #0x2b4]
	STR      r1, [r0]
	MOV      r1, #0
	STRB     r1, [r0, #5]
	STRB     r1, [r0, #6]
	STR      r1, [r0, #8]
	STRB     r1, [r0, #4]
|loc_08024A9A|
	POP      {r3, pc}
|loc_08024A9C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x2a4]
	ADD      r4, r1, #0
	SUB      sp, #0x14
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x119ac
	MOV      r2, #0x40
	MOV      r1, #0
	MOV      r0, #3
	LSL      r0, r0, #0x19
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x40
	LDR      r1, [pc, #0x290]
	LDR      r0, [pc, #0x290]
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r1, [pc, #0x290]
	CMP      r4, #0
	BNE      |loc_08024ACA|
	MOV      r1, #0
|loc_08024ACA|
	MOV      r7, #1
	LSL      r7, r7, #0xb
	ADD      r2, r7, #0
	LDR      r0, [pc, #0x284]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #1
	STRB     r0, [r5, #4]
	LSL      r0, r0, #0xc
	BL       |GBARam_Malloc|
	LDR      r6, [pc, #0x264]
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	ADD      r6, #0x10
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x1bc
	ADD      r1, r4, #0
	LDR      r0, [pc, #0x268]
	LDR      r2, [r6, #4]
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r1, r4, #0
	LDR      r0, [pc, #0x264]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LSR      r3, r7, #1
	ADD      r6, r3, #0
	ADD      r0, r4, #0
	MOV      r1, #0
	SUB      r6, #0x88
|loc_08024B0A|
	LDRH     r2, [r0]
	ADD      r1, #1
	ADD      r2, r2, r6
	STRH     r2, [r0]
	ADD      r0, #2
	CMP      r1, r3
	BLT      |loc_08024B0A|
	ADD      r2, r7, #0
	LDR      r7, [pc, #0x248]
	ADD      r1, r4, #0
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x2c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_08024B60|
	LDR      r0, [pc, #0x214]
	ADD      r1, r4, #0
	SUB      r0, #0xd8
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r2, #0xff
	ADD      r2, #1
	ADD      r1, r4, #0
	LDR      r0, [pc, #0x220]
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #2
	STR      r0, [sp, #0xc]
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	ADD      r1, r7, #0
	STR      r6, [sp, #4]
	STR      r6, [sp, #8]
	LDR      r2, [pc, #0x210]
	BL       |inc_0x03d784_0x041118| + 0x28c
|loc_08024B60|
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x30]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_08024B9E|
	LDR      r0, [pc, #0x1d8]
	ADD      r1, r4, #0
	SUB      r0, #0x78
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r2, #0xff
	ADD      r2, #1
	ADD      r1, r4, #0
	LDR      r0, [pc, #0x1ec]
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0x1c
	STR      r0, [sp, #4]
	MOV      r0, #0x1e
	STR      r0, [sp, #0xc]
	MOV      r0, #2
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	ADD      r1, r7, #0
	STR      r6, [sp, #8]
	LDR      r2, [pc, #0x1d8]
	BL       |inc_0x03d784_0x041118| + 0x28c
|loc_08024B9E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
	MOV      r0, #0x3b
	LSL      r0, r0, #7
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	STRH     r0, [r1, #8]
	LDR      r0, [pc, #0x1c8]
	LDR      r4, [pc, #0x194]
	STRH     r0, [r1, #0xe]
	STRH     r6, [r1, #0x10]
	STRH     r6, [r1, #0x12]
	STRH     r6, [r1, #0x1c]
	STRH     r6, [r1, #0x1e]
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x11458
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x11426
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0x1a8]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x1a0]
	LDR      r0, [pc, #0x1a0]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|loc_08024BE6|
	LDR      r1, [pc, #0x19c]
	LDR      r2, [pc, #0x19c]
	STRH     r1, [r2, #0x10]
	MOV      r1, #1
	STR      r1, [r0, #8]
	BX       lr
	LDRB     r1, [r0, #5]
	CMP      r1, #0
	BEQ      |loc_08024C02|
	LDR      r1, [pc, #0x190]
	LDR      r2, [pc, #0x18c]
	STRH     r1, [r2, #0x10]
	MOV      r1, #1
	STR      r1, [r0, #8]
|loc_08024C02|
	BX       lr
	PUSH     {r3, lr}
	LDRB     r1, [r0, #6]
	CMP      r1, #1
	BEQ      |sub_08024C22|
	CMP      r1, #2
	BNE      |loc_08024C34|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x38]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r3, pc}
|sub_08024C22|
|unk_08024C22|
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #0
		DCW     0xE7F5
|loc_08024C34|
|unk_08024C34|
		MOV r0, #1
		DCW     0xE7F3
|sub_08024C38|
	PUSH     {r4, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r4, [pc, #0x100]
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x118c6
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x11458
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0xf0]
	SUB      sp, #0x1fc
	ADD      r4, r0, #0
	LDR      r0, [r7, #4]
	SUB      sp, #8
	BL       |inc_0x0158_0x143f2| + 0x11426
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x40]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #8]
	CMP      r0, #0
	BEQ      |sub_08024C98|
	LDRB     r0, [r4, #5]
	LDR      r1, [pc, #0x114]
	ADD      r0, #0xff
	STRB     r0, [r4, #5]
	STRB     r0, [r1, #2]
	LDRB     r0, [r4, #5]
	CMP      r0, #0
	BNE      |loc_08024D40|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      sp, #0x1fc
	ADD      sp, #8
	POP      {r4, r5, r6, r7, pc}
|sub_08024C98|
|unk_08024C98|
		LDR r7, [pc, #0xac]
		MOV r6, #1
		LDR r0, [r7]
		LDR r5, [pc, #0xe4]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x16
		LSR r0, r0, #0x1f
		CMP r0, #0
		BEQ      |loc_08024CD8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x2c]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_08024CD8|
		LDR r0, [pc, #0xcc]
		STRB r6, [r4, #6]
		STRH r5, [r0, #0x10]
		LDR r0, [pc, #0x88]
		ADD r7, sp, #4
		ADD r1, r7, #0
		SUB r0, #0xd8
		STR r6, [r4, #8]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LSL r2, r6, #8
		ADD r1, r7, r2
		LDR r0, [pc, #0x94]
		BL       |sub_08049138|
|loc_08024CD8|
		LDR r7, [pc, #0x6c]
		LDR r0, [r7]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x17
		LSR r0, r0, #0x1f
		BEQ      |loc_08024D16|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x30]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_08024D16|
		MOV r0, #2
		STRB r0, [r4, #6]
		LDR r0, [pc, #0x8c]
		STRH r5, [r0, #0x10]
		LDR r0, [pc, #0x4c]
		ADD r5, sp, #4
		ADD r1, r5, #0
		SUB r0, #0x78
		STR r6, [r4, #8]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		MOV r2, #0xff
		ADD r2, #1
		ADD r1, r5, r2
		LDR r0, [pc, #0x5c]
		BL       |sub_08049138|
|loc_08024D16|
		LDR r0, [r7]
		LDRH r0, [r0, #4]
		LSL r1, r0, #0x1e
		LSR r1, r1, #0x1f
		BNE      |loc_08024D26|
		LSL r0, r0, #0x1d
		LSR r0, r0, #0x1f
		BEQ      |loc_08024D32|
|loc_08024D26|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x1c]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
|loc_08024D32|
		LDRB r0, [r4, #5]
		CMP r0, #0x10
		BHS      |loc_08024D40|
		ADD r0, #1
		LDR r1, [pc, #0x54]
		STRB r0, [r4, #5]
		STRB r0, [r1, #2]
|loc_08024D40|
|unk_08024D40|
; cited by 0x08024A8C (a pc-relative load targets 0x08024D44)
		MOV r0, #0
		DCW     0xE7A6
	INCBIN  baserom.gba_0x24d44_0x24d94.extracted
|sub_08024D94|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x180]
	SUB      sp, #8
	LDR      r0, [r0, #0xc]
	MOV      r7, #2
	STR      r0, [r1, #0xc]
	STRB     r7, [r1, #3]
	ADD      r4, r1, #0
	MOV      r1, #1
	LDR      r0, [pc, #0x174]
	STRB     r1, [r4, #2]
	STR      r0, [r4, #0x20]
	MOV      r0, #0x38
	STR      r0, [r4, #4]
	MOV      r0, #0x90
	STR      r0, [r4, #8]
	MOV      r0, #8
	STRB     r0, [r4, #1]
	STRB     r1, [r4]
	CMP      r5, #0
	LDR      r6, [pc, #0x164]
	BEQ      |loc_08024DCE|
	LDRH     r0, [r5]
	LSL      r0, r0, #2
	LDR      r1, [r6, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
|loc_08024DCE|
	MOV      r7, #2
	STRB     r7, [r4, #3]
	MOV      r0, #0
	STRB     r0, [r4]
	MOV      r0, #0x16
	STR      r0, [r4, #8]
	MOV      r0, #0x5f
	MOV      r7, #0x70
	LDR      r6, [pc, #0x144]
	STR      r7, [r4, #4]
	LSL      r0, r0, #3
	LDR      r1, [r6, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r0, #0x20
	STR      r0, [r4, #8]
	MOV      r0, #0xbf
	LSL      r0, r0, #2
	STR      r7, [r4, #4]
	LDR      r1, [r6, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r0, #0x2a
	STR      r0, [r4, #8]
	MOV      r0, #3
	LSL      r0, r0, #8
	STR      r7, [r4, #4]
	LDR      r1, [r6, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r0, #0x34
	STR      r0, [r4, #8]
	MOV      r0, #0xc1
	LSL      r0, r0, #2
	STR      r7, [r4, #4]
	LDR      r1, [r6, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	MOV      r7, #2
	STRB     r7, [r4]
	STRB     r7, [r4, #3]
	SUB      r6, r7, #3
	ADD      r7, r6, #0
	CMP      r5, #0
	STR      r6, [sp, #4]
	LDR      r2, [sp, #0x10]
	BEQ      |sub_08024E88|
	LDR      r0, [r5, #0xc]
	CMP      r0, r6
	BEQ      |sub_08024E88|
	CMP      r0, #0
	BGE      |sub_08024E70|
	ADD      r0, #2
|unk_08024E40|
	INCBIN	baserom.gba_0x24e40_0x24e42.extracted
	MOV      r3, #0x68
	LDR      r0, [pc, #0xd4]
	MUL      r1, r3
	LDR      r0, [r0, #8]
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	CMP      r2, r6
	BNE      |loc_08024E5E|
	ADD      r1, r0, #0
	ADD      r1, #0x16
	MOV      r3, #0
	LDRSH    r2, [r1, r3]
|loc_08024E5E|
	ADD      r1, r0, #0
	ADD      r1, #0x4c
	LDRH     r6, [r1]
	STR      r6, [sp, #4]
	ADD      r1, #2
	LDRH     r6, [r1]
	ADD      r0, #0x50
	LDRH     r7, [r0]
	B        |sub_08024E88|
|sub_08024E70|
|unk_08024E70|
		LSL r3, r0, #3
		SUB r0, r3, r0
		LDR r1, [pc, #0xb0]
		LSL r0, r0, #2
		ADD r0, r0, r1
		ADD r3, r2, #1
		BNE      |loc_08024E80|
		LDR r2, [r0, #4]
|loc_08024E80|
		LDRB r6, [r0, #0xd]
		STR r6, [sp, #4]
		LDRB r6, [r0, #0xe]
		LDRB r7, [r0, #0xf]
|sub_08024E88|
	MOV      r0, #0xa0
	STR      r0, [r4, #4]
	MOV      r0, #0x16
	STR      r0, [r4, #8]
	ADD      r3, r2, #1
	BNE      |sub_08024E98|
	ADD      r1, pc, #0x94
	B        |loc_08024E9A|
|sub_08024E98|
|unk_08024E98|
		ADR      r1, |loc_08024F34|
|loc_08024E9A|
|unk_08024E9A|
		ADD r0, r4, #0
		BL       |sub_0803DC96|
		MOV r0, #0xa0
		STR r0, [r4, #4]
		MOV r0, #0x20
		STR r0, [r4, #8]
		LDR r0, [sp, #4]
		ADD r3, r0, #1
		BNE      |loc_08024EB2|
		ADR      r1, |loc_08024F2C|
		B        |loc_08024EB4|
|loc_08024EB2|
		ADR      r1, |loc_08024F34|
|loc_08024EB4|
		ADD r0, r4, #0
		LDR r2, [sp, #4]
		BL       |sub_0803DC96|
		MOV r0, #0xa0
		STR r0, [r4, #4]
		MOV r0, #0x2a
		STR r0, [r4, #8]
		ADD r3, r6, #1
		BNE      |loc_08024ECC|
		ADR      r1, |loc_08024F2C|
		B        |loc_08024ECE|
|loc_08024ECC|
		ADR      r1, |loc_08024F34|
|loc_08024ECE|
		ADD r2, r6, #0
		ADD r0, r4, #0
		BL       |sub_0803DC96|
		MOV r0, #0xa0
		STR r0, [r4, #4]
		MOV r0, #0x34
		STR r0, [r4, #8]
		ADD r3, r7, #1
		BNE      |sub_08024EE6|
		ADR      r1, |loc_08024F2C|
		DCW     0xE000
|sub_08024EE6|
	ADD      r1, pc, #0x4C
	ADD      r2, r7, #0
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x512
	CMP      r5, #0
	BEQ      |loc_08024EFA|
	LDR      r0, [r5, #8]
	CMP      r0, #0
	BNE      |loc_08024F16|
|loc_08024EFA|
	MOV      r0, #0xc8
	STR      r0, [r4, #4]
	MOV      r0, #0x22
	STR      r0, [r4, #8]
	MOV      r1, #1
	STRB     r1, [r4]
	MOV      r0, #0x61
	LDR      r6, [pc, #0x18]
	LSL      r0, r0, #3
	LDR      r2, [r6, r0]
	MOV      r1, #0x38
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x5e2
|loc_08024F16|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	ASR      r0, r3, #0x17
	LSR      r3, r6, #1
	DCW      0xf5a5,0x0803
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	ASR      r4, r6, #9
	LSR      r1, r6, #1
|loc_08024F2C|
	LSL      r7, r7, #0
	LSL      r7, r7, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
|loc_08024F34|
	LSL      r5, r4, #0
	LSL      r4, r4, #1
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	BNE      |sub_08024F52|
	MOV      r0, #0x59
	LSL      r0, r0, #5
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08024F52|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08024F52|
|unk_08024F52|
		ADD r0, r4, #0
		BL       |loc_08024A7C|
		LDR r0, [pc, #0x3ac]
		ADD r1, r4, #0
		STR r0, [r4]
		MOV r0, #0
		MOV r2, #0xed
		LSL r2, r2, #2
		ADD r1, #0x10
		ADD r2, r4, r2
		STR r0, [r4, #0x10]
		LDR r6, [pc, #0x3a0]
		STR r0, [r2]
|loc_08024F6E|
		LDR r3, [r6, #8]
		ASR r5, r0, #3
		ADD r3, r5, r3
		ADD r3, #0xc0
		LSL r7, r0, #0x1d
		LSR r7, r7, #0x1d
		LDRB r3, [r3, #5]
		MOV r5, #1
		LSL r5, r7
		AND r3, r5
		BEQ      |loc_08024F90|
		LDR r3, [r1]
		ADD r5, r3, #1
		LSL r3, r3, #2
		ADD r3, r3, r1
		STR r5, [r1]
		STR r0, [r3, #4]
|loc_08024F90|
		ADD r0, #1
		CMP r0, #0xe8
		BLT      |loc_08024F6E|
		LDR r5, [r4, #0x10]
		MOV r3, #0
		MOV r0, #0
		CMP r5, #0
		BLE      |loc_08024FD6|
		LDR r7, [pc, #0x36c]
|loc_08024FA2|
		LSL r5, r0, #2
		ADD r5, r5, r1
		LDR r5, [r5, #4]
		LSL r5, r5, #4
		ADD r5, r5, r7
		LDRH r5, [r5]
		CMP r3, r5
		BEQ      |loc_08024FC6|
		ADD r3, r5, #0
		LDR r5, [r2]
		ADD r6, r5, #1
		LSL r5, r5, #3
		ADD r5, r5, r2
		ADD r5, #4
		STR r6, [r2]
		STR r0, [r5]
		STR r0, [r5, #4]
		B        |loc_08024FCE|
|loc_08024FC6|
		LDR r5, [r2]
		LSL r5, r5, #3
		ADD r5, r5, r2
		STR r0, [r5]
|loc_08024FCE|
		LDR r5, [r4, #0x10]
		ADD r0, #1
		CMP r5, r0
		BGT      |loc_08024FA2|
|loc_08024FD6|
		MOV r0, #0x2b
		LSL r0, r0, #6
		ADD r0, r4, r0
		MOV r1, #0
		STR r1, [r0, #0x38]
		MOV r0, #0xb
		LSL r0, r0, #8
		ADD r0, r4, r0
		STR r1, [r0, #0xc]
		STRB r1, [r4, #0xe]
		STR r1, [r0, #0x10]
		STRB r1, [r4, #0xd]
		LDR r1, [r2]
		CMP r1, #0
		BEQ      |loc_08024FFA|
		LDR r1, [r2, #4]
		STR r1, [r0, #0x14]
		B        |loc_08025000|
|loc_08024FFA|
		MOV r1, #0
		MVN r1, r1
		STR r1, [r0, #0x14]
|loc_08025000|
		ADD r0, r4, #0
		DCW     0xE7A5
|sub_08025004|
	PUSH     {r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #0
	SUB      sp, #0x14
	STR      r0, [sp, #4]
	MOV      r0, #0xb
	LSL      r0, r0, #8
	ADD      r4, r5, r0
	LDR      r0, [r4, #0x18]
	ADD      r2, sp, #4
	STR      r0, [sp, #8]
	MOV      r0, #0x68
	STR      r0, [sp, #0xc]
	LDR      r0, [r4, #0x18]
	LDR      r1, [pc, #0x2f0]
	ADD      r0, #0x38
	STR      r0, [sp, #0x10]
	LDR      r0, [r4, #0xc]
	BL       |inc_0x049120_0x055620| + 0x3c
	MOV      r0, #0x2b
	LSL      r0, r0, #6
	ADD      r0, r5, r0
	LDR      r1, [r0, #0x3c]
	LDR      r2, [r4, #0x18]
	MOV      r0, #1
	CMP      r2, #0
	BGT      |loc_0802503E|
	MOV      r0, #0
|loc_0802503E|
	STR      r0, [r1, #0x20]
	LDR      r0, [r4]
	ADD      r4, #0x18
	LDMIA    r4!, {r1, r2}
	CMP      r1, r2
	BGE      |loc_0802504E|
	MOV      r1, #1
	B        |loc_08025050|
|loc_0802504E|
	MOV      r1, #0
|loc_08025050|
	STR      r1, [r0, #0x20]
	ADD      sp, #0x14
	POP      {r4, r5, pc}
|loc_08025056|
	PUSH     {r0, r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x2bc]
	MOV      r0, #0xb
	ADD      sp, r3
	MOV      r3, #0x21
	LSL      r3, r3, #7
	ADD      r3, sp
	LDR      r1, [r3]
	LSL      r0, r0, #8
	ADD      r4, r1, r0
	LDR      r0, [r4, #0x14]
	ADD      r1, #0x10
	SUB      r3, #0x80
	STR      r1, [r3, #0x7c]
	MOV      r7, #0
	ADD      r3, r0, #1
	BEQ      |loc_0802508C|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r1, [r3, #0x7c]
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x288]
	LSL      r0, r0, #4
	ADD      r7, r0, r1
|loc_0802508C|
	LDR      r0, [r4, #0xc]
	CMP      r0, #0
	BEQ      |loc_0802509C|
	MOV      r1, #1
	BL       |inc_0x03d784_0x041118| + 0x1e08
	MOV      r1, #0
	STR      r1, [r4, #0xc]
|loc_0802509C|
	LDR      r5, [pc, #0x27c]
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	ADD      r5, sp
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r3, #1
	LSL      r3, r3, #0xc
	LDR      r0, [pc, #0x25c]
	ADD      r3, sp
	LDR      r1, [r3, #0x68]
	ADD      r0, #0x14
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r2, #0
	MVN      r2, r2
	ADD      r1, r5, #0
	ADD      r0, r7, #0
	BL       |sub_08024D94|
	CMP      r7, #0
	BEQ      |loc_080250F4|
	LDR      r0, [r7, #8]
	CMP      r0, #0
	BEQ      |loc_080250F4|
	LDR      r0, [r7, #8]
	BL       |inc_0x0158_0x143f2| + 0x11dc8
	ADD      r5, sp, #0x44
	ADD      r1, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [pc, #0x240]
	ADD      r6, sp, #0x34
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r6!, {r0, r1, r2, r3}
	SUB      r6, #0x10
	LDR      r0, [pc, #0x230]
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	ADD      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x219e
|loc_080250F4|
	LDR      r0, [pc, #0x224]
	LDR      r1, [pc, #0x22c]
	ADD      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x2234
	MOV      r3, #0x21
	LSL      r3, r3, #7
	ADD      r3, sp
	LDR      r2, [r3]
	MOV      r1, #0x2b
	LSL      r1, r1, #6
	ADD      r1, r2, r1
	SUB      r3, #0x80
	LDRB     r0, [r2, #0xe]
	STR      r1, [r3, #0x78]
	MOV      r1, #0xed
	LSL      r1, r1, #2
	ADD      r6, r2, r1
	CMP      r0, #0
	BNE      |loc_08025202|
	MOV      r0, #0x68
	STR      r0, [r3, #0x6c]
	MOV      r0, #0x38
	STR      r0, [r3, #0x70]
	MOV      r0, #0x5b
	LSL      r0, r0, #6
	STR      r0, [r3, #0x74]
	LDR      r0, [r3, #0x6c]
	LDR      r1, [r3, #0x70]
	STR      r0, [r3, #0x5c]
	STR      r1, [r3, #0x60]
	MOV      r2, #0x5b
	LSL      r2, r2, #6
	MOV      r1, #0
	LDR      r0, [r3, #0x68]
	BL       |inc_0x046118_0x049114| + 0xd28
	MOV      r3, #0x41
	LSL      r3, r3, #6
	ADD      r3, sp
	MOV      r1, #1
	STRB     r1, [r3, #4]
	LDR      r0, [r6]
	MOV      r1, #0x34
	CMP      r0, #0
	BEQ      |sub_080251D4|
	LDR      r2, [r4, #0x10]
	SUB      r3, #0x40
	SUB      r5, r2, #3
	ADD      r2, #4
	CMP      r0, r2
	STR      r5, [r3, #0x40]
	BGT      |loc_08025162|
	SUB      r0, #7
	STR      r0, [r3, #0x40]
|loc_08025162|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r0, [r3, #0x40]
	CMP      r0, #0
	BGE      |loc_08025172|
	MOV      r0, #0
	STR      r0, [r3, #0x40]
|loc_08025172|
	MOV      r5, #0
|loc_08025174|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r0, [r3, #0x40]
	LDR      r1, [r6]
	ADD      r0, r5, r0
	CMP      r1, r0
	BLE      |sub_08025204|
	LSL      r1, r0, #3
	ADD      r1, r1, r6
	ADD      r1, #4
	MOV      ip, r1
	LDR      r2, [r4, #0x10]
	MOV      r1, #2
	CMP      r2, r0
	BEQ      |loc_08025196|
	MOV      r1, #0x75
|loc_08025196|
	MOV      r3, #0x41
	LSL      r3, r3, #6
	ADD      r3, sp
	STRB     r1, [r3, #7]
	LSL      r0, r5, #3
	ADD      r0, #7
	SUB      r3, #0x40
	STR      r0, [r3, #0x4c]
	MOV      r1, #0x34
	STR      r1, [r3, #0x48]
	MOV      r1, ip
	LDR      r1, [r1]
	LDR      r0, [r3, #0x7c]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x158]
	LSL      r0, r0, #4
	ADD      r0, r0, r1
	LDRH     r0, [r0]
	LDR      r1, [pc, #0x168]
	LSL      r0, r0, #2
	LDR      r1, [r1, r0]
	ADD      r0, r3, #0
	ADD      r0, #0x44
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r5, #1
	CMP      r5, #7
	BLT      |loc_08025174|
	B        |sub_08025204|
|sub_080251D4|
|unk_080251D4|
		MOV r3, #0x41
		LSL r3, r3, #6
		ADD r3, sp
		MOV r0, #3
		STRB r0, [r3, #7]
		MOV r0, #0x20
		SUB r3, #0x40
		STR r0, [r3, #0x4c]
		STR r1, [r3, #0x48]
		LDR r1, [pc, #0x140]
		MOV r0, #0xc3
		LSL r0, r0, #2
		LDR r1, [r1, r0]
		ADD r0, r3, #0
		ADD r0, #0x44
		BL       |loc_0803DADA|
		LDR r0, [r4, #4]
		MOV r1, #0
		STR r1, [r0, #0x20]
		LDR r0, [r4, #8]
		STR r1, [r0, #0x20]
		B        |sub_08025204|
|loc_08025202|
|unk_08025202|
		B        |loc_08025238|
|sub_08025204|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r1, [r3, #0x78]
	LDR      r0, [r1, #0x3c]
	LDR      r2, [r4, #0x10]
	MOV      r1, #1
	CMP      r2, #2
	BGT      |loc_08025218|
	MOV      r1, #0
|loc_08025218|
	STR      r1, [r0, #0x20]
	LDR      r0, [r4]
	LDR      r1, [r6]
	LDR      r2, [r4, #0x10]
	SUB      r1, #4
	CMP      r1, r2
	BLE      |sub_0802522A|
	MOV      r1, #1
	B        |loc_0802522C|
|sub_0802522A|
|unk_0802522A|
		MOV r1, #0
|loc_0802522C|
|unk_0802522C|
		STR r1, [r0, #0x20]
		LDR r0, [pc, #0xec]
		LDR r1, [pc, #0xe0]
		ADD r0, sp
		BL       |inc_0x03d784_0x041118| + 0x2234
|loc_08025238|
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r0, [r3, #0x78]
		LDR r5, [pc, #0xc8]
		LDR r0, [r0, #0x38]
		CMP r0, #0
		BEQ      |loc_08025250|
		ADD r1, r0, #0
		LDR r0, [r5, #0xc]
		BL       |loc_08011944|
|loc_08025250|
		CMP r7, #0
		DCW     0xD01C
		ADD r1, r7, #0
		MOV r0, #0
		BL       |sub_080272EC|
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r1, [r3, #0x78]
		ADD r3, #0x80
		STR r0, [r1, #0x38]
		LDR r2, [r3]
		LDRB r1, [r2, #0xe]
		CMP r1, #0
		BEQ      |loc_0802527C|
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #2
		BL       |loc_08046AA4|
|loc_0802527C|
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r0, [r3, #0x78]
		LDR r1, [r0, #0x38]
		LDR r0, [r5, #0xc]
	INCBIN  baserom.gba_0x25288_0x2528a.extracted
|sub_0802528A|
|unk_0802528A|
	INCBIN	baserom.gba_0x2528a_0x2528e.extracted
	MOV      r1, #0
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r0, [r3, #0x78]
	STR      r1, [r0, #0x38]
	LDR      r0, [pc, #0x80]
	MOV      r1, #0
	ADD      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	MOV      r3, #0x21
	LSL      r3, r3, #7
	ADD      r3, sp
	LDR      r2, [r3]
	LDRB     r0, [r2, #0xe]
	CMP      r0, #1
	BNE      |loc_08025330|
	LDR      r2, [r4, #0x1c]
	MOV      r1, #0x68
	ADD      r2, #0x38
	MOV      r0, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	STR      r0, [r4, #0xc]
	LDR      r1, [r5, #0x10]
	STR      r1, [r0, #0xc]
	LDR      r0, [r4, #0xc]
	MOV      r1, #2
	STRB     r1, [r0, #3]
	LDR      r0, [r4, #0xc]
	MOV      r1, #0
	STR      r1, [r0, #4]
	MOV      r1, #0xe
	STR      r1, [r0, #8]
	LDR      r1, [r4, #0xc]
	MOV      r0, #0x10
	STRB     r0, [r1, #1]
	LDR      r0, [r4, #0xc]
	MOV      r1, #0
	LDR      r2, [r0, #0x30]
	LDR      r0, [r0, #0x24]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDRH     r0, [r7, #2]
	LDR      r1, [pc, #0x3c]
	LSL      r0, r0, #2
	LDR      r2, [r1, r0]
	LDR      r0, [r4, #0xc]
	MOV      r1, #0x68
	BL       |inc_0x03d784_0x041118| + 0x5e2
	MOV      r3, #0x21
	LSL      r3, r3, #7
	ADD      r3, sp
	LDR      r0, [r3]
	BL       |sub_08025004|
	LDR      r3, [pc, #0x28]
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
|sub_08025308|
	DCW      0xa950
	DCW      0x0804,0x19cc,0x0873,0xd380,0x0874,0x9800,0x0600,0xef80
	DCW      0xffff,0x1044,0x0000,0x2350,0x0873,0x0040,0x0600,0xbce8
	DCW      0x0806,0x1084,0x0000
|loc_08025330|
|unk_08025330|
		LDR r1, [r6]
		MOV r0, #0
		CMP r1, #0
		BEQ      |loc_0802534A|
		LDR r1, [r4, #0x10]
		LSL r1, r1, #3
		ADD r1, r1, r6
		ADD r1, #4
		LDR r2, [r1]
		LDR r1, [r1, #4]
		CMP r2, r1
		BEQ      |loc_0802534A|
		MOV r0, #1
|loc_0802534A|
		LDR r1, [r4, #4]
		STR r0, [r1, #0x20]
		LDR r1, [r4, #8]
		STR r0, [r1, #0x20]
		DCW     0xE7D6
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDRB r0, [r0, #0xd]
		SUB sp, #0x34
		CMP r0, #0
		BEQ      |sub_080253E2|
		LDRB r0, [r4, #0xe]
		MOV r7, #0
		CMP r0, #0
		BEQ      |sub_0802536E|
		STRB r7, [r4, #0xe]
		STRB r7, [r4, #0xd]
		DCW     0xE030
|sub_0802536E|
	MOV      r1, #0xb
	LSL      r1, r1, #8
	ADD      r6, r4, r1
	LDR      r1, [r6, #0x14]
	ADD      r0, r4, #0
	ADD      r0, #0x10
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x334]
	LSL      r0, r0, #4
	ADD      r5, r0, r1
	MOV      r0, #0x68
	STR      r0, [sp, #8]
	MOV      r0, #0x38
	STR      r0, [sp, #0xc]
	LDR      r0, [pc, #0x32c]
	STR      r7, [sp]
	STR      r7, [sp, #4]
	LDR      r1, [r0, #0x10]
	ADD      r0, sp, #0x10
	MOV      r2, sp
	BL       |inc_0x03d784_0x041118| + 0x2f4
	LDRH     r0, [r5, #2]
	LDR      r1, [pc, #0x31c]
	LSL      r0, r0, #2
	LDR      r0, [r1, r0]
	MOV      r5, #0
	STR      r0, [sp, #4]
|loc_080253AA|
	MOV      r3, sp
	MOV      r2, #0x68
	ADD      r0, sp, #0x10
	LDR      r1, [sp, #4]
	BL       |inc_0x03d784_0x041118| + 0x6e6
	LDR      r0, [sp, #0xc]
	ADD      r5, #1
	CMP      r0, #0
	BEQ      |loc_080253AA|
	LSL      r0, r5, #4
	SUB      r0, #0x38
	STR      r0, [r6, #0x1c]
	BPL      |loc_080253C8|
	STR      r7, [r6, #0x1c]
|loc_080253C8|
	STR      r7, [r6, #0x18]
	STRB     r7, [r4, #0xc]
	MOV      r0, #1
	STRB     r0, [r4, #0xe]
	ADD      r0, r4, #0
	BL       |loc_08025056|
	STRB     r7, [r4, #5]
	STRB     r7, [r4, #6]
	STR      r7, [r4, #8]
	MOV      r0, #0
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
|sub_080253E2|
|unk_080253E2|
		ADD r0, r4, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x8812
		DCW     0xE7F9
|sub_080253EA|
	PUSH     {r3, lr}
	LDRB     r1, [r0, #0xe]
	CMP      r1, #1
	BNE      |sub_080253FE|
	BL       |loc_08024BE6|
	LDR      r0, [pc, #0x2cc]
	LDR      r1, [pc, #0x2cc]
	STRH     r0, [r1, #0x10]
	POP      {r3, pc}
|sub_080253FE|
|unk_080253FE|
		BL       |inc_0x1c3f2_0x2ab4c| + 0x8800
		DCW     0xE7FB
|sub_08025404|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x2b0]
	LDR      r2, [pc, #0x2b0]
	LDR      r0, [r0]
	LDR      r1, [pc, #0x2bc]
	LDRH     r0, [r0, #4]
	LDR      r2, [r2, #4]
	LDR      r7, [pc, #0x2b8]
	ADD      r1, r2, r1
	STR      r1, [sp]
	MOV      r1, #0xb
	MOV      r2, #0xed
	LSL      r2, r2, #2
	LSL      r1, r1, #8
	LSL      r0, r0, #0x19
	LSR      r0, r0, #0x1f
	ADD      r4, r5, r1
	ADD      r6, r5, r2
	CMP      r0, #0
	BEQ      |loc_08025452|
	LDR      r0, [r4, #0x10]
	CMP      r0, #0
	BEQ      |loc_08025452|
	SUB      r0, #1
	STR      r0, [r4, #0x10]
	LSL      r0, r0, #3
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	STR      r0, [r4, #0x14]
	ADD      r0, r5, #0
	BL       |loc_08025056|
	ADD      r1, r7, #0
	MOV      r3, #0
	MOV      r2, #0x40
	LDR      r0, [sp]
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08025452|
	LDR      r0, [pc, #0x268]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1f
	BEQ      |loc_08025486|
	LDR      r1, [r6]
	LDR      r0, [r4, #0x10]
	SUB      r1, #1
	CMP      r1, r0
	BLE      |loc_08025486|
	ADD      r0, #1
	STR      r0, [r4, #0x10]
	LSL      r0, r0, #3
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	STR      r0, [r4, #0x14]
	ADD      r0, r5, #0
	BL       |loc_08025056|
	ADD      r1, r7, #0
	MOV      r3, #0
	MOV      r2, #0x40
	LDR      r0, [sp]
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08025486|
	LDR      r0, [r6]
	CMP      r0, #0
	BEQ      |loc_080254A6|
	LDR      r0, [pc, #0x22c]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |loc_080254A6|
	ADD      r0, r5, #0
	BL       |loc_08024BE6|
	LDR      r0, [pc, #0x224]
	LDR      r1, [pc, #0x228]
	STRH     r0, [r1, #0x10]
	MOV      r0, #1
	STRB     r0, [r5, #0xd]
|loc_080254A6|
	POP      {r3, r4, r5, r6, r7, pc}
|loc_080254A8|
	PUSH     {r4, r5, r6, lr}
	LDR      r6, [pc, #0x210]
	ADD      r4, r0, #0
	LDR      r1, [r6]
	MOV      r2, #0xb
	LDRH     r1, [r1, #2]
	LSL      r2, r2, #8
	ADD      r5, r4, r2
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	MOV      r0, #0
	CMP      r1, #0
	BEQ      |loc_080254D4|
	LDR      r1, [r5, #0x18]
	CMP      r1, #0
	BEQ      |loc_080254D4|
	SUB      r1, #1
	STR      r1, [r5, #0x18]
	ADD      r0, r4, #0
	BL       |sub_08025004|
	MOV      r0, #1
|loc_080254D4|
	LDR      r1, [r6]
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x1f
	BEQ      |loc_080254F2|
	LDR      r1, [r5, #0x18]
	LDR      r2, [r5, #0x1c]
	CMP      r1, r2
	BGE      |loc_080254F2|
	ADD      r1, #1
	STR      r1, [r5, #0x18]
	ADD      r0, r4, #0
	BL       |sub_08025004|
	MOV      r0, #1
|loc_080254F2|
	LDRB     r1, [r4, #0xc]
	CMP      r1, r0
	BEQ      |loc_080254FA|
	STRB     r0, [r4, #0xc]
|loc_080254FA|
	LDR      r0, [r6]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |loc_0802550E|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_0802550E|
	POP      {r4, r5, r6, pc}
|sub_08025510|
|unk_08025510|
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		MOV r0, #0xed
		LSL r0, r0, #2
		ADD r0, r5, r0
		LDR r7, [pc, #0x1a0]
		STR r0, [sp]
		LDR r1, [r7]
		LDR r0, [r0]
		LDRH r1, [r1, #4]
		LSL r1, r1, #0x1a
		LSR r2, r1, #0x1f
		CMP r0, #0
		DCW     0xD040
		MOV r0, #0xb
		LSL r0, r0, #8
		ADD r4, r5, r0
		LDR r1, [sp]
		LDR r0, [r4, #0x10]
		LSL r0, r0, #3
		ADD r0, r0, r1
		ADD r0, #4
		LDR r3, [r0]
		LDR r6, [r0, #4]
		ADD r1, r3, #0
		CMP r3, r6
		DCW     0xD033
		ADD r6, r7, #0
		LDR r6, [r6, #4]
		LDR r3, [pc, #0x180]
		ADD r7, r6, r3
		LDR r6, [pc, #0x180]
		CMP r2, #0
		BEQ      |loc_08025574|
		LDR r2, [r4, #0x14]
		SUB r2, #1
		STR r2, [r4, #0x14]
		CMP r1, r2
		BLE      |loc_08025562|
		LDR r0, [r0, #4]
		STR r0, [r4, #0x14]
|loc_08025562|
		ADD r0, r5, #0
		BL       |loc_08025056|
		ADD r1, r6, #0
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08025574|
		LDR r0, [pc, #0x144]
		LDR r0, [r0]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		DCW     0xD016
		LDR r0, [sp]
		LDR r1, [r4, #0x10]
		LSL r1, r1, #3
		ADD r1, r1, r0
		LDR r0, [r4, #0x14]
		ADD r1, #4
		LDR r2, [r1, #4]
		ADD r0, #1
		STR r0, [r4, #0x14]
		CMP r2, r0
		BGE      |loc_0802559A|
		LDR r0, [r1]
		STR r0, [r4, #0x14]
|loc_0802559A|
		ADD r0, r5, #0
		BL       |loc_08025056|
		ADD r1, r6, #0
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r7, #0
	INCBIN  baserom.gba_0x255a8_0x255aa.extracted
|sub_080255AA|
|unk_080255AA|
	INCBIN	baserom.gba_0x255aa_0x255ae.extracted
	LDRB     r0, [r5, #0xe]
	CMP      r0, #0
	BEQ      |sub_080255BC|
	ADD      r0, r5, #0
	BL       |loc_080254A8|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_080255BC|
|unk_080255BC|
		ADD r0, r5, #0
		BL       |sub_08025404|
		DCW     0xE7FA
|sub_080255C4|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	MOV      r0, #3
	MOV      r2, #0x40
	MOV      r1, #0
	LSL      r0, r0, #0x19
	SUB      sp, #0x14
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0x1e
	STR      r0, [sp, #0xc]
	MOV      r0, #0x14
	MOV      r4, #0
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	STR      r4, [sp, #4]
	STR      r4, [sp, #8]
	MOV      r2, #1
	LDR      r1, [pc, #0xe8]
	BL       |inc_0x03d784_0x041118| + 0x28c
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0xe0]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0xf
	STR      r0, [sp, #4]
	MOV      r0, #0xb
	STR      r0, [sp, #8]
	MOV      r0, #0x1c
	STR      r0, [sp, #0xc]
	MOV      r0, #0x12
	STR      r0, [sp, #0x10]
	MOV      r2, #0x13
	LSL      r2, r2, #5
	ADD      r0, sp, #4
	LDR      r1, [pc, #0xc4]
	BL       |inc_0x03d784_0x041118| + 0x28c
	MOV      r1, #0
	MOV      r0, #0
	BL       |loc_080271D0|
	MOV      r1, #0xb
	LSL      r1, r1, #8
	ADD      r6, r5, r1
	LDR      r7, [pc, #0x94]
	STR      r0, [r6]
	ADD      r1, r0, #0
	LDR      r0, [r7, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r1, #1
	MOV      r0, #0
	BL       |loc_080271D0|
	MOV      r1, #0x2b
	LSL      r1, r1, #6
	ADD      r1, r5, r1
	STR      r0, [r1, #0x3c]
	ADD      r1, r0, #0
	LDR      r0, [r7, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r1, #2
	MOV      r0, #0
	BL       |loc_080271D0|
	ADD      r1, r0, #0
	STR      r0, [r6, #4]
	LDR      r0, [r7, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r1, #3
	MOV      r0, #0
	BL       |loc_080271D0|
	ADD      r1, r0, #0
	STR      r0, [r6, #8]
	LDR      r0, [r7, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r0, r5, #0
	BL       |loc_08025056|
	LDR      r1, [pc, #0x68]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #0xc]
	ADD      r1, #0xff
	ADD      r1, #1
	STRH     r1, [r0, #0xe]
	STRH     r4, [r0, #0x18]
	STRH     r4, [r0, #0x1a]
	STRH     r4, [r0, #0x1c]
	STRH     r4, [r0, #0x1e]
	MOV      r1, #0x52
	STRB     r4, [r1, r0]
	LDR      r1, [pc, #0x50]
	LDR      r2, [pc, #0x38]
	STRB     r4, [r1]
	LDR      r1, [pc, #0x50]
	STRH     r1, [r2, #0x10]
	MOV      r1, #0x71
	LSL      r1, r1, #6
	STRH     r1, [r0]
	LSR      r2, r0, #0x11
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0x44]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x38]
	LDR      r0, [pc, #0x3c]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_080256B8|
	DCW      0xd380
	DCW      0x0874,0x19cc,0x0873,0xbce8,0x0806,0x3e41,0x0000,0x0040
	DCW      0x0400,0x05c4,0x0000,0x947c,0x0831,0xf800
|sub_080256D6|
	LSL      r0, r0, #0x18
	DCW      0xf000,0x0600
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	LSL      r3, r2, #1
	LSL      r0, r0, #0x10
	SUB      r7, #0x5f
	LSL      r0, r0, #0
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	LSL      r0, r0, #8
	LSL      r0, r0, #0x14
|loc_080256F0|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BNE      |loc_08025704|
	LDR      r0, [pc, #0x3dc]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08025704|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_08025704|
	ADD      r0, r4, #0
	BL       |loc_08024A7C|
	LDR      r0, [pc, #0x3cc]
	MOV      r1, #0
	STR      r0, [r4]
	MOV      r0, #1
	LSL      r0, r0, #0xf
	ADD      r0, r4, r0
	STR      r1, [r0, #0x3c]
	LDR      r0, [pc, #0x3c0]
	ADD      r0, r4, r0
	STR      r1, [r0]
	STR      r1, [r0, #4]
	ADD      r1, #0xf0
	STR      r1, [r0, #8]
	LDR      r1, [r0, #4]
	ADD      r1, #0xa0
	STR      r1, [r0, #0xc]
	LDR      r0, [pc, #0x3b4]
	LDR      r0, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0x49b0
	LDR      r1, [pc, #0x3b0]
	ADD      r1, r4, r1
	STR      r0, [r1]
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_0802573C|
	LDR      r2, [pc, #0x3a8]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0802574A|
	BL       |GBARam_Free|
|loc_0802574A|
	POP      {r3, pc}
|loc_0802574C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	MOV      r1, #0
	SUB      sp, #0xec
	BL       |loc_08024A9C|
	ADD      r0, r4, #0
	ADD      r0, #0xc
	MOV      r2, #1
	LSL      r2, r2, #0xf
	MOV      r1, #0
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0x384]
	MOV      r3, #0
	ADD      r7, r4, r0
	STR      r3, [r7]
	STR      r3, [r7, #4]
	STR      r3, [r7, #8]
	SUB      r0, #0x10
	ADD      r0, r4, r0
	STR      r3, [r7, #0xc]
	STR      r3, [r0]
	STR      r3, [r0, #4]
	STR      r3, [r0, #8]
	STR      r3, [r0, #0xc]
	LDR      r0, [pc, #0x360]
	MOV      r1, #0
	ADD      r0, r4, r0
	STR      r0, [sp, #0xe8]
	STR      r1, [sp, #0xe0]
	LDR      r0, [r0]
	MOV      lr, r7
	CMP      r0, #0
	BEQ      |loc_08025876|
	LDR      r0, [r0, #0x14]
	MOV      ip, r1
	CMP      r0, #0
	BLE      |loc_08025878|
	LDR      r0, [sp, #0xe8]
	MOV      r1, ip
	LDR      r0, [r0]
	LSL      r1, r1, #2
	ADD      r0, r0, r1
	LDR      r5, [r0, #0x18]
	LDR      r3, [pc, #0x338]
	LDRH     r0, [r5, #2]
	LDR      r1, [r3, #8]
	LSR      r2, r0, #3
	ADD      r1, r2, r1
	LSL      r2, r0, #0x1d
	ADD      r1, #0x80
	LDRB     r1, [r1, #0xd]
	LSR      r2, r2, #0x1d
	MOV      r0, #1
	LSL      r0, r2
	AND      r1, r0
	BEQ      |sub_080257DA|
	LDR      r2, [r5, #0xc]
	LDR      r3, [r5, #4]
	LDR      r1, [r5, #8]
	SUB      r2, r2, r3
	LDR      r3, [r5, #0x10]
	ADD      r0, r5, #0
	SUB      r1, r3, r1
	MUL      r2, r1
	LSL      r1, r2, #1
	ADD      r6, r1, r5
	ADD      r0, #0x14
	ADD      r6, #0x24
	B        |sub_080257EC|
|sub_080257DA|
|unk_080257DA|
		LDR r3, [pc, #0x304]
		LDR r0, [r3, #8]
		LDRB r0, [r0, #1]
		LSL r0, r0, #0x19
		LSR r0, r0, #0x1f
		DCW     0xD055
		ADD r0, r5, #4
		ADD r6, r5, #0
		ADD r6, #0x24
|sub_080257EC|
	LDR      r1, [r0]
	LDR      r2, [r0, #8]
	MOV      r7, lr
	CMP      r1, r2
	BNE      |loc_080257FE|
	LDR      r2, [r0, #4]
	LDR      r3, [r0, #0xc]
	CMP      r2, r3
	BEQ      |loc_08025842|
|loc_080257FE|
	LDR      r2, [r7]
	STR      r2, [sp, #0xe4]
	LDR      r3, [r7, #8]
	CMP      r2, r3
	BNE      |sub_0802581C|
	LDR      r2, [r7, #4]
	LDR      r3, [r7, #0xc]
	CMP      r2, r3
	BNE      |sub_0802581C|
	LDMIA    r0!, {r1, r2, r3}
	STMIA    r7!, {r1, r2, r3}
	LDMIA    r0!, {r3}
	SUB      r0, #0x10
	STMIA    r7!, {r3}
	B        |loc_08025842|
|sub_0802581C|
|unk_0802581C|
		LDR r2, [sp, #0xe4]
		CMP r1, r2
		BGE      |loc_08025824|
		STR r1, [r7]
|loc_08025824|
		LDR r1, [r0, #4]
		LDR r2, [r7, #4]
		CMP r1, r2
		BGE      |loc_0802582E|
		STR r1, [r7, #4]
|loc_0802582E|
		LDR r1, [r0, #8]
		LDR r2, [r7, #8]
		CMP r1, r2
		BLE      |loc_08025838|
		STR r1, [r7, #8]
|loc_08025838|
		LDR r1, [r0, #0xc]
		LDR r2, [r7, #0xc]
		CMP r1, r2
		BLE      |loc_08025842|
		STR r1, [r7, #0xc]
|loc_08025842|
|unk_08025842|
; cited by 0x003FCB34 (a pool word names 0x08025848)
		LDR r3, [pc, #0x29c]
		LDR r1, [r3, #0x10]
		LDRB r1, [r1]
		LDRB r2, [r5]
		CMP r1, r2
		BNE      |loc_0802585A|
		LDR r1, [r3, #0x10]
		LDRB r1, [r1, #1]
		LDRB r2, [r5, #1]
		CMP r1, r2
		BNE      |loc_0802585A|
		STR r5, [sp, #0xe0]
|loc_0802585A|
		LDR r1, [r0, #0xc]
		LDR r2, [r0, #4]
		CMP r1, r2
		DCW     0xDD17
		LDR r1, [r0]
		LDR r3, [r0, #8]
		CMP r3, r1
		DCW     0xDD0F
		LSL r3, r2, #8
		ADD r5, r3, r4
		LDRH r3, [r6]
		ADD r6, #2
		CMP r3, #0
		DCW     0xE001
|loc_08025876|
|unk_08025876|
		B        |loc_08025A9A|
|loc_08025878|
|unk_08025878|
; cited by 0x080256F6 (a pc-relative load targets 0x08025AD4)
		B        |loc_080258A4|
		BEQ      |loc_08025882|
		LSL r7, r1, #1
		ADD r7, r5, r7
		STRH r3, [r7, #0xc]
|loc_08025882|
		LDR r3, [r0, #8]
		ADD r1, #1
		CMP r3, r1
		DCW     0xDCF1
		LDR r1, [r0, #0xc]
		ADD r2, #1
		CMP r1, r2
		DCW     0xDCE7
		LDR r0, [sp, #0xe8]
		MOV r1, ip
		LDR r0, [r0]
		ADD r1, #1
		LDR r0, [r0, #0x14]
		MOV ip, r1
		CMP r0, r1
		BLE      |loc_080258A4|
		DCW     0xE77A
|loc_080258A4|
		MOV r7, lr
		LDR r0, [r7]
		LSL r0, r0, #3
		STR r0, [r7]
		LDR r0, [r7, #4]
		LSL r0, r0, #3
		STR r0, [r7, #4]
		LDR r0, [pc, #0x23c]
		ADD r0, r4, r0
		LDR r1, [r0]
		LSL r1, r1, #3
		STR r1, [r0]
		LDR r1, [r0, #4]
		LSL r1, r1, #3
		STR r1, [r0, #4]
		MOV r0, #1
		LSL r0, r0, #0xf
		ADD r5, r4, r0
		LDR r0, [r5, #0x1c]
		ADD r1, r0, #0
		SUB r1, #0xdf
		STR r1, [r5, #0xc]
		LDR r1, [r5, #0x20]
		SUB r0, #0x10
		ADD r2, r1, #0
		SUB r2, #0x8f
		STR r2, [r5, #0x10]
		LDR r2, [r5, #0x24]
		SUB r1, #0x10
		ADD r3, r2, #0
		SUB r3, #0x11
		STR r3, [r5, #0x14]
		LDR r3, [r5, #0x28]
		ADD r5, #0x1c
		ADD r6, r3, #0
		SUB r3, #0x90
		SUB r2, #0xe0
		STMIA r5!, {r0, r1, r2, r3}
		SUB r5, #0x2c
		LDR r0, [pc, #0x1ec]
		SUB r6, #0x11
		STR r6, [r5, #0x18]
		LDR r0, [r0, #0xc]
		MOV r1, #0x2f
		ADD r6, r0, #0
		LDR r0, [pc, #0x1e0]
		ADD r6, #0x94
		LDR r0, [r0, #4]
		LSL r1, r1, #6
		ADD r0, r0, r1
		MOV r2, #0
		MOV r1, #9
		LDR r0, [r0, #0x38]
		BL       |loc_08011C70|
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #0xd4]
		ADD r0, r1, #0
		STR r1, [sp, #0xd0]
		LDR r1, [sp, #0xd4]
		LDR r7, [sp, #0xe0]
		STR r0, [sp, #0xd8]
		STR r1, [sp, #0xdc]
		ADD r7, #4
		LDR r0, [r7, #8]
		LDR r1, [r7]
		SUB r0, r0, r1
		LSL r1, r0, #3
		LDR r0, [sp, #0xd8]
		MUL r1, r0
		LDR r0, [r6]
		ASR r2, r0, #1
		ADD r1, r1, r2
		BL       |sub_08046E58|
		LDR r1, [sp, #0xe0]
		LDR r1, [r1, #4]
		LSL r1, r1, #3
		ADD r0, r0, r1
		STR r0, [r5, #0x2c]
		LDR r0, [r7, #0xc]
		LDR r1, [r7, #4]
		SUB r0, r0, r1
		LSL r1, r0, #3
		LDR r0, [sp, #0xdc]
		MUL r1, r0
		LDR r0, [r6, #4]
		ASR r2, r0, #1
		ADD r1, r1, r2
		BL       |sub_08046E58|
		LDR r1, [sp, #0xe0]
		LDR r1, [r1, #8]
		LSL r1, r1, #3
		ADD r0, r0, r1
		STR r0, [r5, #0x30]
		LDR r0, [pc, #0x16c]
		ADD r2, r4, r0
		ADD r6, r2, #0
		ADD r1, r4, #0
		MOV r0, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0xaaf4
		ADD r1, r0, #0
		LDR r0, [pc, #0x160]
		LDR r0, [r0, #4]
		BL       |sub_0801191A|
		LDR r0, [r5, #0x2c]
		SUB r0, #0x78
		STR r0, [r5, #0x2c]
		LDR r0, [r5, #0x30]
		SUB r0, #0x50
		STR r0, [r5, #0x30]
		LDR r0, [r6]
		ADD r0, #0xf0
		STR r0, [r6, #8]
		LDR r0, [r6, #4]
		ADD r0, #0xa0
		STR r0, [r6, #0xc]
		LDR r0, [sp, #0xe8]
		LDR r0, [r0]
		LDR r0, [r0]
		LDR r0, [r0, #4]
		DCW     0xF017
		DCW     0xFE07
		ADD r5, r0, #0
		LDR r0, [sp, #0xe8]
		ADD r1, r5, #0
		LDR r0, [r0]
		LDR r0, [r0]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LDR r0, [sp, #0xe8]
		ADD r1, r5, #0
		LDR r0, [r0]
		LDR r0, [r0]
		LDR r2, [r0, #4]
		MOV r0, #3
		LSL r0, r0, #0x19
		BL       |sub_08049138|
		ADD r0, r5, #0
		DCD     0xFE36F017
		LDR r0, [sp, #0xe8]
		LDR r0, [r0]
		LDR r1, [r0, #8]
		CMP r1, #0
		BEQ      |loc_08025A82|
		LDR r0, [r0, #0x10]
		LDR r7, [pc, #0x100]
		LDR r1, [r0, #4]
		LDR r0, [r7, #4]
		BL       |loc_0801124C|
		ADD r6, r0, #0
		LDR r0, [sp, #0xe8]
		LDR r0, [r0]
		LDR r0, [r0, #0x10]
		LDR r0, [r0, #4]
		DCD     0xFDE2F017
		ADD r5, r0, #0
		LDR r0, [sp, #0xe8]
		ADD r1, r5, #0
		LDR r0, [r0]
		LDR r0, [r0, #0x10]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LDR r1, [pc, #0xf0]
		LSL r0, r6, #5
		ADD r0, r0, r1
		LDR r1, [sp, #0xe8]
		LDR r1, [r1]
		LDR r1, [r1, #0x10]
		LDR r2, [r1, #4]
		ADD r1, r5, #0
		BL       |sub_08049138|
		ADD r0, r5, #0
		DCD     0xFE10F017
		LDR r0, [sp, #0xe8]
		LDR r0, [r0]
		LDR r7, [r0, #0xc]
		MOV r0, #0x20
		DCD     0xFDC8F017
		ADD r5, r0, #0
		BEQ      |loc_08025A3E|
		MOV r3, #0
		ADD r2, r7, #0
		ADD r1, r4, #0
		ADD r0, r5, #0
		STR r6, [sp]
		BL       |inc_0x1c3f2_0x2ab4c| + 0xa8aa
		LDR r0, [pc, #0xbc]
		STR r0, [r5]
|loc_08025A3E|
		LDR r7, [pc, #0xa0]
		ADD r1, r5, #0
		LDR r0, [r7, #4]
		BL       |sub_0801191A|
		LDR r0, [sp, #0xe8]
		MOV r5, #1
		LDR r0, [r0]
		LDR r0, [r0, #8]
		CMP r0, #1
		BLE      |loc_08025A82|
|loc_08025A54|
		LDR r0, [sp, #0xe8]
		STR r6, [sp]
		LDR r0, [r0]
		LSL r1, r5, #1
		ADD r1, r1, r5
		LDR r0, [r0, #0xc]
		LSL r1, r1, #3
		ADD r2, r0, r1
		ADD r3, r5, #0
		ADD r1, r4, #0
		MOV r0, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0xa8aa
		ADD r1, r0, #0
		LDR r0, [r7, #4]
		BL       |sub_0801191A|
		LDR r0, [sp, #0xe8]
		ADD r5, #1
		LDR r0, [r0]
		LDR r0, [r0, #8]
		CMP r0, r5
		BGT      |loc_08025A54|
|loc_08025A82|
		LDR r0, [sp, #0xe8]
		LDR r0, [r0]
		LDR r1, [r0, #4]
		CMP r1, #0
		BEQ      |loc_08025A9A|
		MOV r3, #0
		STR r3, [sp]
		STR r3, [sp, #0x44]
		MOV r2, #0
		MOV r0, sp
		BL       |loc_08004038|
|loc_08025A9A|
		MOV r2, #0
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08026B4C|
		LDR r5, [pc, #0x38]
		ADD r1, r0, #0
		LDR r0, [r5, #4]
		BL       |sub_0801191A|
		MOV r2, #1
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08026B4C|
		ADD r1, r0, #0
		LDR r0, [r5, #4]
		BL       |sub_0801191A|
		MOV r2, #2
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08026B4C|
		ADD r1, r0, #0
		LDR r0, [r5, #4]
		BL       |sub_0801191A|
		DCW     0xE013
	INCBIN  baserom.gba_0x25ad4_0x25adc.extracted
		DCD     0x0000802C
		DCD     0x08732360
	INCBIN  baserom.gba_0x25ae4_0x25af0.extracted
		DCD     0x00008024
		DCD     0x06010000
	INCBIN  baserom.gba_0x25af8_0x25afa.extracted
|sub_08025AFA|
	LSR      r4, r0, #0x20
	MOV      r2, #3
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |loc_08026B4C|
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0x2e0]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #0xc]
	SUB      r1, #0xff
	SUB      r1, #0x44
	STRH     r1, [r0]
	ADD      sp, #0xec
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_08025B32|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08025B32|
	POP      {r3, pc}
|sub_08025B34|
|unk_08025B34|
; cited by 0x004C31D0 (a pool word names 0x08025C00)
		PUSH {r0, r4, r5, r6, r7, lr}
		SUB sp, #0x40
		LDR r1, [sp, #0x40]
		MOV r0, #1
		LSL r0, r0, #0xf
		ADD r0, r1, r0
		LDR r1, [r0, #0x2c]
		LDR r0, [r0, #0x30]
		SUB r1, #8
		LSL r2, r1, #0x18
		LSR r6, r2, #0x1b
		SUB r0, #0x30
		LSL r2, r0, #0x18
		ASR r0, r0, #8
		STR r0, [sp, #0xc]
		MOV r0, #0x20
		SUB r0, r0, r6
		STR r0, [sp, #8]
		LDR r0, [sp, #0xc]
		ASR r1, r1, #8
		LSR r5, r2, #0x1b
		CMP r0, #0
		STR r1, [sp, #0x10]
		LDR r4, [pc, #0x290]
		BGE      |loc_08025B80|
		ADD r7, r5, #0
		CMP r5, #0x20
		BGE      |loc_08025C12|
|loc_08025B6C|
		LSL r0, r7, #6
		ADD r0, r0, r4
		MOV r2, #0x40
		MOV r1, #0
		BL       |sub_0804912C|
		ADD r7, #1
		CMP r7, #0x20
		BLT      |loc_08025B6C|
		B        |loc_08025C12|
|loc_08025B80|
		LDR r1, [sp, #0x10]
		CMP r1, #0
		BGE      |loc_08025BAE|
		ADD r7, r5, #0
		CMP r5, #0x20
		BGE      |loc_08025BEC|
		LDR r0, [sp, #8]
		LSL r2, r0, #1
		LSL r1, r6, #1
		STR r1, [sp, #0x38]
		STR r2, [sp, #0x3c]
|loc_08025B96|
		LSL r0, r7, #6
		LDR r1, [sp, #0x38]
		ADD r0, r0, r4
		ADD r0, r0, r1
		MOV r1, #0
		LDR r2, [sp, #0x3c]
		BL       |sub_08049168|
		ADD r7, #1
		CMP r7, #0x20
		BLT      |loc_08025B96|
		B        |loc_08025BEC|
|loc_08025BAE|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x40]
		LSL r0, r0, #0xd
		ADD r0, r0, r1
		LDR r1, [sp, #0x10]
		ADD r7, r5, #0
		LSL r1, r1, #6
		ADD r1, r0, r1
		ADD r1, #0xc
		STR r1, [sp, #4]
		CMP r5, #0x20
		BGE      |loc_08025BEC|
		LDR r0, [sp, #8]
		LSL r0, r0, #1
		LSL r2, r6, #1
		STR r2, [sp, #0x30]
		STR r0, [sp, #0x34]
|loc_08025BD0|
		LDR r1, [sp, #4]
		LSL r0, r7, #8
		LDR r2, [sp, #0x30]
		ADD r0, r0, r1
		ADD r1, r0, r2
		LSL r0, r7, #6
		ADD r0, r0, r4
		ADD r0, r0, r2
		LDR r2, [sp, #0x34]
		BL       |sub_08049144|
		ADD r7, #1
		CMP r7, #0x20
		BLT      |loc_08025BD0|
|loc_08025BEC|
		CMP r6, #0
		BEQ      |loc_08025C12|
		LDR r1, [sp, #0x10]
		CMP r1, #3
		BLT      |sub_08025C14|
		ADD r7, r5, #0
		CMP r5, #0x20
		BGE      |loc_08025C12|
		LSL r2, r6, #1
		STR r2, [sp, #0x2c]
|loc_08025C00|
		LSL r0, r7, #6
		ADD r0, r0, r4
		MOV r1, #0
		LDR r2, [sp, #0x2c]
		BL       |sub_08049168|
		ADD r7, #1
		CMP r7, #0x20
		BLT      |loc_08025C00|
|loc_08025C12|
		B        |loc_08025C46|
|sub_08025C14|
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x40]
	LSL      r0, r0, #0xd
	ADD      r0, r0, r1
	LDR      r1, [sp, #0x10]
	ADD      r7, r5, #0
	LSL      r1, r1, #6
	ADD      r1, r0, r1
	ADD      r1, #0x4c
	STR      r1, [sp, #4]
	CMP      r5, #0x20
	BGE      |loc_08025C46|
	LSL      r0, r6, #1
	STR      r0, [sp, #0x28]
|loc_08025C30|
	LDR      r1, [sp, #4]
	LSL      r0, r7, #8
	ADD      r1, r0, r1
	LSL      r0, r7, #6
	ADD      r0, r0, r4
	LDR      r2, [sp, #0x28]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      r7, #1
	CMP      r7, #0x20
	BLT      |loc_08025C30|
|loc_08025C46|
	LDR      r0, [sp, #0xc]
	CMP      r0, #3
	BLT      |sub_08025C66|
	CMP      r5, #0x20
	BGE      |loc_08025C62|
|loc_08025C50|
	LSL      r0, r5, #6
	ADD      r0, r0, r4
	MOV      r2, #0x40
	MOV      r1, #0
	BL       |inc_0x049120_0x055620| + 0xc
	ADD      r5, #1
	CMP      r5, #0x20
	BLT      |loc_08025C50|
|loc_08025C62|
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
|sub_08025C66|
|unk_08025C66|
		LDR r1, [sp, #0x10]
		CMP r1, #0
		BGE      |loc_08025C94|
		MOV r7, #0
		CMP r5, #0
		BLE      |loc_08025CD4|
		LDR r0, [sp, #8]
		LSL r2, r0, #1
		LSL r1, r6, #1
		STR r1, [sp, #0x20]
		STR r2, [sp, #0x24]
|loc_08025C7C|
		LSL r0, r7, #6
		LDR r1, [sp, #0x20]
		ADD r0, r0, r4
		ADD r0, r0, r1
		MOV r1, #0
		LDR r2, [sp, #0x24]
		BL       |sub_08049168|
		ADD r7, #1
		CMP r7, r5
		BLT      |loc_08025C7C|
		B        |loc_08025CD4|
|loc_08025C94|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x40]
		LSL r0, r0, #0xd
		ADD r0, r0, r1
		LDR r1, [sp, #0x10]
		MOV r7, #0
		LSL r1, r1, #6
		ADD r0, r0, r1
		LDR r1, [pc, #0x150]
		ADD r1, r0, r1
		STR r1, [sp, #4]
		CMP r5, #0
		BLE      |loc_08025CD4|
		LDR r0, [sp, #8]
		LSL r0, r0, #1
		LSL r2, r6, #1
		STR r2, [sp, #0x18]
		STR r0, [sp, #0x1c]
|loc_08025CB8|
		LDR r1, [sp, #4]
		LSL r0, r7, #8
		LDR r2, [sp, #0x18]
		ADD r0, r0, r1
		ADD r1, r0, r2
		LSL r0, r7, #6
		ADD r0, r0, r4
		ADD r0, r0, r2
		LDR r2, [sp, #0x1c]
		BL       |sub_08049144|
		ADD r7, #1
		CMP r7, r5
		BLT      |loc_08025CB8|
|loc_08025CD4|
		CMP r6, #0
		BEQ      |loc_08025C62|
		LDR r1, [sp, #0x10]
		CMP r1, #3
		BLT      |loc_08025CFA|
		MOV r7, #0
		CMP r5, #0
		BLE      |loc_08025C62|
		LSL r6, r6, #1
|loc_08025CE6|
		LSL r0, r7, #6
		ADD r0, r0, r4
		ADD r2, r6, #0
		MOV r1, #0
		BL       |sub_08049168|
		ADD r7, #1
		CMP r7, r5
		BLT      |loc_08025CE6|
		B        |loc_08025C62|
|loc_08025CFA|
		MOV r7, #0
		CMP r5, #0
		BLE      |loc_08025C62|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x40]
		LSL r0, r0, #0xd
		ADD r0, r0, r1
		LDR r1, [sp, #0x10]
		LSL r1, r1, #6
		ADD r1, r0, r1
		LDR r0, [pc, #0xec]
		ADD r1, r1, r0
		STR r1, [sp, #0x14]
		LSL r6, r6, #1
|loc_08025D16|
		LDR r1, [sp, #0x14]
		LSL r0, r7, #8
		ADD r1, r0, r1
		LSL r0, r7, #6
		ADD r0, r0, r4
		ADD r2, r6, #0
		BL       |sub_08049144|
		ADD r7, #1
		CMP r7, r5
		BLT      |loc_08025D16|
		B        |loc_08025C62|
|sub_08025D2E|
	MOV      r1, #1
	LSL      r1, r1, #0xf
	ADD      r0, r0, r1
	LDR      r1, [r0, #0x2c]
	LDR      r3, [pc, #0xc8]
	LDR      r2, [r0, #0x30]
	STRH     r1, [r3]
	STRH     r2, [r3, #2]
	LDR      r1, [r0, #0x2c]
	LDR      r0, [r0, #0x30]
	STRH     r1, [r3, #4]
	STRH     r0, [r3, #6]
	BX       lr
	LDR      r3, [pc, #0xb8]
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r3]
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x1a
	LSR      r2, r1, #0x1f
	MOV      r1, #1
	LSL      r1, r1, #0xf
	ADD      r1, r0, r1
	CMP      r2, #0
	BEQ      |loc_08025D6A|
	LDR      r2, [r1, #0x2c]
	LDR      r4, [r1, #0xc]
	CMP      r2, r4
	BLE      |loc_08025D6A|
	SUB      r2, #1
	STR      r2, [r1, #0x2c]
|loc_08025D6A|
	LDR      r2, [r3]
	LDRH     r2, [r2, #2]
	LSL      r2, r2, #0x1b
	LSR      r2, r2, #0x1f
	BEQ      |loc_08025D80|
	LDR      r2, [r1, #0x2c]
	LDR      r4, [r1, #0x14]
	CMP      r2, r4
	BGE      |loc_08025D80|
	ADD      r2, #1
	STR      r2, [r1, #0x2c]
|loc_08025D80|
	LDR      r2, [r3]
	LDRH     r2, [r2, #2]
	LSL      r2, r2, #0x19
	LSR      r2, r2, #0x1f
	BEQ      |loc_08025D96|
	LDR      r2, [r1, #0x30]
	LDR      r4, [r1, #0x10]
	CMP      r2, r4
	BLE      |loc_08025D96|
	SUB      r2, #1
	STR      r2, [r1, #0x30]
|loc_08025D96|
	LDR      r2, [r3]
	ADD      r4, r3, #0
	LDRH     r2, [r2, #2]
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x1f
	BEQ      |loc_08025DAE|
	LDR      r2, [r1, #0x30]
	LDR      r3, [r1, #0x18]
	CMP      r2, r3
	BGE      |loc_08025DAE|
	ADD      r2, #1
	STR      r2, [r1, #0x30]
|loc_08025DAE|
	LDR      r2, [pc, #0x58]
	MOV      r5, #1
	ADD      r2, r0, r2
	LDR      r3, [r2]
	ADD      r3, #0xf0
	STR      r3, [r2, #8]
	LDR      r3, [r2, #4]
	ADD      r3, #0xa0
	STR      r3, [r2, #0xc]
	LDR      r3, [r4]
	ADD      r2, r5, #0
	LDRH     r3, [r3, #2]
	LSL      r3, r3, #0x18
	LSR      r6, r3, #0x1c
	BNE      |loc_08025DCE|
	MOV      r2, #0
|loc_08025DCE|
	LDR      r6, [r1, #0x3c]
	CMP      r2, r6
	BEQ      |loc_08025DDC|
	LSR      r2, r3, #0x1c
	BNE      |loc_08025DDA|
	MOV      r5, #0
|loc_08025DDA|
	STR      r5, [r1, #0x3c]
|loc_08025DDC|
	LDR      r1, [r4]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1f
	BEQ      |loc_08025DEE|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_08025DEE|
	POP      {r4, r5, r6, pc}
|sub_08025DF0|
|unk_08025DF0|
	INCBIN	baserom.gba_0x25df0_0x25df2.extracted
|sub_08025DF2|
	LSL      r0, r0, #0
	DCW      0xf000,0x0600
	MOV      r0, #0xc
	LSL      r0, r0, #0
	MOV      r0, #0x4c
	LSL      r0, r0, #0
	LSL      r0, r3, #0
	LSL      r0, r0, #0x10
	MOV      r3, #0x60
	LSR      r3, r6, #1
	STRH     r4, [r5]
	LSL      r0, r0, #0
	MOV      r1, #1
	LSL      r1, r1, #0xf
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x2c]
	ASR      r0, r0, #1
	BX       lr
	MOV      r1, #1
	LSL      r1, r1, #0xf
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x30]
	ASR      r0, r0, #1
	BX       lr
	PUSH     {r3, lr}
	MOV      r0, #0
	BL       |loc_080261D4|
	POP      {r3, pc}
	PUSH     {r4, lr}
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08025E3E|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_08025E3E|
	ADD      r0, r4, #0
	BL       |loc_08024A7C|
	LDR      r0, [pc, #4]
	STR      r0, [r4]
	ADD      r0, r4, #0
	POP      {r4, pc}
|sub_08025E4C|
|unk_08025E4C|
	INCBIN	baserom.gba_0x25e4c_0x25e4e.extracted
|sub_08025E4E|
	LSR      r4, r0, #0x20
|loc_08025E50|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x34
	BNE      |sub_08025E6E|
	MOV      r0, #0x2c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08025E6E|
	ADD      r0, r4, #0
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
|sub_08025E6E|
|unk_08025E6E|
		ADD r0, r4, #0
		BL       |loc_08024A7C|
		LDR r0, [pc, #0x30c]
		ASR r2, r5, #3
		STR r0, [r4]
		STR r6, [r4, #0x18]
		LDR r0, [pc, #0x308]
		LSL r6, r5, #0x1d
		LDR r1, [r0, #8]
		LSR r6, r6, #0x1d
		ADD r1, r2, r1
		ADD r1, #0xc0
		MOV r3, #1
		LDRB r2, [r1, #5]
		LSL r3, r6
		ORR r2, r3
		STRB r2, [r1, #5]
		LSL r1, r5, #4
		LDR r2, [pc, #0x2f4]
		MOV r5, #0
		ADD r1, r1, r2
		STR r1, [r4, #0x20]
		MOV r1, #0
		STR r1, [r4, #0x10]
		STR r1, [r4, #0x1c]
		STRB r1, [r4, #0xc]
		STRB r1, [r4, #0xd]
		STR r1, [sp]
		STR r1, [sp, #4]
		MOV r1, #0x68
		STR r1, [sp, #8]
		MOV r1, #0x38
		STR r1, [sp, #0xc]
		LDR r1, [r0, #0xc]
		ADD r6, sp, #0x10
		ADD r0, r6, #0
		MOV r2, sp
		BL       |inc_0x03d784_0x041118| + 0x2f4
		LDR r0, [r4, #0x20]
		LDR r1, [pc, #0x2cc]
		LDRH r0, [r0, #2]
		MOV r7, sp
		LSL r0, r0, #2
		LDR r0, [r1, r0]
		STR r0, [sp, #4]
|loc_08025ECC|
		ADD r3, r7, #0
		MOV r2, #0x68
		ADD r0, r6, #0
		LDR r1, [sp, #4]
		BL       |inc_0x03d784_0x041118| + 0x6e6
		LDR r0, [sp, #0xc]
		ADD r5, #1
		CMP r0, #0
		BEQ      |loc_08025ECC|
		LSL r0, r5, #4
		SUB r0, #0x38
		STR r0, [r4, #0x14]
		BPL      |loc_08025EEC|
		MOV r1, #0
		STR r1, [r4, #0x14]
|loc_08025EEC|
		ADD r0, r4, #0
		DCW     0xE7BC
|sub_08025EF0|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x28c]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0x1c]
	CMP      r0, #0
	BEQ      |loc_08025F06|
	MOV      r1, #1
	BL       |inc_0x03d784_0x041118| + 0x1e08
|loc_08025F06|
	LDR      r0, [pc, #0x28c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08025F14|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08025F14|
	POP      {r3, r4, r5, pc}
|loc_08025F16|
	PUSH     {r4, lr}
	LDR      r2, [r0, #0x14]
	ADD      r4, r0, #0
	ADD      r2, #0x38
	MOV      r1, #0x68
	MOV      r0, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r1, [pc, #0x260]
	STR      r0, [r4, #0x1c]
	LDR      r1, [r1, #0xc]
	STR      r1, [r0, #0xc]
	LDR      r1, [r4, #0x1c]
	MOV      r0, #2
	STRB     r0, [r1, #3]
	LDR      r0, [r4, #0x1c]
	MOV      r1, #0
	STR      r1, [r0, #4]
	MOV      r1, #0xe
	STR      r1, [r0, #8]
	LDR      r1, [r4, #0x1c]
	MOV      r0, #0x10
	STRB     r0, [r1, #1]
	LDR      r0, [r4, #0x1c]
	MOV      r1, #0
	LDR      r2, [r0, #0x30]
	LDR      r0, [r0, #0x24]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x20]
	LDR      r1, [pc, #0x23c]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #2
	LDR      r2, [r1, r0]
	LDR      r0, [r4, #0x1c]
	MOV      r1, #0x68
	BL       |inc_0x03d784_0x041118| + 0x5e2
	POP      {r4, pc}
|sub_08025F64|
|unk_08025F64|
		BX       lr
|sub_08025F66|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0
	SUB      sp, #0x10
	STR      r0, [sp]
	LDR      r0, [r4, #0x10]
	MOV      r2, sp
	STR      r0, [sp, #4]
	MOV      r0, #0x68
	STR      r0, [sp, #8]
	LDR      r0, [r4, #0x10]
	LDR      r1, [pc, #0x218]
	ADD      r0, #0x38
	STR      r0, [sp, #0xc]
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x049120_0x055620| + 0x3c
	LDR      r1, [r4, #0x24]
	LDR      r2, [r4, #0x10]
	MOV      r0, #1
	CMP      r2, #0
	BGT      |loc_08025F94|
	MOV      r0, #0
|loc_08025F94|
	STR      r0, [r1, #0x20]
	LDR      r0, [r4, #0x28]
	ADD      r4, #0x10
	LDMIA    r4!, {r1, r2}
	CMP      r1, r2
	BGE      |loc_08025FA4|
	MOV      r1, #1
	B        |loc_08025FA6|
|loc_08025FA4|
	MOV      r1, #0
|loc_08025FA6|
	STR      r1, [r0, #0x20]
	ADD      sp, #0x10
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x1d8]
	ADD      r4, r0, #0
	LDR      r1, [r5]
	MOV      r0, #0
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	BEQ      |loc_08025FD0|
	LDR      r1, [r4, #0x10]
	CMP      r1, #0
	BEQ      |loc_08025FD0|
	SUB      r1, #1
	STR      r1, [r4, #0x10]
	ADD      r0, r4, #0
	BL       |sub_08025F66|
	MOV      r0, #1
|loc_08025FD0|
	LDR      r1, [r5]
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x1f
	BEQ      |loc_08025FEE|
	LDR      r1, [r4, #0x10]
	LDR      r2, [r4, #0x14]
	CMP      r1, r2
	BGE      |loc_08025FEE|
	ADD      r1, #1
	STR      r1, [r4, #0x10]
	ADD      r0, r4, #0
	BL       |sub_08025F66|
	MOV      r0, #1
|loc_08025FEE|
	LDRB     r1, [r4, #0xd]
	CMP      r1, r0
	BEQ      |loc_08025FF6|
	STRB     r0, [r4, #0xd]
|loc_08025FF6|
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1f
	BEQ      |loc_08026004|
	MOV      r0, #1
	STRB     r0, [r4, #0xc]
|loc_08026004|
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |loc_08026018|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_08026018|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	LDRB     r1, [r0, #0xc]
	CMP      r1, #0
	BEQ      |sub_08026042|
	MOV      r0, #0x29
	LSL      r0, r0, #5
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_08026038|
	ADD      r0, r4, #0
	BL       |loc_080261D4|
	LDR      r0, [pc, #0x164]
	STR      r0, [r4]
|loc_08026038|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r4, pc}
|sub_08026042|
|unk_08026042|
	INCBIN	baserom.gba_0x26042_0x26044.extracted
|sub_08026044|
|unk_08026044|
	INCBIN	baserom.gba_0x26044_0x26048.extracted
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x154]
	LDR      r6, [pc, #0x138]
	ADD      r4, r0, #0
	ADD      sp, r3
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x119ac
	LDR      r0, [r4, #0x20]
	LDR      r0, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0x11dc8
	LDR      r6, [pc, #0x140]
	ADD      r5, r0, #0
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	ADD      r6, sp
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r3, #1
	LSL      r3, r3, #0xc
	LDR      r0, [pc, #0x110]
	ADD      r3, sp
	LDR      r1, [r3, #0x34]
	ADD      r0, #0x10
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [r4, #0x20]
	LDR      r2, [r4, #0x18]
	ADD      r1, r6, #0
	BL       |sub_08024D94|
	CMP      r5, #0
	BEQ      |loc_080260AC|
	ADD      r7, sp, #0x10
	ADD      r1, r7, #0
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [pc, #0x10c]
	MOV      r5, sp
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r5!, {r0, r1, r2, r3}
	SUB      r5, #0x10
	ADD      r1, r7, #0
	ADD      r0, r6, #0
	MOV      r2, sp
	BL       |inc_0x03d784_0x041118| + 0x219e
|loc_080260AC|
	LDR      r1, [pc, #0xfc]
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x2234
	LDR      r0, [pc, #0xec]
	MOV      r1, #0
	ADD      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	MOV      r0, #0
	LDR      r1, [r4, #0x20]
	BL       |sub_080272EC|
	ADD      r5, r0, #0
	LDR      r6, [pc, #0xbc]
	ADD      r1, r0, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #2
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	MOV      r5, #0
	STR      r5, [r3, #0x34]
	MOV      r0, #0x1e
	STR      r0, [r3, #0x3c]
	STR      r5, [r3, #0x38]
	MOV      r0, #0x14
	STR      r0, [r3, #0x40]
	ADD      r0, r3, #0
	MOV      r2, #1
	ADD      r0, #0x34
	LDR      r1, [pc, #0xb4]
	BL       |inc_0x03d784_0x041118| + 0x28c
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0xac]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	MOV      r0, #0xf
	STR      r0, [r3, #0x34]
	MOV      r0, #0xb
	STR      r0, [r3, #0x38]
	MOV      r0, #0x1c
	STR      r0, [r3, #0x3c]
	MOV      r0, #0x12
	STR      r0, [r3, #0x40]
	MOV      r2, #0x13
	LSL      r2, r2, #5
	ADD      r0, r3, #0
	ADD      r0, #0x34
	LDR      r1, [pc, #0x88]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0x84]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #0xc]
	ADD      r1, #0xff
	ADD      r1, #1
	STRH     r1, [r0, #0xe]
	STRH     r5, [r0, #0x18]
	STRH     r5, [r0, #0x1a]
	STRH     r5, [r0, #0x1c]
	MOV      r1, #0x71
	LSL      r1, r1, #6
	STRH     r5, [r0, #0x1e]
	STRH     r1, [r0]
	MOV      r1, #1
	MOV      r0, #0
	BL       |loc_080271D0|
	MOV      r1, #0
	STR      r0, [r4, #0x24]
	MOV      r0, #0
	BL       |loc_080271D0|
	STR      r0, [r4, #0x28]
	LDR      r1, [r4, #0x24]
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [r4, #0x28]
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r0, r4, #0
	BL       |loc_08025F16|
	ADD      r0, r4, #0
	BL       |sub_08025F66|
	LDR      r3, [pc, #0x3c]
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
|sub_08026182|
	DCW      0x0000
	DCW      0xa52c,0x0804,0x2374,0x0873,0xd380,0x0874,0xbce8,0x0806
	DCW      0x91f0,0x0804,0x9800,0x0600,0xe3c8,0x0804,0xefbc,0xffff
	DCW      0x1010,0x0000,0x25e8,0x0873,0x0040,0x0600,0xf800
|sub_080261B2|
	LSL      r0, r0, #0x18
	DCW      0xf000,0x0600
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	ASR      r4, r0, #1
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_080261D2|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080261D2|
	POP      {r3, pc}
|loc_080261D4|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BNE      |loc_080261EA|
	MOV      r0, #0x29
	LSL      r0, r0, #5
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_080261EA|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_080261EA|
	ADD      r0, r4, #0
	BL       |loc_08024A7C|
	LDR      r0, [pc, #0x214]
	ADD      r2, r4, #0
	STR      r0, [r4]
	MOV      r0, #0
	STR      r0, [r4, #0xc]
	LDR      r0, [pc, #0x210]
	MOV      r1, #0x2f
	LDR      r0, [r0, #4]
	LSL      r1, r1, #6
	ADD      r2, #0xc
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x38]
	MOV      r1, #0x16
	BL       |inc_0x0158_0x143f2| + 0x11ab4
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_08026212|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	MOV      r1, #1
	BL       |loc_08024A9C|
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r7, r5, r1
	MOV      r0, #0
	STR      r0, [r7, #0x18]
	STR      r0, [r7, #0x10]
	LDR      r0, [r5, #0xc]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08026256|
	ADD      r6, r5, #0
	ADD      r6, #0xc
|loc_08026234|
	LSL      r0, r4, #2
	ADD      r0, r0, r4
	LSL      r0, r0, #3
	ADD      r1, r0, r6
	ADD      r1, #4
	MOV      r0, #0
	BL       |loc_08027390|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x1c4]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r0, [r5, #0xc]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08026234|
|loc_08026256|
	MOV      r0, #0
	BL       |loc_08026F94|
	ADD      r1, r0, #0
	STR      r0, [r7, #0x1c]
	LDR      r0, [pc, #0x1a8]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r0, #0x65
	LSL      r0, r0, #6
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	STRH     r0, [r1]
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	MOV      r0, #0
	BL       |loc_080256F0|
	POP      {r3, pc}
|loc_0802627E|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r3, [r0, #0xc]
	LDR      r5, [pc, #0x18c]
	MOV      r4, #0
	MOV      r2, #0
	CMP      r3, #0
	SUB      sp, #0x14
	MOV      lr, r5
	BLE      |loc_0802630A|
	ADD      r5, r0, #0
	ADD      r5, #0xc
	MOV      ip, r5
|loc_08026296|
	LSL      r3, r2, #2
	ADD      r3, r3, r2
	LSL      r3, r3, #3
	ADD      r3, ip
	ADD      r3, #4
	STR      r3, [sp, #0x10]
	LDR      r5, [r1]
	ADD      r3, #0x14
	LDR      r7, [r3]
	ADD      r6, r3, #0
	CMP      r5, r7
	BLT      |loc_08026302|
	LDR      r7, [r3, #8]
	CMP      r5, r7
	BGE      |loc_08026302|
	LDR      r5, [r1, #4]
	LDR      r7, [r3, #4]
	CMP      r5, r7
	BLT      |loc_08026302|
	LDR      r3, [r3, #0xc]
	CMP      r5, r3
	BGE      |loc_08026302|
	ADD      r3, r6, #0
	LDR      r5, [r6]
	LDR      r7, [r6, #8]
	LDR      r6, [r6, #4]
	ADD      r3, #8
	LDR      r3, [r3, #4]
	ADD      r5, r5, r7
	ADD      r3, r6, r3
	STR      r3, [sp, #4]
	STR      r5, [sp]
	ASR      r5, r5, #1
	ASR      r3, r3, #1
	STR      r3, [sp, #4]
	STR      r3, [sp, #0xc]
	STR      r5, [sp]
	STR      r5, [sp, #8]
	LDR      r3, [r1]
	SUB      r3, r3, r5
	LDR      r5, [r1, #4]
	LDR      r6, [sp, #0xc]
	STR      r3, [sp]
	SUB      r5, r5, r6
	ADD      r6, r3, #0
	MUL      r3, r6
	ADD      r6, r5, #0
	MUL      r6, r5
	ADD      r3, r3, r6
	CMP      r3, lr
	STR      r5, [sp, #4]
	BGE      |loc_08026302|
	LDR      r3, [sp, #0x10]
	LDR      r4, [r3, #0x24]
|loc_08026302|
	LDR      r3, [r0, #0xc]
	ADD      r2, #1
	CMP      r3, r2
	BGT      |loc_08026296|
|loc_0802630A|
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r5, r0, r1
	LDR      r0, [r5, #0x18]
	CMP      r0, r4
	BEQ      |loc_0802632A|
	CMP      r0, #0
	BEQ      |loc_0802631E|
	BL       |loc_08027448|
|loc_0802631E|
	STR      r4, [r5, #0x18]
	CMP      r4, #0
	BEQ      |loc_0802632A|
	ADD      r0, r4, #0
	BL       |sub_08027424|
|loc_0802632A|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	MOV      r1, #5
	LSL      r1, r1, #8
	PUSH     {lr}
	ADD      r1, r0, r1
	LDR      r1, [r1, #0x1c]
	MOV      r2, #0xc1
	LSL      r2, r2, #4
	ADD      r1, r1, r2
	LDMIA    r1!, {r2}
	LDR      r1, [r1]
	SUB      sp, #0x14
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #8]
	ADD      r1, r2, #0
	STR      r2, [sp, #4]
	LDR      r2, [sp, #8]
	STR      r1, [sp, #0xc]
	ADD      r3, sp, #0xc
	ADD      r1, r3, #0
	STR      r2, [sp, #0x10]
	BL       |loc_0802627E|
	ADD      sp, #0x14
	POP      {pc}
	LDR      r1, [pc, #0xa8]
	PUSH     {r3, lr}
	LDR      r1, [r1]
	LDRH     r1, [r1, #6]
	LSL      r1, r1, #0x1f
	BEQ      |loc_08026388|
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r1, r0, r1
	LDR      r2, [r1, #0x18]
	CMP      r2, #0
	BEQ      |loc_08026388|
	STR      r2, [r1, #0x14]
	MOV      r2, #1
	STR      r2, [r1, #0x10]
	BL       |loc_08024BE6|
	LDR      r0, [pc, #0x90]
	LDR      r1, [pc, #0x90]
	STRH     r0, [r1, #0x10]
|loc_08026388|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r4, r0, r1
	LDR      r1, [r4, #0x10]
	CMP      r1, #0
	BEQ      |sub_080263B8|
	LDR      r0, [r4, #0x14]
	BL       |loc_0802745E|
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x14]
	BL       |loc_08027454|
	ADD      r1, r0, #0
	ADD      r2, r5, #0
	MOV      r0, #0
	BL       |loc_08025E50|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
|sub_080263B8|
|unk_080263B8|
	INCBIN	baserom.gba_0x263b8_0x263ba.extracted
|sub_080263BA|
|unk_080263BA|
	INCBIN	baserom.gba_0x263ba_0x263be.extracted
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x1c]
	MOV      r1, #0xc1
	LSL      r1, r1, #4
	ADD      r0, r0, r1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	SUB      sp, #0x10
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #4]
	STR      r1, [sp]
	STR      r1, [sp, #8]
	ADD      sp, #0x10
	ASR      r0, r1, #2
	BX       lr
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x1c]
	MOV      r1, #0xc1
	LSL      r1, r1, #4
	ADD      r0, r0, r1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	SUB      sp, #0x10
	ASR      r0, r0, #8
	ASR      r1, r1, #8
	STR      r0, [sp, #4]
	STR      r0, [sp, #0xc]
	STR      r1, [sp]
	ADD      sp, #0x10
	ASR      r0, r0, #2
	BX       lr
|sub_08026406|
	DCW      0x0000
	DCW      0xa570,0x0804,0x25f8,0x0873,0xffff
|sub_08026412|
	LDRB     r7, [r7, #0x1f]
	SUB      r7, #0x5f
	LSL      r0, r0, #0
	LSL      r0, r0, #1
	LSL      r0, r0, #0x10
	PUSH     {r4, r5, lr}
	SUB      sp, #0x6c
	MOV      r1, #1
	BL       |loc_08024A9C|
	LDR      r5, [pc, #0x8c]
	LDR      r0, [r5, #4]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1bc
	ADD      r1, r4, #0
	LDR      r0, [pc, #0x7c]
	LDR      r2, [r5, #4]
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08026448|
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x6c]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0x1e
	STR      r0, [sp, #0x64]
	MOV      r0, #0x14
	MOV      r4, #0
	STR      r0, [sp, #0x68]
	ADD      r0, sp, #0x5c
	STR      r4, [sp, #0x5c]
	STR      r4, [sp, #0x60]
	MOV      r2, #1
	LDR      r1, [pc, #0x54]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0x50]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #0xc]
	SUB      r1, #0xff
	SUB      r1, #0x44
	STRH     r1, [r0]
	LDR      r1, [pc, #0x48]
	MOV      r0, sp
	MOV      r2, #0
	BL       |inc_0x0158_0x143f2| + 0x3f40
	LDR      r0, [pc, #0x40]
	STRH     r4, [r0]
	STRH     r4, [r0, #2]
	ADD      sp, #0x6c
	POP      {r4, r5, pc}
	PUSH     {r3, lr}
	MOV      r0, #0
	BL       |loc_080256F0|
	POP      {r3, pc}
	LDR      r1, [pc, #0x18]
	PUSH     {r3, lr}
	SUB      r1, #4
	LDR      r1, [r1]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1f
	BEQ      |loc_080264B0|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_080264B0|
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r6, #4
	LSR      r3, r6, #1
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	DCW      0xf000,0x0600
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	BEQ      |loc_08026448|
	LSR      r7, r6, #1
	LSL      r0, r3, #0
	LSL      r0, r0, #0x10
	LDR      r0, [pc, #0]
	BX       lr
|sub_080264D0|
|unk_080264D0|
	INCBIN	baserom.gba_0x264d0_0x264d2.extracted
|sub_080264D2|
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	ADD      r0, r1, #0
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	STRB     r2, [r0, #0x11]
	MOV      r1, #0x12
	BL       |inc_0x0158_0x143f2| + 0xeb82
	POP      {r3, pc}
	PUSH     {r4, r5, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x1c
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x10
	BCC      |sub_08026510|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
|sub_08026510|
|unk_08026510|
		LSR r0, r0, #2
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #4
		DCW     0xD1F8
		LDR r5, [pc, #0xd4]
		LDR r0, [r5, #4]
		BL       |loc_080116FC|
		CMP r0, #0x80
		DCW     0xDBF2
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0xac]
		ADD r1, #8
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #0xc]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0x10]
		LDR r0, [r0, #4]
		STR r1, [sp, #4]
		ADD r0, r2, r0
		STR r0, [sp, #8]
		ADD r0, r1, #0
		LDR r1, [sp, #8]
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x18]
		ADD r3, r4, #0
		MOV r0, #0
		LDRB r2, [r4, #0x10]
		ADD r1, sp, #0x14
		BL       |inc_0x1c3f2_0x2ab4c| + 0xb0c2
		ADD r1, r0, #0
		LDR r0, [r5, #4]
		BL       |sub_0801191A|
		LDR r4, [pc, #0x80]
		LDR r0, [r5]
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r0, r4
		LDR r1, [pc, #0x70]
	INCBIN  baserom.gba_0x26582_0x26584.extracted
|sub_08026584|
|unk_08026584|
	INCBIN	baserom.gba_0x26584_0x26588.extracted
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x70]
	SUB      sp, #0x10
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x68]
	STR      r1, [sp, #8]
	CMP      r4, #0
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	BEQ      |loc_080265A6|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_080265A6|
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x4c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x48]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_080265D2|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080265D2|
	ADD      sp, #0x10
	POP      {r4, pc}
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0x28]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_080265E4|
	MOV      r0, #0
|loc_080265E4|
	SUB      r0, r2, r0
	BX       lr
	LDR      r0, [pc, #0x18]
	ADD      r0, #4
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r2!, {r3, r4, r5}
	LSR      r4, r6, #1
	STR      r3, [sp, #0x3e0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	CMP      r7, #0xc4
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x18
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x20
	LDR      r6, [pc, #0x114]
	LDR      r5, [pc, #0x114]
	BCC      |sub_08026660|
	LDR      r0, [r5]
	LDR      r3, [r6, #4]
	ADD      r1, r0, #4
	LDR      r5, [r1]
	MOV      r0, #0
	CMP      r5, #0
	BLE      |loc_0802664E|
|loc_0802663E|
	LSL      r2, r0, #2
	ADD      r2, r2, r1
	LDR      r2, [r2, #4]
	CMP      r2, r3
	BEQ      |loc_0802665C|
	ADD      r0, #1
	CMP      r5, r0
	BGT      |loc_0802663E|
|loc_0802664E|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802665C|
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
|sub_08026660|
|unk_08026660|
		LSL r0, r0, #0x15
		LSR r0, r0, #0x18
		STRB r0, [r4, #0x11]
		CMP r0, #2
		BLS      |loc_08026674|
		ADD r0, #1
		LSL r0, r0, #0x1f
		LSR r0, r0, #0x1f
		ADD r0, #1
		STRB r0, [r4, #0x11]
|loc_08026674|
		LDRH r0, [r4, #0x12]
		CMP r0, #8
		BNE      |loc_0802665C|
		LDR r0, [r5]
		BL       |loc_080116FC|
		CMP r0, #0x80
		BLT      |loc_0802665C|
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #4]
		ADD r0, r1, #0
		STR r1, [sp]
		LDR r1, [sp, #4]
		STR r0, [sp, #8]
		STR r1, [sp, #0xc]
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0xa0]
		ADD r1, #4
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #8]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0xc]
		LDR r0, [r0, #4]
		STR r1, [sp]
		ADD r0, r2, r0
		STR r0, [sp, #4]
		ADD r0, r1, #0
		LDR r1, [sp, #4]
		STR r0, [sp, #0x10]
		STR r1, [sp, #0x14]
		ADD r3, r4, #0
		MOV r0, #0
		LDRB r2, [r4, #0x10]
		ADD r1, sp, #0x10
		BL       |inc_0x1c3f2_0x2ab4c| + 0xdefa
		ADD r1, r0, #0
		STR r0, [r6, #4]
		LDR r0, [r5]
	INCBIN  baserom.gba_0x266d2_0x266d4.extracted
|sub_080266D4|
|unk_080266D4|
	INCBIN	baserom.gba_0x266d4_0x266d8.extracted
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x6c]
	SUB      sp, #0x10
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x64]
	STR      r1, [sp, #8]
	CMP      r4, #0
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	BEQ      |loc_080266F6|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_080266F6|
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x38]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x40]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_08026722|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08026722|
	ADD      sp, #0x10
	POP      {r4, pc}
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0x14]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_08026734|
	MOV      r0, #0
|loc_08026734|
	SUB      r0, r2, r0
	BX       lr
	LDR      r0, [pc, #4]
	ADD      r0, #8
	BX       lr
	LSL      r0, r0, #0
	CMP      r7, #0xcc
	LSL      r0, r0, #0xc
	LDMIA    r2!, {r2, r3, r5, r6}
	LSR      r4, r6, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	ADD      r0, r1, #0
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	STRB     r2, [r0, #0x11]
	MOV      r1, #0x12
	BL       |inc_0x0158_0x143f2| + 0xeb82
	POP      {r3, pc}
	PUSH     {r4, r5, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x1c
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x20
	BCC      |sub_08026790|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
|sub_08026790|
|unk_08026790|
		LSR r0, r0, #3
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #8
		DCW     0xD1F8
		LDR r5, [pc, #0xd4]
		LDR r0, [r5, #4]
		BL       |loc_080116FC|
		CMP r0, #0x80
		DCW     0xDBF2
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0xac]
		ADD r1, #8
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #0xc]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0x10]
		LDR r0, [r0, #4]
		STR r1, [sp, #4]
		ADD r0, r2, r0
		STR r0, [sp, #8]
		ADD r0, r1, #0
		LDR r1, [sp, #8]
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x18]
		ADD r3, r4, #0
		MOV r0, #0
		LDRB r2, [r4, #0x10]
		ADD r1, sp, #0x14
		BL       |inc_0x1c3f2_0x2ab4c| + 0xb2b6
		ADD r1, r0, #0
		LDR r0, [r5, #4]
		BL       |sub_0801191A|
		LDR r4, [pc, #0x80]
		LDR r0, [r5]
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r0, r4
		LDR r1, [pc, #0x70]
	INCBIN  baserom.gba_0x26802_0x26804.extracted
|sub_08026804|
|unk_08026804|
	INCBIN	baserom.gba_0x26804_0x26808.extracted
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x70]
	SUB      sp, #0x10
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x68]
	STR      r1, [sp, #8]
	CMP      r4, #0
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	BEQ      |loc_08026826|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_08026826|
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x4c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x48]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_08026852|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08026852|
	ADD      sp, #0x10
	POP      {r4, pc}
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0x28]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_08026864|
	MOV      r0, #0
|loc_08026864|
	SUB      r0, r2, r0
	BX       lr
	LDR      r0, [pc, #0x18]
	ADD      r0, #4
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r2!, {r2, r3, r4, r7}
	LSR      r4, r6, #1
	STR      r3, [sp, #0x3e0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	CMP      r7, #0xd8
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r0, [pc, #0xbc]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x40
	CMP      r1, #0
	BEQ      |loc_080268A4|
	MOV      r0, #0xff
	ADD      r0, #0xcd
	LDR      r0, [r0, r1]
	CMP      r0, #0
	BNE      |sub_080268AA|
|loc_080268A4|
	MOV      r0, #0
	ADD      sp, #0x40
	POP      {r4, pc}
|sub_080268AA|
|unk_080268AA|
		ADD r0, sp, #8
		BL       |sub_0800FDFA|
		LDR r0, [sp, #8]
		LDR r1, [sp, #0x10]
		LDR r2, [sp, #0x14]
		ADD r1, r0, r1
		LDR r0, [sp, #0xc]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp]
		STR r1, [sp, #0x18]
		STR r0, [sp, #4]
		STR r0, [sp, #0x1c]
		ADD r0, sp, #0x20
		ADD r1, r4, #0
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0x20]
		LDR r1, [sp, #0x28]
		LDR r2, [sp, #0x2c]
		ADD r1, r0, r1
		LDR r0, [sp, #0x24]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		STR r0, [sp, #4]
		STR r0, [sp, #0x34]
		ASR r1, r1, #1
		LDR r0, [sp, #0x18]
		STR r1, [sp]
		SUB r0, r0, r1
		STR r1, [sp, #0x30]
		LDR r1, [sp, #0x1c]
		LDR r2, [sp, #0x34]
		STR r0, [sp]
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #4]
		STR r1, [sp, #0x3c]
		STR r0, [sp, #0x38]
		BGE      |loc_0802690A|
		NEG r0, r2
|loc_0802690A|
		ADD r1, r0, #0
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BGE      |loc_08026914|
		NEG r0, r0
|loc_08026914|
		STR r0, [sp, #0x34]
		ADD r0, r1, #0
		STR r1, [sp, #0x30]
		LDR r1, [sp, #0x34]
		CMP r0, #0x10
		BLT      |loc_08026924|
		CMP r1, #0x10
		BGE      |loc_08026928|
|loc_08026924|
		MOV r0, #1
		DCW     0xE7BE
|loc_08026928|
		MOV r0, #0
		DCW     0xE7BC
|sub_0802692C|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08026948|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08026948|
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	ADD      r1, pc, #0x80
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08026966|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802697C|
|loc_08026966|
	LDR      r1, [pc, #0x1c8]
	LDR      r3, [pc, #0x1c8]
	STR      r1, [r0]
	LDR      r1, [r4]
	MUL      r1, r3
	ASR      r1, r1, #8
	STR      r1, [r0, #4]
	LDR      r1, [r4, #4]
	MUL      r1, r3
	ASR      r1, r1, #8
	STR      r1, [r0, #8]
|loc_0802697C|
	POP      {r4, pc}
	PUSH     {r3, lr}
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	ADD      r0, r1, #0
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	STRB     r2, [r0, #0x11]
	MOV      r1, #0x12
	BL       |inc_0x0158_0x143f2| + 0xeb82
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x18
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x18
	BCC      |sub_080269BC|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
|sub_080269BC|
|unk_080269BC|
		LSR r0, r0, #3
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #0x10
		DCW     0xD1F8
		LDR r5, [pc, #0x170]
		LDR r0, [r5]
		BL       |loc_080116FC|
		MOV r1, #0xff
		ADD r1, #1
		CMP r0, r1
|loc_080269D4|
|unk_080269D4|
		DCW     0xDBF0
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #4]
		ADD r0, r1, #0
		STR r1, [sp]
		LDR r1, [sp, #4]
		STR r0, [sp, #8]
		STR r1, [sp, #0xc]
		LDRB r0, [r4, #0x10]
		ADD r1, r5, #4
		ADD r3, r4, #0
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #8]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0xc]
		LDR r0, [r0, #4]
		STR r1, [sp]
		ADD r0, r2, r0
		STR r0, [sp, #4]
		ADD r0, r1, #0
		LDR r1, [sp, #4]
		STR r0, [sp, #0x10]
		ADD r2, r6, #4
		STR r1, [sp, #0x14]
		ADD r1, sp, #0x10
		MOV r0, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x2f2
		ADD r1, r0, #0
		LDR r0, [r5]
		BL       |sub_0801191A|
		DCW     0xE7C8
|sub_08026A26|
	PUSH     {r4, r5, r6, lr}
	LDR      r0, [pc, #0x110]
	SUB      sp, #0x30
	MOV      r5, #0
	LDR      r0, [r0]
	ADD      r4, r1, #0
	LDR      r2, [pc, #0x110]
	ADD      r1, r5, #0
	CMP      r4, #0
	STR      r5, [sp, #0x28]
	LDR      r6, [pc, #0x104]
	STR      r0, [sp, #0x2c]
	STR      r2, [sp, #0x24]
	BEQ      |loc_08026A48|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_08026A48|
	ADD      r0, sp, #0x24
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	LDR      r0, [pc, #0xec]
	LDR      r0, [r0]
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #8]
	ADD      r0, r1, #0
	STR      r0, [sp, #0xc]
	STR      r1, [sp, #4]
	LDR      r1, [sp, #8]
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	STR      r1, [sp, #0x10]
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #8]
	ADD      r0, r1, #0
	STR      r1, [sp, #4]
	LDR      r1, [sp, #8]
	STR      r0, [sp, #0x14]
	STR      r1, [sp, #0x18]
	LDR      r1, [sp, #0x14]
	LDR      r0, [sp, #0xc]
	LDR      r2, [sp, #0x18]
	SUB      r1, r0, r1
	LDR      r0, [sp, #0x10]
	STR      r1, [sp, #4]
	SUB      r0, r0, r2
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x20]
	STR      r1, [sp, #0x1c]
	LDRB     r1, [r4, #0x10]
	MOV      r0, #1
	CMP      r1, #2
	BCS      |loc_08026AA2|
	MOV      r0, #0
|loc_08026AA2|
	LSL      r0, r0, #2
	ADD      r1, sp, #0x1c
	ADD      r0, r0, r1
	STR      r5, [r0]
	MOV      r0, #0x7f
	LDR      r1, [sp, #0x1c]
	MVN      r0, r0
	CMP      r1, r0
	BGE      |loc_08026AB6|
	STR      r0, [sp, #0x1c]
|loc_08026AB6|
	LDR      r2, [sp, #0x1c]
	MOV      r1, #0x80
	CMP      r2, #0x80
	BLE      |loc_08026AC0|
	STR      r1, [sp, #0x1c]
|loc_08026AC0|
	LDR      r2, [sp, #0x20]
	CMP      r2, r0
	BGE      |loc_08026AC8|
	STR      r0, [sp, #0x20]
|loc_08026AC8|
	LDR      r0, [sp, #0x20]
	CMP      r0, #0x80
	BLE      |loc_08026AD0|
	STR      r1, [sp, #0x20]
|loc_08026AD0|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08026AF0|
	LDR      r1, [pc, #0x54]
	LDR      r3, [pc, #0x54]
	STR      r1, [r0]
	LDR      r1, [sp, #0x1c]
	MUL      r1, r3
	ASR      r1, r1, #8
	STR      r1, [r0, #4]
	LDR      r1, [sp, #0x20]
	MUL      r1, r3
	ASR      r1, r1, #8
	STR      r1, [r0, #8]
|loc_08026AF0|
	ADD      r5, r0, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [sp, #0x28]
	STR      r6, [sp, #0x24]
	CMP      r0, #0
	BEQ      |loc_08026B16|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08026B16|
	ADD      sp, #0x30
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
|sub_08026B2C|
|unk_08026B2C|
	INCBIN	baserom.gba_0x26b2c_0x26b32.extracted
|sub_08026B32|
	LSR      r4, r0, #0x20
	LSL      r5, r3, #0x1c
	LSL      r0, r0, #0
	LDMIA    r2!, {r4, r6, r7}
	LSR      r4, r6, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	CMP      r7, #0xe0
	LSL      r0, r0, #0xc
|loc_08026B4C|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08026B66|
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08026B66|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08026B66|
|unk_08026B66|
		LDR r0, [pc, #0x124]
		LDR r6, [pc, #0x124]
		STR r0, [r4]
		MOV r0, #0x80
		STRH r0, [r4, #0xe]
		LDR r0, [r6]
		MOV r1, #0x80
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08026B8C|
		MOV r1, #0x80
		LDR r0, [r6]
		BL       |sub_08011732|
		MOV r1, #0x80
		LDR r0, [r6]
		BL       |loc_0801124C|
|loc_08026B8C|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		STRH r0, [r4, #0xc]
		LDR r1, [pc, #0x100]
		LDR r2, [pc, #0xf8]
		STR r1, [r4]
		STR r7, [r4, #0x18]
		MOV r1, #0
		STRB r1, [r4, #0x11]
		STRB r1, [r4, #0x12]
		LSL r1, r5, #3
		ADD r2, #4
		ADD r1, r1, r2
		LDR r2, [pc, #0xf0]
		STRB r5, [r4, #0x10]
		LSL r0, r0, #5
		ADD r0, r0, r2
		STR r1, [r4, #0x14]
		LDR r1, [r1, #4]
		MOV r2, #0x80
		BL       |sub_08049138|
		ADD r0, r4, #0
		DCW     0xE7D3
		PUSH {r3, lr}
		ADD r1, r0, #0
		LDRB r3, [r1, #0x10]
		MOV r2, #1
		LSL r2, r2, #0xf
		CMP r3, #0
		BEQ      |loc_08026BE6|
		CMP r3, #1
		BEQ      |loc_08026BFA|
		CMP r3, #2
		BEQ      |loc_08026C0E|
		CMP r3, #3
		BNE      |loc_08026C24|
		LDR r0, [r1, #0x18]
		ADD r0, r0, r2
		LDR r2, [r0, #0x2c]
		LDR r0, [r0, #0x24]
		CMP r2, r0
		BGE      |loc_08026C22|
		MOV r0, #1
		B        |loc_08026C24|
|loc_08026BE6|
		LDR r0, [r1, #0x18]
		ADD r0, r0, r2
		LDR r2, [r0, #0x30]
		LDR r0, [r0, #0x28]
		CMP r2, r0
		BGE      |loc_08026BF6|
		MOV r0, #1
		B        |loc_08026C24|
|loc_08026BF6|
		MOV r0, #0
		B        |loc_08026C24|
|loc_08026BFA|
		LDR r0, [r1, #0x18]
		ADD r0, r0, r2
		LDR r2, [r0, #0x30]
		LDR r0, [r0, #0x20]
		CMP r2, r0
		BLE      |loc_08026C0A|
		MOV r0, #1
		B        |loc_08026C24|
|loc_08026C0A|
		MOV r0, #0
		B        |loc_08026C24|
|loc_08026C0E|
		LDR r0, [r1, #0x18]
		ADD r0, r0, r2
		LDR r2, [r0, #0x2c]
		LDR r0, [r0, #0x1c]
		CMP r2, r0
		BLE      |loc_08026C1E|
		MOV r0, #1
		B        |loc_08026C24|
|loc_08026C1E|
		MOV r0, #0
		B        |loc_08026C24|
|loc_08026C22|
		MOV r0, #0
|loc_08026C24|
		CMP r0, #0
		BEQ      |sub_08026C3C|
		LDRB r0, [r1, #0x12]
		ADD r0, #1
		STRB r0, [r1, #0x12]
		LSL r0, r0, #0x1b
		LSR r2, r0, #0x1d
		CMP r2, #4
		DCW     0xDB05
		MOV r0, #7
		SUB r2, r0, r2
		DCW     0xE002
|sub_08026C3C|
	MOV      r2, #3
	MOV      r0, #0x10
	STRB     r0, [r1, #0x12]
	LDRB     r0, [r1, #0x11]
	CMP      r0, r2
	BEQ      |loc_08026C60|
	STRB     r2, [r1, #0x11]
	LDRH     r0, [r1, #0xc]
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0x48]
	LDR      r1, [r1, #4]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	LSL      r2, r2, #7
	ADD      r1, r1, r2
	MOV      r2, #0x80
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08026C60|
	POP      {r3, pc}
	LDR      r2, [r1]
	ADD      r3, r2, #0
	ADD      r3, #8
	STR      r3, [r1]
	LDR      r1, [r0, #0x14]
	LDR      r1, [r1]
	STR      r1, [r2]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r2, #4]
	LSR      r1, r1, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r1, r1, #0xa
	ORR      r0, r1
	MOV      r1, #3
	LSL      r1, r1, #0xa
	BIC      r0, r1
	STR      r0, [r2, #4]
	MOV      r0, #0
	BX       lr
|sub_08026C8A|
	DCW      0x0000
	DCW      0x9680,0x0804,0xcb00
|sub_08026C92|
	LSR      r4, r6, #1
	STMIA    r0!, {r3, r6}
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r6, r3, #0
	ADD      r4, r2, #0
	CMP      r0, #0
	LDR      r5, [sp, #0x18]
	BNE      |loc_08026CB4|
	MOV      r0, #0x20
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08026CD8|
|loc_08026CB4|
	LDR      r1, [pc, #0x114]
	STR      r1, [r0]
	STR      r4, [r0, #0x1c]
	STR      r7, [r0, #0x10]
	STRH     r6, [r0, #0xc]
	LDRH     r1, [r4, #0x14]
	ADD      r1, r1, r5
	STRH     r1, [r0, #0x14]
	LDRB     r2, [r4, #0x16]
	MOV      r1, #1
	CMP      r2, #0
	BNE      |loc_08026CCE|
	MOV      r1, #0
|loc_08026CCE|
	STR      r1, [r0, #0x18]
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	LDR      r1, [r4, #0xc]
	STR      r1, [r0, #4]
|loc_08026CD8|
	POP      {r3, r4, r5, r6, r7, pc}
	LDR      r1, [r0, #0x18]
	CMP      r1, #0
	BNE      |loc_08026CE4|
	MOV      r0, #0
	BX       lr
|loc_08026CE4|
	LDR      r1, [r0, #0x1c]
	LDR      r0, [r0, #0x10]
	LDR      r2, [pc, #0xe4]
	ADD      r0, r0, r2
	LDR      r2, [r1]
	LDR      r3, [r0, #8]
	CMP      r2, r3
	BGE      |sub_08026D10|
	LDR      r2, [r0]
	LDR      r3, [r1, #8]
	CMP      r2, r3
	BGE      |sub_08026D10|
	LDR      r2, [r1, #4]
	LDR      r3, [r0, #0xc]
	CMP      r2, r3
	BGE      |sub_08026D10|
	LDR      r0, [r0, #4]
	LDR      r1, [r1, #0xc]
	CMP      r0, r1
	BGE      |sub_08026D10|
	MOV      r0, #1
	BX       lr
|sub_08026D10|
|unk_08026D10|
		MOV r0, #0
		BX       lr
|sub_08026D14|
	PUSH     {r4, r5}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	SUB      sp, #0x10
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	LDR      r2, [r0, #0x10]
	LDR      r4, [pc, #0xa8]
	LDR      r3, [r0, #0x1c]
	ADD      r2, r2, r4
	LDR      r4, [r3]
	LDR      r5, [r2]
	LDR      r3, [r3, #4]
	LDR      r2, [r2, #4]
	SUB      r4, r4, r5
	SUB      r2, r3, r2
	STR      r2, [sp, #4]
	LDR      r3, [sp, #4]
	STR      r4, [sp]
	STR      r3, [sp, #0xc]
	STR      r4, [sp, #8]
	LDR      r2, [r0, #0x1c]
	ADD      r3, r4, #0
	LDR      r4, [pc, #0x8c]
	LDR      r2, [r2, #0x10]
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	AND      r2, r4
	ORR      r3, r2
	LDR      r2, [sp, #0xc]
	LSR      r3, r3, #8
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x18
	LSL      r3, r3, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRH     r0, [r0, #0x14]
	LDR      r2, [r1, #4]
	LSR      r2, r2, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r2, r2, #0xa
	ORR      r0, r2
	MOV      r2, #3
	LSL      r2, r2, #0xa
	ORR      r0, r2
	STR      r0, [r1, #4]
	ADD      sp, #0x10
	POP      {r4, r5}
	MOV      r0, #0
	BX       lr
	CMP      r1, #4
	BNE      |sub_08026D96|
	LDRH     r3, [r0, #0xc]
	ASR      r1, r2, #1
	CMP      r1, r3
	BNE      |sub_08026D92|
	LSL      r1, r2, #0x1f
	LSR      r1, r1, #0x1f
	STR      r1, [r0, #0x18]
	MOV      r0, #1
	BX       lr
|sub_08026D92|
|unk_08026D92|
		MOV r0, #0
|loc_08026D94|
|unk_08026D94|
		BX       lr
|sub_08026D96|
	CMP      r1, #8
	BNE      |sub_08026DA4|
	LDRH     r1, [r0, #0xc]
	CMP      r1, r2
	BEQ      |loc_08026D94|
	MOV      r0, #0
	BX       lr
|sub_08026DA4|
|unk_08026DA4|
		MOV r0, #0
		BX       lr
|sub_08026DA8|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x28]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [pc, #0x28]
	LDRH     r1, [r4, #0x14]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
	LDR      r0, [pc, #0x20]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08026DCA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08026DCA|
	POP      {r3, r4, r5, pc}
|sub_08026DCC|
	DCW      0xda60
	DCW      0x0804,0x802c,0x0000,0xffff,0xfe00,0xe148,0x0804,0xcf24
	DCW      0x0874,0xe454
|sub_08026DE2|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r6, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08026DFE|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08026DFE|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08026DFE|
|unk_08026DFE|
		LDR r0, [pc, #0x178]
		LDR r5, [pc, #0x178]
		STR r0, [r4]
		MOV r0, #0x40
		STRH r0, [r4, #0xe]
		LDR r0, [r5]
		MOV r1, #0x40
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08026E24|
		MOV r1, #0x40
		LDR r0, [r5]
		BL       |sub_08011732|
		MOV r1, #0x40
		LDR r0, [r5]
		BL       |loc_0801124C|
|loc_08026E24|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LDR r1, [pc, #0x154]
		STRH r0, [r4, #0xc]
		STR r1, [r4]
		LDR r1, [r7, #4]
		LDR r2, [r7]
		STR r1, [r4, #0x20]
		STR r2, [r4, #0x1c]
		STR r6, [r4, #0x10]
		MOV r2, #0
		STR r2, [r4, #0x14]
		STR r2, [r4, #0x18]
		MOV r2, #0x37
		STRB r2, [r4, #8]
		STR r1, [r4, #4]
		LDR r1, [pc, #0x134]
		LDR r2, [pc, #0x13c]
		ADD r1, #4
		CMP r6, #0
		BEQ      |loc_08026E5A|
		LSL r0, r0, #5
		ADD r0, r0, r2
		MOV r2, #0x40
		BL       |sub_08049138|
		B        |loc_08026E66|
|loc_08026E5A|
		LSL r0, r0, #5
		ADD r0, r0, r2
		MOV r2, #0x40
		ADD r1, #0x80
		BL       |sub_08049138|
|loc_08026E66|
		ADD r0, r4, #0
		DCW     0xE7C8
|sub_08026E6A|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x10]
	CMP      r1, #0
	BEQ      |loc_08026EA2|
	LDR      r1, [r0, #0x14]
	ADD      r1, #1
	STR      r1, [r0, #0x14]
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x1d
	CMP      r1, #4
	BLT      |loc_08026E84|
	MOV      r2, #7
	SUB      r1, r2, r1
|loc_08026E84|
	LDR      r2, [r0, #0x18]
	CMP      r2, r1
	BEQ      |loc_08026EA2|
	STR      r1, [r0, #0x18]
	LDRH     r0, [r0, #0xc]
	LDR      r2, [pc, #0xf4]
	LSL      r1, r1, #6
	LSL      r0, r0, #5
	ADD      r0, r0, r2
	LDR      r2, [pc, #0xe4]
	ADD      r2, #4
	ADD      r1, r1, r2
	MOV      r2, #0x40
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08026EA2|
	POP      {r3, pc}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	MOV      r2, #1
	LSL      r2, r2, #0xd
	STR      r2, [r1]
|loc_08026EB4|
	LDR      r3, [r0, #0x1c]
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x20]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRH     r0, [r0, #0xc]
	LDR      r2, [r1, #4]
	LSR      r2, r2, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r2, r2, #0xa
	ORR      r0, r2
	MOV      r2, #3
	LSL      r2, r2, #0xa
	ORR      r0, r2
	STR      r0, [r1, #4]
	MOV      r0, #0
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #8
	BNE      |sub_08026F04|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08026F04|
	ADD      r0, r4, #0
	ADD      sp, #8
	POP      {r4, r5, r6, pc}
|sub_08026F04|
|unk_08026F04|
		MOV r0, #0
		STR r0, [sp]
		STR r0, [sp, #4]
		MOV r2, #1
		ADD r0, r4, #0
		MOV r1, sp
		BL       |inc_0x1c3f2_0x2ab4c| + 0xa9f2
		LDR r0, [pc, #0x70]
		STR r0, [r4]
		STR r6, [r4, #0x2c]
		LDR r0, [r5]
		LDR r1, [r5, #4]
		SUB r0, #4
		STR r0, [r4, #0x24]
		SUB r1, #4
		STR r1, [r4, #0x28]
		ADD r0, r4, #0
		DCW     0xE7EA
|sub_08026F2A|
	PUSH     {r4}
	LDR      r1, [r0, #0x2c]
	LDR      r3, [pc, #0x5c]
	SUB      sp, #8
	ADD      r1, r1, r3
	LDR      r4, [r1]
	LDR      r3, [r0, #0x24]
	ADD      r2, r0, #0
	SUB      r3, r3, r4
	LDR      r4, [r0, #0x28]
	LDR      r1, [r1, #4]
	STR      r3, [sp]
	SUB      r1, r4, r1
	STR      r1, [sp, #4]
	ADD      r1, r3, #0
	LDR      r3, [sp, #4]
	ADD      r2, #0x1c
	STMIA    r2!, {r1, r3}
	LDR      r2, [pc, #0x40]
	LDR      r1, [r0, #0x1c]
	LDR      r3, [r2]
	CMP      r1, r3
	BLT      |sub_08026F74|
	LDR      r3, [r2, #8]
	CMP      r1, r3
	BGE      |sub_08026F74|
	LDR      r0, [r0, #0x20]
	LDR      r1, [r2, #4]
	CMP      r0, r1
	BLT      |sub_08026F74|
	LDR      r1, [r2, #0xc]
	CMP      r0, r1
	BGE      |sub_08026F74|
	MOV      r0, #1
	ADD      sp, #8
	POP      {r4}
	BX       lr
|sub_08026F74|
|unk_08026F74|
		MOV r0, #0
		DCW     0xE7FA
|sub_08026F78|
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	LDMIA    r7!, {r3, r5}
	LSR      r4, r6, #1
	BVS      |loc_08026FEC|
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	BPL      |loc_08026EB4|
	LSR      r4, r0, #0x20
	STRH     r4, [r5]
	LSL      r0, r0, #0
	BEQ      |loc_08026FEC|
	LSR      r4, r6, #1
|loc_08026F94|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	BNE      |sub_08026FA8|
	LDR      r0, [pc, #0x210]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08026FA8|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08026FA8|
|unk_08026FA8|
		LDR r0, [pc, #0x204]
		MOV r6, #1
		LSL r6, r6, #0xa
		LDR r5, [pc, #0x204]
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		LDR r0, [r5, #4]
		ADD r1, r6, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08026FD0|
		ADD r1, r6, #0
		LDR r0, [r5, #4]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5, #4]
		BL       |loc_0801124C|
|loc_08026FD0|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x1e4]
		MOV r5, #0xf
		STR r0, [r4]
		MOV r0, #0xc1
		LSL r0, r0, #4
		ADD r2, r4, r0
		MOV r7, #5
		LSL r7, r7, #0xc
		LSL r5, r5, #0xb
		STMIA r2!, {r5, r7}
		ADD r0, #8
		ADD r1, r4, r0
		MOV r5, #0
|loc_08026FEC|
|unk_08026FEC|
		STR r5, [r1]
		ADD r7, r4, #0
		ADD r7, #0x10
		STR r5, [r1, #4]
		LDR r0, [pc, #0x1bc]
		ADD r1, r7, #0
		ADD r0, #8
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LDRH r0, [r4, #0xc]
		LDR r1, [pc, #0x1b8]
		ADD r2, r6, #0
		LSL r0, r0, #5
		ADD r0, r0, r1
		ADD r1, r7, #0
		BL       |sub_08049138|
		MOV r0, #0x10
		STRB r0, [r4, #8]
		MOV r0, #3
		LSL r0, r0, #0xa
		ADD r0, r4, r0
		STR r5, [r0, #0x24]
		STR r5, [r0, #0x20]
		ADD r0, r4, #0
		DCW     0xE7C2
		PUSH {r3, r4, r5, r6, r7, lr}
		LDR r7, [pc, #0x190]
		ADD r5, r0, #0
		LDR r0, [r7]
		MOV r1, #3
		LDRH r0, [r0, #4]
		LSL r1, r1, #0xa
		ADD r4, r5, r1
		LSL r0, r0, #0x1f
		LSR r0, r0, #0x1f
		MOV r6, #0
		CMP r0, #0
		BEQ      |loc_08027040|
		MOV r0, #1
		STR r0, [r4, #0x24]
		STR r6, [r4, #0x20]
|loc_08027040|
		LDR r0, [r7]
		LDRH r0, [r0, #6]
		LSL r0, r0, #0x1f
		BEQ      |loc_0802704A|
		STR r6, [r4, #0x24]
|loc_0802704A|
		MOV r2, #1
		LDR r1, [r4, #0x24]
		LSL r2, r2, #0xa
		CMP r1, #0
		LDR r1, [r4, #0x20]
		LDR r0, [pc, #0x164]
		BEQ      |sub_08027078|
		CMP r1, #4
		BGE      |loc_08027096|
		ADD r1, #1
		STR r1, [r4, #0x20]
		LSL r3, r1, #0x1f
		BMI      |loc_08027096|
		LDRH r3, [r5, #0xc]
		ASR r1, r1, #1
		LSL r1, r1, #0xa
		LSL r3, r3, #5
		ADD r0, r3, r0
		ADD r1, r1, r5
		ADD r1, #0x10
		BL       |sub_08049138|
		B        |loc_08027096|
|sub_08027078|
	CMP      r1, #0
	BEQ      |loc_08027096|
	SUB      r1, #1
	STR      r1, [r4, #0x20]
	LSL      r3, r1, #0x1f
	BMI      |loc_08027096|
	LDRH     r3, [r5, #0xc]
	ASR      r1, r1, #1
	LSL      r1, r1, #0xa
	LSL      r3, r3, #5
	ADD      r0, r3, r0
	ADD      r1, r1, r5
	ADD      r1, #0x10
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08027096|
	LDR      r0, [r7]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x1a
	LSR      r1, r0, #0x1f
	LDR      r0, [pc, #0x120]
	ADD      r0, r5, r0
	CMP      r1, #0
	BEQ      |loc_080270AC|
	LDR      r1, [r0]
	SUB      r1, #0x80
	STR      r1, [r0]
|loc_080270AC|
	LDR      r1, [r7]
	ADD      r3, r7, #0
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x1b
	LSR      r1, r1, #0x1f
	BEQ      |loc_080270BE|
	LDR      r1, [r0]
	ADD      r1, #0x80
	STR      r1, [r0]
|loc_080270BE|
	LDR      r1, [r3]
	LDR      r2, [pc, #0x100]
	LDRH     r1, [r1, #2]
	ADD      r2, r5, r2
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	CMP      r1, #0
	BEQ      |loc_080270D4|
	LDR      r1, [r2]
	SUB      r1, #0x80
	STR      r1, [r2]
|loc_080270D4|
	LDR      r1, [r3]
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x1f
	BEQ      |loc_080270E4|
	LDR      r1, [r2]
	ADD      r1, #0x80
	STR      r1, [r2]
|loc_080270E4|
	MOV      r1, #0xc1
	LSL      r1, r1, #4
	ADD      r1, r5, r1
	LDR      r3, [r1]
	LDR      r7, [r0]
	ADD      r3, r3, r7
	STR      r3, [r1]
	LDR      r7, [r1, #4]
	LDR      r3, [r0, #4]
	ADD      r3, r7, r3
	STR      r3, [r1, #4]
	LDR      r7, [r4, #0x18]
	LSL      r3, r7, #1
	ADD      r3, r3, r7
	ASR      r7, r3, #0x1f
	LSR      r7, r7, #0x1e
	ADD      r3, r7, r3
	ASR      r3, r3, #2
	STR      r3, [r4, #0x18]
	LDR      r7, [r4, #0x1c]
	LSL      r3, r7, #1
	ADD      r3, r3, r7
	ASR      r7, r3, #0x1f
	LSR      r7, r7, #0x1e
	ADD      r3, r7, r3
	ASR      r3, r3, #2
	STR      r3, [r4, #0x1c]
	MOV      r3, #1
	LDR      r4, [r1]
	LSL      r3, r3, #0xc
	CMP      r4, r3
	BGE      |loc_08027128|
	STR      r3, [r1]
	STR      r6, [r0]
|loc_08027128|
	MOV      r4, #7
	LDR      r7, [r1]
	LSL      r4, r4, #0xd
	CMP      r7, r4
	BLE      |loc_08027136|
	STR      r4, [r1]
	STR      r6, [r0]
|loc_08027136|
	LDR      r0, [pc, #0x90]
	ADD      r0, r5, r0
	LDR      r1, [r0]
	CMP      r1, r3
	BGE      |loc_08027144|
	STR      r3, [r0]
	STR      r6, [r2]
|loc_08027144|
	MOV      r1, #9
	LDR      r3, [r0]
	LSL      r1, r1, #0xc
	CMP      r3, r1
	BLE      |loc_08027152|
	STR      r1, [r0]
	STR      r6, [r2]
|loc_08027152|
	POP      {r3, r4, r5, r6, r7, pc}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	MOV      r3, #0xc1
	LDR      r2, [pc, #0x68]
	LSL      r3, r3, #4
	ADD      r3, r0, r3
	STR      r2, [r1]
	LDR      r3, [r3]
	ASR      r3, r3, #8
	SUB      r3, #0x10
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	LDR      r3, [pc, #0x50]
	STR      r2, [r1]
	ADD      r3, r0, r3
	LDR      r3, [r3]
	LSR      r2, r2, #8
	ASR      r3, r3, #8
	ADD      r3, #0xf0
	LSL      r3, r3, #0x18
|loc_08027184|
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRH     r0, [r0, #0xc]
	LDR      r2, [r1, #4]
	LSR      r2, r2, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r2, r2, #0xa
	ORR      r0, r2
	MOV      r2, #3
	LSL      r2, r2, #0xa
	BIC      r0, r2
	MOV      r2, #1
	LSL      r2, r2, #0xa
	ADD      r0, r0, r2
	STR      r0, [r1, #4]
	MOV      r0, #0
	BX       lr
|sub_080271AC|
|unk_080271AC|
	INCBIN	baserom.gba_0x271ac_0x271ae.extracted
|sub_080271AE|
	LSL      r0, r0, #0
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	BEQ      |loc_08027230|
	LSR      r4, r6, #1
	BPL      |loc_08027184|
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	LSR      r0, r3, #0x10
	LSL      r0, r0, #0
	LSR      r4, r3, #0x10
	LSL      r0, r0, #0
	LSR      r4, r2, #0x10
	LSL      r0, r0, #0
	MOV      r0, #0
	STRH     r0, [r0]
|loc_080271D0|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_080271E8|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_080271E8|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_080271E8|
	LDR      r0, [pc, #0xb0]
	LDR      r6, [pc, #0xb4]
	STR      r0, [r4]
	MOV      r0, #0x40
	STRH     r0, [r4, #0xe]
	LDR      r0, [r6]
	MOV      r1, #0x40
	BL       |inc_0x0158_0x143f2| + 0x110f4
	ADD      r3, r0, #1
	BNE      |loc_0802720E|
	MOV      r1, #0x40
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x115da
	MOV      r1, #0x40
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x110f4
|loc_0802720E|
	STRH     r0, [r4, #0xc]
	LDR      r0, [pc, #0x90]
	STR      r0, [r4]
	MOV      r0, #0
	STR      r0, [r4, #0x14]
	STRB     r5, [r4, #0x1c]
	MOV      r0, #1
	STR      r0, [r4, #0x20]
	LDR      r0, [pc, #0x80]
	ADD      r0, #0x94
	CMP      r5, #2
	BGE      |loc_08027228|
	SUB      r0, #0x80
|loc_08027228|
	STR      r0, [r4, #0x10]
	MOV      r0, #0
	MVN      r0, r0
	STR      r0, [r4, #0x18]
|loc_08027230|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|sub_08027234|
|unk_08027234|
		PUSH {r3, lr}
		ADD r1, r0, #0
		LDR r0, [r0, #0x20]
		CMP r0, #0
		BEQ      |sub_0802724A|
		LDR r0, [r1, #0x14]
		ADD r0, #1
		STR r0, [r1, #0x14]
		LSL r0, r0, #0x1b
		LSR r2, r0, #0x1f
		DCW     0xE001
|sub_0802724A|
	MOV      r2, #0
	STR      r2, [r1, #0x14]
	LDR      r0, [r1, #0x18]
	CMP      r0, r2
	BEQ      |loc_0802726A|
	STR      r2, [r1, #0x18]
	LDRH     r0, [r1, #0xc]
	LDR      r3, [pc, #0x4c]
	LDR      r1, [r1, #0x10]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	LSL      r2, r2, #6
	ADD      r1, r1, r2
	MOV      r2, #0x40
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0802726A|
	POP      {r3, pc}
	LDR      r2, [r1]
	ADD      r3, r2, #0
	ADD      r3, #8
	STR      r3, [r1]
	LDRB     r1, [r0, #0x1c]
	LDR      r3, [pc, #0x28]
	ADD      r3, #4
	LSL      r1, r1, #2
	LDR      r1, [r3, r1]
	STR      r1, [r2]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r2, #4]
	LSR      r1, r1, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r1, r1, #0xa
	ORR      r0, r1
	MOV      r1, #3
	LSL      r1, r1, #0xa
	BIC      r0, r1
	STR      r0, [r2, #4]
	MOV      r0, #0
	BX       lr
	LSL      r0, r0, #0
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	BCS      |loc_08027334|
	LSR      r4, r6, #1
	BVS      |loc_080272C0|
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
|loc_080272AC|
	PUSH     {r4, r5}
	LDRB     r2, [r0, #0x11]
	LDR      r1, [r0, #0x50]
	MOV      r3, #4
	LSL      r2, r2, #4
	ADD      r1, r1, r2
	LDRB     r2, [r0, #0x10]
	MOV      r4, #0x38
	LSL      r2, r2, #2
	ADD      r1, r1, r2
|loc_080272C0|
	LDR      r1, [r1, #4]
	STR      r1, [r0, #0x54]
	LDRB     r2, [r1, #6]
	LDRSB    r5, [r1, r3]
	LSR      r2, r2, #1
	SUB      r2, r4, r2
	SUB      r2, r2, r5
	STR      r2, [r0, #0x6c]
	LDRB     r2, [r1, #7]
	CMP      r2, #0x20
	BLS      |sub_080272E6|
	MOV      r3, #5
	LDRSB    r1, [r1, r3]
	LSR      r2, r2, #1
	SUB      r2, r4, r2
	SUB      r1, r2, r1
	STR      r1, [r0, #0x70]
	POP      {r4, r5}
	BX       lr
|sub_080272E6|
|unk_080272E6|
		MOV r1, #0x40
		STR r1, [r0, #0x70]
		DCW     0xE7FA
|sub_080272EC|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08027306|
	MOV      r0, #0xff
	ADD      r0, #0x99
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08027306|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
|sub_08027306|
|unk_08027306|
		LDR r0, [r5, #4]
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		LDR r2, [pc, #0x6c]
		BL       |loc_0800EB60|
		LDR r0, [pc, #0x6c]
		MOV r1, #0xff
		STR r0, [r4]
		MOV r0, #0
		ADD r1, #0x95
		STR r0, [r1, r4]
		ADD r0, r4, #0
		BL       |loc_080272AC|
		ADD r0, r4, #0
		DCW     0xE7EB
|sub_0802732C|
	PUSH     {r3, lr}
	BL       |inc_0x0158_0x143f2| + 0xede0
	MOV      r0, #1
|loc_08027334|
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |inc_0x0158_0x143f2| + 0xedb0
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0x81
	LDR      r1, [r0, #0x14]
	ADD      r1, #1
	STR      r1, [r0, #0x14]
	LSL      r0, r1, #0x17
	LDR      r1, [pc, #0x38]
	LSR      r0, r0, #0x1e
	LDRB     r0, [r1, r0]
	STRB     r0, [r4, #0x10]
	ADD      r0, r4, #0
	BL       |loc_080272AC|
	POP      {r4, pc}
	PUSH     {r3, lr}
	CMP      r1, #0
	BNE      |sub_0802736A|
	LDR      r1, [pc, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, pc}
|sub_0802736A|
|unk_0802736A|
		LDR r1, [r0, #0x58]
		LDRB r2, [r1]
		CMP r2, #1
		DCW     0xD9FA
		LDR r1, [r1, #0x58]
		CMP r1, #0
		DCW     0xD0F7
|loc_08027378|
|unk_08027378|
		LDR r1, [pc, #0x10]
	INCBIN  baserom.gba_0x2737a_0x2737c.extracted
|sub_0802737C|
|unk_0802737C|
	INCBIN	baserom.gba_0x2737c_0x27380.extracted
	SUB      r4, r1, r4
	LSL      r0, r0, #0xc
	LDMIA    r6!, {r2, r3, r4, r5, r6}
	LSR      r4, r0, #0x20
	BCC      |loc_08027444|
	LSR      r4, r6, #1
	SUB      r0, r3, r5
	LSL      r0, r0, #0xc
|loc_08027390|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080273AA|
	MOV      r0, #0xff
	ADD      r0, #0x91
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080273AA|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_080273AA|
|unk_080273AA|
		LDR r0, [r5]
		LDR r1, [pc, #0xc4]
		LSL r0, r0, #4
		ADD r0, r0, r1
		LDR r0, [r0, #4]
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		LDR r2, [pc, #0xb8]
		BL       |loc_0800EB60|
		LDR r0, [pc, #0xb8]
		STR r0, [r4]
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0x81
		STR r5, [r0, #0xc]
		LDR r1, [r5, #8]
		LSL r1, r1, #0x18
		LSR r1, r1, #0x18
		STRB r1, [r4, #0x10]
		LDRB r3, [r4, #0x11]
		LDR r2, [r4, #0x50]
		LSL r1, r1, #2
		LSL r3, r3, #4
		ADD r2, r2, r3
		ADD r1, r2, r1
		LDR r1, [r1, #4]
		STR r1, [r4, #0x54]
		LDR r2, [r5, #0xc]
		LDR r3, [r5, #0x10]
		STR r2, [r4, #0x6c]
		STR r3, [r4, #0x70]
		MOV r3, #4
		LDRSB r7, [r1, r3]
		MOV r3, #5
		LDRSB r1, [r1, r3]
		LDR r6, [r5, #0xc]
		ADD r2, r5, #0
		LDR r5, [r5, #0x10]
		ADD r2, #0x14
		ADD r1, r5, r1
		STR r1, [r2, #4]
		ADD r6, r6, r7
		STR r6, [r2]
		LDR r1, [r0, #0xc]
		LDR r3, [r4, #0x54]
		ADD r1, #0x14
		LDRB r2, [r3, #6]
		LDR r5, [r1]
		LDRB r3, [r3, #7]
		ADD r2, r5, r2
		STR r2, [r1, #8]
		LDR r2, [r1, #4]
		ADD r2, r2, r3
		STR r2, [r1, #0xc]
		LDR r0, [r0, #0xc]
		STR r4, [r0, #0x24]
		ADD r0, r4, #0
		DCW     0xE7C1
|sub_08027424|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802743A|
	LDR      r1, [pc, #0x4c]
	STR      r1, [r0]
	MOV      r1, #0
	STRB     r1, [r0, #4]
|loc_0802743A|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xec28
	MOV      r0, #0x28
|loc_08027444|
	STRB     r0, [r4, #8]
	POP      {r4, pc}
|loc_08027448|
	PUSH     {r3, lr}
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0xec4e
	POP      {r3, pc}
|loc_08027454|
	ADD      r0, #0xff
	ADD      r0, #0x81
	LDR      r0, [r0, #0xc]
	LDR      r0, [r0]
	BX       lr
|loc_0802745E|
	ADD      r0, #0xff
	ADD      r0, #0x81
	LDR      r0, [r0, #0xc]
	LDR      r0, [r0, #4]
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [pc, #0xc]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, pc}
	LSL      r0, r0, #0
	BCC      |loc_08027378|
	LSR      r4, r6, #1
	SUB      r4, r1, r4
	LSL      r0, r0, #0xc
	LDMIA    r6!, {r3, r4, r5, r7}
	LSR      r4, r0, #0x20
	ADD      r6, sp, #0xe0
	LSR      r4, r0, #0x20
	ADD      r2, r0, #0
	ADD      r0, r1, #0
	PUSH     {r3, lr}
	LDRB     r1, [r2, #4]
	ADD      r1, #1
	STRB     r1, [r2, #4]
	LSL      r1, r1, #0x1b
	LSR      r1, r1, #0x1d
	LDR      r2, [pc, #0x18]
	LSL      r1, r1, #2
	LDR      r1, [r2, r1]
	LDR      r2, [r0, #0x38]
	CMP      r2, r1
	BEQ      |loc_080274A4|
	BL       |inc_0x0158_0x143f2| + 0xed74
|loc_080274A4|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	LSL      r0, r0, #0
	BCC      |loc_08027574|
	LSR      r4, r6, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080274D0|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080274D0|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_080274D0|
|unk_080274D0|
		ADD r2, r7, #0
		MOV r1, #0x80
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x1b8]
		STR r0, [r4]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		MOV r0, #0
		STR r0, [r4, #0x48]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r0, r6, #1
		ADD r0, r0, r6
		LDR r1, [pc, #0x1a8]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		LSL r0, r0, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		LDR r2, [pc, #0x1a0]
		LSL r0, r6, #3
		LDR r1, [r2, r0]
		ADD r0, r0, r2
		STR r1, [r4, #0x40]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x44]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		DCW     0xE7DB
|sub_08027516|
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x20]
	SUB      sp, #0x18
	ASR      r1, r1, #8
	STR      r1, [sp, #0x10]
	LDR      r1, [r0, #0x24]
	LDR      r4, [pc, #0x178]
	ASR      r1, r1, #8
	STR      r1, [sp, #0x14]
	ADD      r1, r0, #0
	SUB      r4, #8
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0802755E|
	MOV      r2, #0x38
	LSL      r0, r1, #3
	STR      r0, [sp]
	STR      r2, [sp, #8]
	STR      r1, [sp, #4]
	MOV      r3, #4
	MOV      r0, #0
	ADD      r1, sp, #0x10
	LDR      r2, [pc, #0x14c]
	BL       |loc_0802A81C|
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0802755E|
	ADD      sp, #0x18
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x48]
	ADD      r7, r1, #0
	ADD      r0, #1
	SUB      sp, #0x34
	STR      r0, [r4, #0x48]
	LSL      r1, r0, #0x1e
	BNE      |loc_0802758C|
|loc_08027574|
	LSL      r0, r0, #0x1c
	LSR      r0, r0, #0x1e
	BEQ      |sub_080275D6|
	CMP      r0, #1
	BEQ      |loc_080275DE|
	CMP      r0, #2
	BEQ      |loc_080275E6|
	CMP      r0, #3
	BNE      |loc_0802758C|
	LDR      r0, [r4, #0x18]
	SUB      r0, #0x30
	STR      r0, [r4, #0x18]
|loc_0802758C|
	LDR      r1, [r4, #0x20]
	LDR      r2, [r4, #0x40]
	ADD      r1, r1, r2
	STR      r1, [r4, #0x20]
	LDR      r0, [r4, #0x44]
	LDR      r1, [r4, #0x24]
	ADD      r0, r1, r0
	STR      r0, [r4, #0x24]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r6, [pc, #0xf8]
	SUB      r6, #8
	LDR      r0, [r6, #4]
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r2, [r4, #0x30]
	CMP      r1, r2
	BGE      |loc_080275CA|
	LDR      r1, [r4, #0x28]
	LDR      r2, [r0, #8]
	CMP      r1, r2
	BGE      |loc_080275CA|
	LDR      r1, [r0, #4]
	LDR      r2, [r4, #0x34]
	CMP      r1, r2
	BGE      |loc_080275CA|
	LDR      r1, [r4, #0x2c]
	LDR      r0, [r0, #0xc]
	CMP      r1, r0
	BLT      |loc_080275EE|
|loc_080275CA|
	ADD      r1, r4, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
|sub_080275D6|
|unk_080275D6|
		LDR r0, [r4, #0x18]
		SUB r0, #0x30
		STR r0, [r4, #0x18]
		B        |loc_0802758C|
|loc_080275DE|
|unk_080275DE|
		LDR r0, [r4, #0x18]
		ADD r0, #0x30
		STR r0, [r4, #0x18]
		B        |loc_0802758C|
|loc_080275E6|
|unk_080275E6|
		LDR r0, [r4, #0x18]
		ADD r0, #0x30
		STR r0, [r4, #0x18]
		B        |loc_0802758C|
|loc_080275EE|
|unk_080275EE|
		ADD r0, r4, #0
		ADD r0, #0x28
		LDR r1, [r6, #4]
		ADD r5, r0, #0
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_0802760A|
		ADD r0, r4, #0
		BL       |sub_08027516|
		DCW     0xE7E3
|loc_0802760A|
		CMP r7, #0
		DCW     0xD0E1
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		DCW     0xD0DE
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		MOV r7, sp
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x80]
		STR r0, [sp, #0x1c]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x18]
		LDMIA r5!, {r1, r2, r3, r5}
		ADD r0, sp, #4
		STMIA r0!, {r1, r2, r3, r5}
		MOV r0, #0
		ADD r3, sp, #0
		STRB r0, [r3]
		STR r4, [sp, #0x30]
		ADD r2, r7, #0
		MOV r1, #0
		LDR r0, [r6]
		BL       |loc_08011C70|
		CMP r0, #0
		DCW     0xD0C5
		ADD r0, r4, #0
		BL       |sub_08027516|
		DCW     0xE7C1
|sub_0802764E|
	PUSH     {r3, lr}
	CMP      r1, #0
	BNE      |loc_0802768C|
	LDR      r1, [r2, #0x30]
	CMP      r1, r0
	BNE      |sub_0802765E|
	MOV      r0, #0
	POP      {r3, pc}
|sub_0802765E|
|unk_0802765E|
		ADD r1, r2, #4
		LDR r2, [r2, #4]
		LDR r3, [r0, #0x30]
		CMP r2, r3
		BGE      |loc_08027688|
		LDR r2, [r0, #0x28]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_08027688|
		LDR r2, [r1, #4]
		LDR r3, [r0, #0x34]
		CMP r2, r3
		BGE      |loc_08027688|
		LDR r2, [r0, #0x2c]
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BGE      |loc_08027688|
		BL       |sub_08027516|
		MOV r0, #1
		DCW     0xE7E9
|loc_08027688|
		MOV r0, #0
		DCW     0xE7E7
|loc_0802768C|
|unk_0802768C|
; cited by 0x080274DA (a pc-relative load targets 0x08027694)
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		DCW     0xE7E4
	INCBIN  baserom.gba_0x27692_0x2769e.extracted
|sub_0802769E|
	LSR      r4, r6, #1
	CMP      r7, #0xdc
	LSR      r1, r6, #1
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080276C4|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080276C4|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_080276C4|
|unk_080276C4|
		MOV r1, #0xff
		ADD r1, #1
		ADD r2, r7, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x254]
		STR r0, [r4]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		MOV r0, #0
		STR r0, [r4, #0x48]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r0, r6, #1
		ADD r0, r0, r6
		LDR r1, [pc, #0x244]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		LSL r0, r0, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		LDR r2, [pc, #0x23c]
		LSL r0, r6, #3
		LDR r1, [r2, r0]
		ADD r0, r0, r2
		STR r1, [r4, #0x40]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x44]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		DCW     0xE7DA
|sub_0802770C|
	PUSH     {r4, r5, lr}
	LDR      r1, [r0, #0x20]
	SUB      sp, #0x14
	ASR      r1, r1, #8
	STR      r1, [sp, #0xc]
	LDR      r1, [r0, #0x24]
	LDR      r4, [pc, #0x214]
	ASR      r1, r1, #8
	STR      r1, [sp, #0x10]
	ADD      r1, r0, #0
	SUB      r4, #0xc
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r1, #0x45
	LDR      r2, [pc, #0x208]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r5, [pc, #0x204]
	LDR      r0, [r4]
	MOV      r2, #0x40
	MOV      r3, #0
	ADD      r0, r0, r5
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0802776A|
	MOV      r2, #0x38
	LSL      r0, r1, #3
	STR      r0, [sp]
	STR      r2, [sp, #8]
	STR      r1, [sp, #4]
	MOV      r3, #4
	MOV      r0, #0
	ADD      r1, sp, #0xc
	LDR      r2, [pc, #0x1dc]
	BL       |loc_0802A81C|
	ADD      r1, r0, #0
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0802776A|
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x48]
	SUB      sp, #0x34
	ADD      r0, #1
	STR      r0, [r4, #0x48]
	ADD      r6, r4, #0
	ADD      r6, #0x40
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1e
	ADD      r5, r6, #4
	CMP      r0, #0
	BNE      |loc_08027816|
	LDR      r0, [pc, #0x1a4]
	SUB      r0, #0xc
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	CMP      r0, #0x40
	BLT      |loc_08027816|
	LDR      r1, [r6]
	LDR      r2, [r5]
	LSL      r1, r1, #0xb
	LSL      r2, r2, #0xb
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	ADD      r0, r4, #0
	ADD      r0, #0x20
	STR      r1, [sp, #0x14]
	STR      r1, [sp, #0x1c]
	STR      r2, [sp, #0x18]
	STR      r2, [sp, #0x20]
	LDR      r1, [r0]
	LDR      r2, [sp, #0x1c]
	LDR      r3, [r0, #4]
	SUB      r2, r1, r2
	LDR      r7, [sp, #0x20]
	STR      r2, [sp, #0x14]
	STR      r2, [sp, #0x24]
	SUB      r3, r3, r7
	ASR      r2, r2, #8
	STR      r2, [sp, #0x2c]
	STR      r3, [sp, #0x18]
	STR      r3, [sp, #0x28]
	LDR      r2, [r6]
	LDR      r7, [r5]
	LSL      r2, r2, #0xb
	LSL      r3, r7, #0xb
	ASR      r3, r3, #8
	ASR      r2, r2, #8
	STR      r2, [sp, #0x14]
	STR      r2, [sp, #0x1c]
	STR      r3, [sp, #0x18]
	STR      r3, [sp, #0x20]
	ADD      r1, r0, #4
	LDR      r0, [r0]
	LDR      r1, [r1]
	SUB      r0, r0, r2
	SUB      r1, r1, r3
	STR      r0, [sp, #0x14]
	STR      r0, [sp, #0x24]
	ASR      r0, r1, #8
	STR      r1, [sp, #0x28]
	MOV      r2, #0x38
	STR      r2, [sp, #8]
	STR      r0, [sp, #0x30]
	STR      r1, [sp, #0x18]
	MOV      r1, #0x40
	LDR      r0, [pc, #0x148]
	LDR      r2, [pc, #0x130]
	STR      r1, [sp, #4]
	MOV      r3, #3
	STR      r0, [sp]
	ADD      r2, #0x30
	MOV      r0, #0
	ADD      r1, sp, #0x2c
	BL       |loc_0802A81C|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x120]
	SUB      r0, #0xc
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08027816|
	LDR      r0, [r4, #0x20]
	LDR      r1, [r6]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x20]
	LDR      r0, [r4, #0x24]
	LDR      r1, [r5]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x24]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r6, [pc, #0x100]
	SUB      r6, #0xc
	LDR      r0, [r6, #8]
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r2, [r4, #0x30]
	CMP      r1, r2
	BGE      |loc_08027854|
	LDR      r1, [r4, #0x28]
	LDR      r2, [r0, #8]
	CMP      r1, r2
	BGE      |loc_08027854|
	LDR      r1, [r0, #4]
	LDR      r2, [r4, #0x34]
	CMP      r1, r2
	BGE      |loc_08027854|
	LDR      r1, [r4, #0x2c]
	LDR      r0, [r0, #0xc]
	CMP      r1, r0
	BLT      |sub_08027860|
|loc_08027854|
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
|sub_08027860|
|unk_08027860|
		ADD r0, r4, #0
		ADD r0, #0x28
		LDR r1, [r6, #8]
		ADD r5, r0, #0
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_0802787C|
		ADD r0, r4, #0
		BL       |sub_0802770C|
		DCW     0xE7EF
|loc_0802787C|
		LDR r0, [sp, #0x38]
		CMP r0, #0
		DCW     0xD0EC
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		DCW     0xD0E9
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		MOV r7, sp
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0xac]
		STR r0, [sp, #0x1c]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x18]
		LDMIA r5!, {r1, r2, r3, r5}
		ADD r0, sp, #4
		STMIA r0!, {r1, r2, r3, r5}
		MOV r5, #0
		ADD r3, sp, #0
		STRB r5, [r3]
		STR r4, [sp, #0x30]
		ADD r2, r7, #0
		MOV r1, #0
		LDR r0, [r6, #4]
		BL       |loc_08011C70|
		CMP r0, #0
		DCW     0xD0D0
		LDR r6, [r6]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0x68]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDR r0, [pc, #0x68]
		ADD r3, r5, #0
		MOV r2, #0x40
		ADD r0, r6, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
|loc_080278DC|
|unk_080278DC|
	INCBIN	baserom.gba_0x278dc_0x278de.extracted
|sub_080278DE|
|unk_080278DE|
	INCBIN	baserom.gba_0x278de_0x278e2.extracted
	PUSH     {r3, lr}
	CMP      r1, #0
	BNE      |loc_08027920|
	LDR      r1, [r2, #0x30]
	CMP      r1, r0
	BNE      |sub_080278F2|
	MOV      r0, #0
	POP      {r3, pc}
|sub_080278F2|
|unk_080278F2|
		ADD r1, r2, #4
		LDR r2, [r2, #4]
		LDR r3, [r0, #0x30]
		CMP r2, r3
		BGE      |loc_0802791C|
		LDR r2, [r0, #0x28]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_0802791C|
		LDR r2, [r1, #4]
		LDR r3, [r0, #0x34]
		CMP r2, r3
		BGE      |loc_0802791C|
		LDR r2, [r0, #0x2c]
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BGE      |loc_0802791C|
		BL       |sub_0802770C|
		MOV r0, #1
		DCW     0xE7E9
|loc_0802791C|
		MOV r0, #0
		DCW     0xE7E7
|loc_08027920|
|unk_08027920|
; cited by 0x080276D0 (a pc-relative load targets 0x08027928)
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		DCW     0xE7E4
	INCBIN  baserom.gba_0x27926_0x27932.extracted
|sub_08027932|
	LSR      r4, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	CMP      r7, #0xdc
	LSR      r1, r6, #1
	CMP      r2, #0xaa
	LSL      r0, r0, #0
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #0x95
	BL       |inc_0x0158_0x143f2|
	CMP      r0, r7
	BNE      |loc_08027960|
	MOV      r0, #0x92
	BL       |inc_0x0158_0x143f2|
	ADD      r7, r0, #0
|loc_08027960|
	MOV      r4, #0
	LDR      r1, [pc, #0x74]
	LSL      r0, r4, #4
	ADD      r6, r0, r1
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2|
	CMP      r0, r7
	BNE      |loc_08027996|
	CMP      r5, #0
	LDR      r0, [r6, #0xc]
	BEQ      |sub_0802798E|
	CMP      r0, #0
	BLT      |loc_08027996|
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LDR      r6, [pc, #0x58]
	LSL      r0, r0, #2
	ADD      r0, r0, r6
	CMP      r0, r5
	BNE      |loc_08027996|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0802798E|
|unk_0802798E|
		CMP r0, #0
		BGE      |loc_08027996|
		ADD r0, r4, #0
		DCW     0xE7FA
|loc_08027996|
|unk_08027996|
		ADD r4, #1
		CMP r4, #0xe8
		DCW     0xDBE2
		LDR r6, [pc, #0x3c]
		MOV r4, #0
|loc_080279A0|
		LDR r1, [pc, #0x34]
		LSL r0, r4, #4
		ADD r0, r0, r1
		CMP r5, #0
		BEQ      |loc_080279BC|
		LDR r1, [r0, #0xc]
		CMP r1, #0
		BLT      |loc_080279CA|
		LSL r3, r1, #3
		SUB r1, r3, r1
		LSL r1, r1, #2
		ADD r1, r1, r6
		CMP r1, r5
		BNE      |loc_080279CA|
|loc_080279BC|
		LDR r0, [r0, #4]
		BL       |inc_0x0158_0x143f2|
		CMP r0, r7
		BNE      |loc_080279CA|
		ADD r0, r4, #0
		DCW     0xE7E0
|loc_080279CA|
		ADD r4, #1
		CMP r4, #0xe8
		BLT      |loc_080279A0|
		MOV r0, #0
		MVN r0, r0
		DCW     0xE7DA
|sub_080279D6|
	LSL      r0, r0, #0
	BCC      |loc_080278DC|
	LSR      r4, r6, #1
	ASR      r4, r6, #9
	LSR      r1, r6, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080279F8|
	MOV      r0, #0x20
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080279F8|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_080279F8|
|unk_080279F8|
		LDR r0, [pc, #0x13c]
		LDR r6, [pc, #0x140]
		STR r0, [r4]
		MOV r0, #0x40
		STRH r0, [r4, #0xe]
		LDR r0, [r6]
		MOV r1, #0x40
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08027A1E|
		MOV r1, #0x40
		LDR r0, [r6]
		BL       |sub_08011732|
		MOV r1, #0x40
		LDR r0, [r6]
		BL       |loc_0801124C|
|loc_08027A1E|
		LSL r7, r0, #0x10
		LSR r7, r7, #0x10
		LDR r0, [pc, #0x11c]
		STRH r7, [r4, #0xc]
		STR r0, [r4]
		LDR r0, [r5]
		SUB r0, #8
		STR r0, [r4, #0x10]
		LDR r0, [r5, #4]
		SUB r0, #8
		STR r0, [r4, #0x14]
		LDR r0, [r6, #4]
		LDR r1, [r5]
		ADD r6, r0, #0
		LDR r0, [r5, #8]
		ADD r6, #0x94
		SUB r0, r0, r1
		LSL r1, r0, #0x16
		LDR r0, [r6]
		BL       |sub_08046E58|
		STR r0, [r4, #0x18]
		LDR r0, [r5, #0xc]
		LDR r1, [r5, #4]
		SUB r0, r0, r1
		LSL r1, r0, #0x16
		LDR r0, [r6, #4]
		BL       |sub_08046E58|
		STR r0, [r4, #0x1c]
		MOV r0, #0
		STR r0, [r4, #4]
		STRB r0, [r4, #8]
		LDR r1, [pc, #0xe0]
		LSL r0, r7, #5
		ADD r0, r0, r1
		LDR r1, [pc, #0xd4]
		MOV r2, #0x40
		ADD r1, #8
		BL       |sub_08049138|
		ADD r0, r4, #0
		DCW     0xE7C0
|sub_08027A74|
	PUSH     {r4, r5, r6, r7}
	LDR      r2, [pc, #0xc4]
	LDR      r5, [r2, #4]
	LDR      r2, [pc, #0xcc]
	LDR      r4, [r2]
	CMP      r4, #0
	BNE      |sub_08027A88|
	MOV      r0, #0
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_08027A88|
|unk_08027A88|
		LDR r2, [r1]
		ADD r3, r2, #0
		ADD r3, #8
		STR r3, [r1]
		LDR r3, [r1, #4]
		ADD r6, r3, #0
		ADD r6, #0x20
		STR r6, [r1, #4]
		LDR r6, [r1, #8]
		ADD r7, r6, #1
		STR r7, [r1, #8]
		MOV r1, #0x23
		LSL r1, r1, #8
		STR r1, [r2]
		MOV r1, #0xff
		ADD r1, #0xa1
		LDR r1, [r1, r4]
		LDR r7, [r0, #0x18]
		ASR r1, r1, #8
		MUL r1, r7
		LDR r7, [r0, #0x10]
		ASR r1, r1, #0x16
		ADD r7, r1, r7
		MOV r1, #0x23
		LSL r7, r7, #0x17
		LSR r7, r7, #7
		LSL r1, r1, #8
		ORR r1, r7
		STR r1, [r2]
		ADD r4, #0xff
		ADD r4, #0xa5
		LDR r4, [r4]
		LDR r7, [r0, #0x1c]
		ASR r4, r4, #8
		MUL r4, r7
		LDR r7, [r0, #0x14]
		ASR r4, r4, #0x16
		ADD r4, r4, r7
		LSL r4, r4, #0x18
		LSR r1, r1, #8
		LSL r1, r1, #8
		LSR r4, r4, #0x18
		ORR r1, r4
		MOV r4, #0x1f
		LSL r4, r4, #0x19
		BIC r1, r4
		LSL r4, r6, #0x1b
		LSR r4, r4, #2
		ORR r1, r4
		STR r1, [r2]
		LDRH r0, [r0, #0xc]
		LDR r1, [r2, #4]
		LSR r1, r1, #0xa
		LSL r0, r0, #0x16
		LSR r0, r0, #0x16
		LSL r1, r1, #0xa
		ORR r0, r1
		STR r0, [r2, #4]
		LDR r1, [r5, #0x44]
		ASR r1, r1, #2
		STRH r1, [r3, #6]
		LDR r1, [r5, #0x48]
		ASR r1, r1, #2
		STRH r1, [r3, #0x16]
		LDR r1, [r5, #0x4c]
		ASR r1, r1, #2
		STRH r1, [r3, #0xe]
		LDR r0, [r5, #0x50]
		ASR r0, r0, #2
		STRH r0, [r3, #0x1e]
		MOV r0, #0
		DCW     0xE7B5
|sub_08027B18|
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BNE      |sub_08027B34|
	LDRH     r0, [r0, #0xc]
	LDR      r1, [pc, #0x20]
	MOV      r2, #0x40
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LDR      r1, [pc, #0x10]
	ADD      r1, #8
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0
	POP      {r3, pc}
|sub_08027B34|
|unk_08027B34|
; cited by 0x080279F8 (a pc-relative load targets 0x08027B38)
		MOV r0, #0
		DCW     0xE7FC
		DCD     0x08049680
		DCD     0x0874E9F8
		DCD     0x0804D8A0
		DCD     0x06010000
		DCD     0x03001C34
|sub_08027B4C|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	LDR      r5, [r1, #4]
	SUB      sp, #0x10
	ADD      r7, sp, #8
	ADD      r4, r0, #0
	ADD      r1, r5, #0
	ADD      r0, r7, #0
	BL       |inc_0x0158_0x143f2| + 0xfdec
	LDR      r2, [r4, #0x14]
	ADD      r3, r4, #0
	STR      r2, [sp]
	ADD      r2, r4, #0
	ADD      r3, #8
	ADD      r6, r3, #0
	ADD      r2, #0x10
	ADD      r0, r7, #0
	LDR      r1, [sp, #0x18]
	BL       |inc_0x153f2_0x1a3f2| + 0x3edc
	MOV      r1, #3
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0xa8]
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [r4, #8]
	ADD      r2, r0, #0
	CMP      r0, #0
	BGE      |loc_08027B8E|
|unk_08027B8C|
	INCBIN	baserom.gba_0x27b8c_0x27b8e.extracted
|loc_08027B8E|
	LDR      r1, [r4, #0xc]
	ADD      r3, r1, #0
	CMP      r1, #0
	BGE      |loc_08027B98|
|unk_08027B96|
	INCBIN	baserom.gba_0x27b96_0x27b98.extracted
|loc_08027B98|
	CMP      r0, r1
	BLE      |loc_08027BA8|
	MOV      r3, #3
	CMP      r2, #0
	BGT      |loc_08027BA4|
	MOV      r3, #2
|loc_08027BA4|
	ADD      r0, r3, #0
	B        |loc_08027BB0|
|loc_08027BA8|
	MOV      r0, #1
	CMP      r3, #0
	BLE      |loc_08027BB0|
	MOV      r0, #0
|loc_08027BB0|
	ADD      r3, r0, #0
	ADD      r2, r6, #0
	ADD      r1, r7, #0
	MOV      r0, #0
	BL       |loc_08027CBC|
	ADD      r1, r0, #0
	STR      r0, [r4, #0x18]
	LDR      r0, [pc, #0x68]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|sub_08027BCC|
|unk_08027BCC|
		BX       lr
|sub_08027BCE|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x10]
	SUB      r1, #1
	STR      r1, [r0, #0x10]
	BNE      |sub_08027BE2|
	LDR      r0, [r0, #0x18]
	BL       |sub_08027D3E|
	MOV      r0, #1
	POP      {r3, pc}
|sub_08027BE2|
|unk_08027BE2|
		MOV r0, #0
		DCW     0xE7FC
|sub_08027BE6|
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	LDR      r1, [r0, #0x1c]
	SUB      sp, #0x24
	ADD      r0, sp, #0xc
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x14]
	LDR      r3, [sp, #0x18]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x10]
	STR      r1, [sp, #4]
	ADD      r0, r0, r3
	STR      r0, [sp, #8]
	ASR      r1, r1, #1
	ASR      r0, r0, #1
	STR      r1, [sp, #4]
	STR      r1, [sp, #0x1c]
	ADD      r1, r5, #0
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x20]
	ADD      r0, r4, #0
	ADD      r2, sp, #0x1c
	BL       |sub_08027B4C|
	ADD      sp, #0x24
	POP      {r4, r5, pc}
|sub_08027C20|
|unk_08027C20|
		ADD r2, r0, #0
		ADD r2, #0x1c
		B        |sub_08027B4C|
|sub_08027C26|
	LSL      r0, r0, #0
	SUB      r0, r2, r4
	LSL      r0, r0, #0xc
	DCW      0xea40,0x0874
	PUSH     {r4, r5, lr}
	SUB      sp, #0x2c
	ADD      r4, r0, #0
	ADD      r0, sp, #0x1c
	LDR      r1, [r1, #4]
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r5, [pc, #0x78]
	MOV      r1, #1
	LSL      r1, r1, #0xa
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x115da
	LDR      r0, [sp, #0x1c]
	LDR      r1, [sp, #0x24]
	LDR      r2, [sp, #0x28]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x20]
	STR      r1, [sp, #4]
	ADD      r0, r0, r2
	STR      r0, [sp, #8]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x10]
	ADD      r0, r1, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	LDR      r1, [r4, #8]
	ADD      r0, r0, r1
	LDR      r1, [sp, #0x10]
	LDR      r2, [r4, #0xc]
	STR      r0, [sp, #4]
	ADD      r1, r1, r2
	STR      r1, [sp, #8]
	STR      r1, [sp, #0x18]
	MOV      r2, #0x37
	STR      r0, [sp, #0x14]
	MOV      r0, #0
	ADD      r1, sp, #0x14
	BL       |inc_0x153f2_0x1a3f2| + 0x413a
	ADD      r1, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x2c
	POP      {r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r4, [pc, #0x20]
	MOV      r1, #1
	LSL      r1, r1, #0xa
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x115da
	ADD      r1, r5, #0
	ADD      r1, #8
	MOV      r2, #0x37
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x413a
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	DCW      0xea44,0x0874
|loc_08027CBC|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08027CD8|
	MOV      r0, #0x54
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08027CD8|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08027CD8|
|unk_08027CD8|
		MOV r1, #0xff
		ADD r1, #1
		MOV r2, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0xb0]
		STR r0, [r4]
		LDMIA r6!, {r1, r2}
		STR r1, [r4, #0x40]
		STR r2, [r4, #0x44]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r0, r7, #1
		ADD r0, r0, r7
		LDR r1, [pc, #0xa0]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		LSL r0, r0, #4
		MOV r5, #0
		STR r5, [r4, #0x50]
		ADD r0, r0, r1
		STR r0, [r4, #0x48]
		STR r5, [r4, #0x4c]
		STR r0, [r4, #0x18]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [pc, #0x84]
		LDR r6, [r0]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x14
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0x78]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDR r0, [pc, #0x78]
		ADD r3, r5, #0
		MOV r2, #0x40
		ADD r0, r6, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		DCW     0xE7CB
|sub_08027D3E|
	MOV      r1, #0x10
	STR      r1, [r0, #0x4c]
	LDR      r1, [pc, #0x68]
	STR      r1, [r0, #0x18]
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x4c]
	CMP      r1, #0
	BEQ      |sub_08027D62|
	SUB      r1, #1
	STR      r1, [r0, #0x4c]
	BNE      |loc_08027D60|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x44]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08027D60|
	POP      {r3, pc}
|sub_08027D62|
|unk_08027D62|
		LDR r2, [r0, #0x20]
		LDR r3, [r0, #0x40]
		ADD r2, r2, r3
		STR r2, [r0, #0x20]
		LDR r1, [r0, #0x44]
		LDR r2, [r0, #0x24]
		ADD r1, r2, r1
		STR r1, [r0, #0x24]
		LDR r1, [r0, #0x50]
		ADD r1, #1
		ASR r2, r1, #3
		CMP r2, #3
		STR r1, [r0, #0x50]
		BLE      |loc_08027D84|
		LSL r2, r2, #0x1f
		LSR r2, r2, #0x1f
		ADD r2, #2
|loc_08027D84|
		LSL r3, r2, #1
		ADD r2, r3, r2
		LDR r1, [r0, #0x48]
		LSL r2, r2, #2
		ADD r1, r1, r2
		STR r1, [r0, #0x18]
	INCBIN  baserom.gba_0x27d90_0x27d92.extracted
|sub_08027D92|
|unk_08027D92|
	INCBIN	baserom.gba_0x27d92_0x27d96.extracted
	LSL      r0, r0, #0
	BCS      |loc_08027E04|
	LSR      r4, r0, #0x20
	ADD      r7, #0xc
	LSR      r1, r6, #1
	DCW      0xea48,0x0874
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r7, #0xcc
	LSR      r1, r6, #1
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_08027DC8|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08027DC8|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08027DC8|
	LDR      r0, [pc, #0x74]
	LDR      r5, [pc, #0x78]
	MOV      r1, #5
	STR      r0, [r4]
	LDR      r0, [r5]
	LSL      r1, r1, #0xb
	BL       |inc_0x0158_0x143f2| + 0x115da
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |loc_08028144|
	ADD      r1, r0, #0
	STR      r0, [r4, #4]
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|sub_08027DEE|
|unk_08027DEE|
		BX       lr
|sub_08027DF0|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x50]
	LDR      r1, [r0, #4]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x11d3c
|loc_08027E04|
	ADD      r0, r4, #0
	BEQ      |loc_08027E14|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08027E14|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [pc, #0x1c]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11458
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x10]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11426
	LDR      r0, [r4, #4]
	LDR      r0, [r0, #0x10]
	POP      {r4, pc}
|sub_08027E40|
|unk_08027E40|
	INCBIN	baserom.gba_0x27e40_0x27e42.extracted
|sub_08027E42|
	LSR      r4, r0, #0x20
	DCW      0xea50,0x0874
|loc_08027E48|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRH     r0, [r0, #0xc]
	SUB      sp, #0x14
	LDR      r1, [pc, #0x2b8]
	LSL      r0, r0, #5
	ADD      r1, r0, r1
	MOV      r7, #0
	MOV      r6, #0x40
	ADD      r0, r4, #0
	ADD      r0, #0x34
	ADD      r5, r0, #0
	STR      r6, [sp, #0xc]
	STR      r6, [sp, #0x10]
	STR      r7, [sp, #4]
	STR      r7, [sp, #8]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x298]
	STR      r6, [sp, #4]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSL      r1, r6, #6
	ADD      r1, r0, r1
	MOV      r0, #0x80
	STR      r0, [sp, #0xc]
	ADD      r0, r5, #0
	STR      r7, [sp, #8]
	STR      r6, [sp, #0x10]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x27c]
	STR      r7, [sp, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSL      r1, r6, #7
	ADD      r1, r0, r1
	MOV      r0, #0x80
	STR      r0, [sp, #4]
	MOV      r0, #0xa0
	STR      r0, [sp, #0xc]
	ADD      r0, r5, #0
	STR      r6, [sp, #0x10]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	SUB      r0, #1
	STR      r0, [r4, #0x14]
	BNE      |loc_08027ED2|
	ADD      r0, r4, #0
	ADD      r0, #0x29
	MOV      r2, #5
	ADD      r5, r0, #0
	LDR      r1, [pc, #0x248]
	BL       |inc_0x046118_0x049114| + 0xb3c
	MOV      r6, #2
	CMP      r0, #0
	BNE      |loc_08027ED4|
	STR      r6, [r4, #0x10]
|loc_08027ED2|
	POP      {r4, r5, r6, pc}
|loc_08027ED4|
	ADD      r1, r4, #0
	ADD      r1, #0x24
	MOV      r2, #5
	ADD      r0, r5, #0
	BL       |inc_0x046118_0x049114| + 0xb3c
	CMP      r0, #0
	BNE      |loc_08027EE8|
	STR      r6, [r4, #0x10]
	POP      {r4, r5, r6, pc}
|loc_08027EE8|
	MOV      r0, #1
	STR      r0, [r4, #0x10]
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x18]
	SUB      sp, #0x14
	ADD      r0, #1
	STR      r0, [r4, #0x18]
	CMP      r0, #0x20
	BLT      |loc_08027F02|
	LDR      r1, [pc, #0x214]
	STR      r1, [r4, #0x30]
|loc_08027F02|
	LSL      r1, r0, #0x1d
	BNE      |loc_08027F68|
	LSL      r0, r0, #0x1c
	BPL      |sub_08027F6C|
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x1fc]
	MOV      r7, #0
	LSL      r0, r0, #5
	ADD      r1, r0, r1
	MOV      r6, #0x40
	ADD      r0, r4, #0
	ADD      r0, #0x68
	ADD      r5, r0, #0
	STR      r6, [sp, #0xc]
	STR      r6, [sp, #0x10]
	STR      r7, [sp, #4]
	STR      r7, [sp, #8]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x1dc]
	STR      r6, [sp, #4]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSL      r1, r6, #6
	ADD      r1, r0, r1
	MOV      r0, #0x80
	STR      r0, [sp, #0xc]
	ADD      r0, r5, #0
	STR      r7, [sp, #8]
	STR      r6, [sp, #0x10]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x1c0]
	STR      r7, [sp, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSL      r1, r6, #7
	ADD      r1, r0, r1
	MOV      r0, #0x80
	STR      r0, [sp, #4]
	MOV      r0, #0xa0
	STR      r0, [sp, #0xc]
	ADD      r0, r5, #0
	STR      r6, [sp, #0x10]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
|loc_08027F68|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_08027F6C|
|unk_08027F6C|
		ADD r0, r4, #0
		BL       |loc_08027E48|
		B        |loc_08027F68|
|sub_08027F74|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x18]
	ADD      r0, #1
	STR      r0, [r4, #0x18]
	CMP      r0, #0x10
	BLT      |loc_08027FB6|
	MOV      r1, #0x8c
	LDR      r2, [pc, #0x190]
	LDR      r1, [r1, r4]
	LDR      r0, [r4, #0x58]
	LDR      r2, [r2, #4]
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0x50
	STR      r0, [r4, #0x38]
	MOV      r0, #0x1c
	STR      r0, [r4, #0x3c]
	MOV      r0, #0x4b
	LDR      r1, [pc, #0x180]
	LSL      r0, r0, #3
	LDR      r1, [r1, r0]
	ADD      r0, r4, #0
	ADD      r0, #0x34
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r0, r4, #0
	BL       |loc_08027E48|
	LDR      r0, [pc, #0x170]
	STR      r0, [r4, #0x30]
	MOV      r0, #0
	STR      r0, [r4, #0x18]
|loc_08027FB6|
	POP      {r4, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x150]
	MOV      r2, #0xf3
	SUB      r0, #0xc
	LDR      r1, [r0]
	SUB      sp, #0x110
	LDRH     r1, [r1, #4]
	AND      r1, r2
	BEQ      |loc_08028030|
	LDR      r1, [r4, #0x18]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, #0x14
	STR      r1, [sp]
	MOV      r1, #0x2c
	STR      r1, [sp, #4]
	LDR      r1, [sp]
	ADD      r1, #0x10
	STR      r1, [sp, #8]
	MOV      r1, #0x3c
	STR      r1, [sp, #0xc]
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x2b9e
	CMP      r0, #2
	BLT      |loc_08027FF2|
	SUB      r0, #2
|loc_08027FF2|
	LDR      r1, [r4, #0x18]
	MOV      r6, #0
	ADD      r2, r1, #1
	ADD      r1, r1, r4
	ADD      r1, #0x20
	STR      r2, [r4, #0x18]
	STRB     r0, [r1, #9]
	LDR      r1, [pc, #0x10c]
	LSL      r0, r0, #2
	ADD      r1, #8
	LDR      r0, [r1, r0]
	ADD      r5, sp, #0x10
	LDR      r1, [r0, #4]
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	ADD      r0, #0x34
	MOV      r2, sp
	BL       |inc_0x03d784_0x041118| + 0x219e
	ADD      r0, r4, #0
	BL       |loc_08027E48|
	LDR      r0, [r4, #0x18]
	CMP      r0, #5
	BNE      |loc_08028030|
	LDR      r0, [pc, #0xf8]
	STR      r0, [r4, #0x30]
	STR      r6, [r4, #0x18]
|loc_08028030|
	ADD      sp, #0x110
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x1c]
	SUB      sp, #0x114
	SUB      r0, #1
	STR      r0, [r4, #0x1c]
	BNE      |loc_0802807E|
	ADD      r5, r4, #0
	LDR      r0, [r4, #0x18]
	ADD      r5, #0x34
	MOV      r6, #0
	CMP      r0, #0xa
	BLT      |sub_08028082|
	MOV      r1, #0x8c
	LDR      r2, [pc, #0xc4]
	LDR      r1, [r1, r4]
	LDR      r0, [r4, #0x58]
	LDR      r2, [r2, #4]
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0x50
	STR      r0, [r4, #0x38]
	MOV      r0, #0x1c
	STR      r0, [r4, #0x3c]
	MOV      r0, #0x95
	LDR      r1, [pc, #0xb4]
	LSL      r0, r0, #2
	LDR      r1, [r1, r0]
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r0, r4, #0
	BL       |loc_08027E48|
	LDR      r0, [pc, #0xac]
	STR      r0, [r4, #0x30]
	STR      r6, [r4, #0x18]
|loc_0802807E|
	ADD      sp, #0x114
	POP      {r4, r5, r6, r7, pc}
|sub_08028082|
|unk_08028082|
		MOV r6, #0x2c
		CMP r0, #5
		LDR r0, [r4, #0x18]
		BLT      |loc_080280C0|
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		SUB r0, #0x64
		STR r0, [sp, #0x104]
		ADD r0, #0x10
		STR r0, [sp, #0x10c]
		MOV r0, #0x3c
		STR r0, [sp, #0x110]
		ADD r0, r4, #0
		ADD r0, #0x68
		STR r6, [sp, #0x108]
		LDR r1, [r0, #0x28]
		LDR r0, [r0, #0x24]
		MUL r1, r6
		ADD r0, r1, r0
		LDR r1, [sp, #0x104]
		MOV r3, #0xa0
		ADD r1, r0, r1
		ADD r0, r5, #0
		ADD r2, sp, #0x104
		BL       |inc_0x03d784_0x041118| + 0x215e
		ADD r0, r4, #0
		BL       |loc_08027E48|
		B        |loc_080280FE|
|loc_080280C0|
		ADD r0, r0, r4
		ADD r0, #0x20
		LDRB r0, [r0, #4]
		LDR r1, [pc, #0x48]
		ADD r7, sp, #0x14
		ADD r1, #8
		LSL r0, r0, #2
		LDR r0, [r1, r0]
		LDR r1, [r0, #4]
		ADD r0, r7, #0
		BL       |inc_0x049120_0x055620|
		LDR r0, [r4, #0x18]
		ADD r1, r7, #0
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, #0x14
		STR r0, [sp, #4]
		ADD r0, #0x10
		STR r0, [sp, #0xc]
		MOV r0, #0x3c
		STR r0, [sp, #0x10]
		ADD r0, r5, #0
		STR r6, [sp, #8]
		ADD r2, sp, #4
		BL       |inc_0x03d784_0x041118| + 0x219e
		ADD r0, r4, #0
		BL       |loc_08027E48|
|loc_080280FE|
		LDR r0, [r4, #0x18]
		ADD r0, #1
		STR r0, [r4, #0x18]
		LDR r0, [r4, #0x20]
		STR r0, [r4, #0x1c]
		B        |loc_0802807E|
|sub_0802810A|
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	DCW      0xea60,0x0874
	LDRB     r1, [r6, #0x1a]
	LSR      r2, r0, #0x20
	ASR      r0, r3, #0x1d
	LSR      r7, r0, #0x20
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	LDRB     r7, [r5, #0x1b]
	LSR      r2, r0, #0x20
	LDRB     r5, [r6, #0x1d]
	LSR      r2, r0, #0x20
	LDRB     r1, [r7, #0x1e]
	LSR      r2, r0, #0x20
	LDR      r1, [r0, #0x14]
	ADD      r1, #1
	STR      r1, [r0, #0x14]
	CMP      r1, #8
	BLT      |loc_08028142|
	LDR      r1, [pc, #0x230]
	STR      r1, [r0, #0x30]
	MOV      r1, #0
	STR      r1, [r0, #0x18]
	MOV      r1, #1
	STR      r1, [r0, #0x1c]
|loc_08028142|
	BX       lr
|loc_08028144|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0802815C|
	MOV      r0, #0x9c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802815C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0802815C|
|unk_0802815C|
		LDR r0, [pc, #0x20c]
		MOV r5, #5
		LSL r5, r5, #0xb
		LDR r6, [pc, #0x20c]
		STR r0, [r4]
		STRH r5, [r4, #0xe]
		LDR r0, [r6, #4]
		ADD r1, r5, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08028184|
		ADD r1, r5, #0
		LDR r0, [r6, #4]
		BL       |sub_08011732|
		ADD r1, r5, #0
		LDR r0, [r6, #4]
		BL       |loc_0801124C|
|loc_08028184|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x1ec]
		MOV r2, #0x40
		STR r0, [r4]
		ADD r0, r4, #0
		ADD r0, #0x34
		MOV r1, #0xa0
		ADD r5, r0, #0
		BL       |loc_0803F540|
		MOV r2, #0x40
		MOV r1, #0xa0
		ADD r0, r4, #0
		ADD r0, #0x68
		BL       |loc_0803F540|
		MOV r1, #8
		SUB r1, r1, r7
		MOV r0, #0
		STR r0, [r4, #0x10]
		STRB r0, [r4, #8]
		LSL r3, r1, #1
		ADD r1, r3, r1
		STR r0, [r4, #4]
		STR r1, [r4, #0x20]
		STR r0, [r4, #0x14]
		LDR r0, [pc, #0x1bc]
		ADD r7, r4, #0
		STR r0, [r4, #0x30]
		ADD r7, #0x80
		LDR r1, [r7, #0xc]
		LDR r0, [pc, #0x1b8]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LDR r2, [pc, #0x1b0]
		LDR r0, [r4, #0x58]
		LDR r1, [r7, #0xc]
		LDR r2, [r2, #4]
		BL       |sub_08049138|
		ADD r0, r4, #0
		BL       |loc_08027E48|
		MOV r7, #0
|loc_080281DC|
		MOV r0, #6
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r1, r4, r7
		ADD r1, #0x20
		ADD r7, #1
		CMP r7, #5
		STRB r0, [r1, #4]
		BLT      |loc_080281DC|
		MOV r0, #2
		STRB r0, [r5, #3]
		LDR r0, [pc, #0x18c]
		MOV r1, #1
		STRB r1, [r5, #2]
		STR r0, [r5, #0x20]
		STRB r1, [r5]
		LDR r0, [r6, #8]
		LDR r1, [pc, #0x184]
		STR r0, [r4, #0x40]
		MOV r0, #0x50
		STR r0, [r4, #0x38]
		MOV r0, #0x1c
		STR r0, [r4, #0x3c]
		MOV r0, #0x25
		LSL r0, r0, #4
		LDR r1, [r1, r0]
		ADD r0, r5, #0
		BL       |loc_0803DADA|
		ADD r0, r4, #0
		DCW     0xE79F
|sub_0802821A|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x30]
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	ADD      r6, r1, #0
	CMP      r0, #0
	SUB      sp, #0x14
	BNE      |sub_08028236|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_08028236|
|unk_08028236|
; cited by 0x08028136 (a pc-relative load targets 0x08028368)
		LDR r0, [r6, #4]
		LDR r5, [r6]
		ADD r7, r0, #0
		ADD r0, #0x20
		STR r0, [r6, #4]
		LDR r0, [r6, #8]
		MOV r1, #1
		ADD r2, r0, #0
		ADD r0, #1
		STR r0, [r6, #8]
		STR r2, [sp, #4]
		LDR r0, [r4, #0x14]
		LSL r1, r1, #0xb
		STR r0, [sp, #0x10]
		BL       |sub_08046E58|
		MOV ip, r0
		LDR r0, [sp, #0x10]
		LDR r2, [pc, #0x12c]
		SUB r0, #8
		MOV lr, r0
		LSL r3, r0, #4
		STR r2, [r5]
		LDR r1, [r4, #0x14]
		SUB r0, r3, r0
		LSL r3, r1, #2
		ADD r1, r3, r1
		MOV r3, lr
		LSL r2, r3, #5
		LSL r1, r1, #3
		ADD r1, r1, r2
		LSL r0, r0, #3
		SUB r1, r1, r0
		STR r2, [sp, #0xc]
		ASR r2, r1, #0x1f
		LSR r2, r2, #0x1d
		ADD r1, r2, r1
		ASR r1, r1, #3
		LSL r1, r1, #0x17
		LDR r2, [pc, #0x100]
		LSR r1, r1, #7
		ORR r1, r2
		LSR r1, r1, #8
		LSL r1, r1, #8
		ADD r1, #0x30
		STR r1, [r5]
		LDRH r2, [r4, #0xc]
		ADD r3, r1, #0
		LDR r1, [r5, #4]
		LSL r2, r2, #0x16
		LSR r1, r1, #0xa
		LSL r1, r1, #0xa
		LSR r2, r2, #0x16
		ORR r1, r2
		MOV r2, #0x1f
		LSL r2, r2, #0x19
		BIC r3, r2
		STR r1, [r5, #4]
		LDR r2, [sp, #4]
		ADD r1, r3, #0
		LSL r2, r2, #0x1b
		LSR r2, r2, #2
		STR r2, [sp, #8]
		ORR r1, r2
		LDR r2, [pc, #0xd0]
		STR r1, [r5]
		STR r2, [r5, #8]
		LDR r2, [r4, #0x14]
		MOV r3, #0x68
		MUL r2, r3
		LDR r3, [sp, #0xc]
		ADD r1, r5, #0
		ADD r2, r2, r3
		SUB r2, r2, r0
		ASR r3, r2, #0x1f
		LSR r3, r3, #0x1d
		ADD r2, r3, r2
		ASR r2, r2, #3
		LSL r2, r2, #0x17
		LDR r3, [pc, #0xb0]
		LSR r2, r2, #7
		ORR r2, r3
		LSR r2, r2, #8
		LSL r2, r2, #8
		ADD r2, #0x30
		ADD r1, #8
		STR r2, [r1]
		ADD r5, r2, #0
		LDRH r2, [r4, #0xc]
		LDR r3, [r1, #4]
		ADD r2, #0x80
		LSL r2, r2, #0x16
		LSR r3, r3, #0xa
		LSL r3, r3, #0xa
		LSR r2, r2, #0x16
		ORR r2, r3
		STR r2, [r1, #4]
		ADD r2, r5, #0
		MOV r5, #0x1f
		LSL r5, r5, #0x19
		BIC r2, r5
		ADD r3, r2, #0
		LDR r2, [sp, #8]
		LDR r5, [pc, #0x84]
		ORR r2, r3
		STR r2, [r1]
		ADD r1, #8
		STR r5, [r1]
		LDR r2, [r4, #0x14]
		MOV r3, #0xa8
		MUL r2, r3
		MOV r3, lr
		LSL r3, r3, #4
		ADD r2, r2, r3
		SUB r0, r2, r0
		ASR r2, r0, #0x1f
		LSR r2, r2, #0x1d
		ADD r0, r2, r0
		ASR r0, r0, #3
		LSL r0, r0, #0x17
		LSR r0, r0, #7
		ORR r0, r5
		LSR r0, r0, #8
		LSL r0, r0, #8
		ADD r0, #0x30
		STR r0, [r1]
		LDRH r2, [r4, #0xc]
		LDR r3, [r1, #4]
		ADD r2, #0xff
		ADD r2, #1
		LSL r2, r2, #0x16
		LSR r3, r3, #0xa
		LSL r3, r3, #0xa
		LSR r2, r2, #0x16
		ORR r2, r3
		STR r2, [r1, #4]
		MOV r2, #0x1f
		LSL r2, r2, #0x19
		BIC r0, r2
		LDR r2, [sp, #8]
		ORR r0, r2
		STR r0, [r1]
		MOV r0, ip
		STRH r0, [r7, #6]
		MOV r2, #0
		STRH r2, [r7, #0xe]
		STRH r2, [r7, #0x16]
		STRH r0, [r7, #0x1e]
		ADD r1, #8
		STR r1, [r6]
		MOV r0, #0
		DCW     0xE765
	DCB	0x00,0x00
	DCD	0x08028035
	DCD	0x08049680
	DCD	0x0874EA54
	DCD	0x0804C9C8
	DCD	0x0802812D
	DCD	0x08071758
	DCD	0x0803F70D
	DCD	0x0806BCE8
		DCD     0xC0002100
		DCD     0xC000A100
|sub_08028390|
	PUSH     {r4, r5, r6, lr}
	LDR      r6, [pc, #0x324]
	ADD      r4, r1, #0
	LDR      r0, [r6]
	CMP      r0, #0
	BNE      |loc_080283D6|
	LDR      r0, [pc, #0x31c]
	MOV      r3, #0x68
	LDR      r0, [r0, #4]
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x30c]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080283D4|
	POP      {r4, r5, r6, pc}
|loc_080283D6|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	MOV      r1, #0xf0
	AND      r0, r1
	BEQ      |loc_08028400|
	LDR      r1, [pc, #0x2d4]
	MOV      r2, #0x11
	LSL      r2, r2, #5
	ADD      r2, r4, r2
	LDR      r1, [r1, #4]
	STRH     r0, [r2, #0x10]
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	STR      r1, [r0, #0x34]
|loc_08028400|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #2]
	MOV      r5, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1c
	BEQ      |loc_0802849E|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1f
	BEQ      |loc_08028432|
	MOV      r0, #2
	STRB     r0, [r4, #0x10]
|loc_08028432|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1b
	LSR      r0, r0, #0x1f
	BEQ      |loc_0802844C|
	MOV      r0, #3
	STRB     r0, [r4, #0x10]
|loc_0802844C|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x19
	LSR      r0, r0, #0x1f
	BEQ      |loc_08028464|
	STRB     r5, [r4, #0x10]
|loc_08028464|
	LDR      r1, [r4]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1f
	BEQ      |loc_0802847E|
	MOV      r0, #0
	STRB     r0, [r4, #0x10]
|loc_0802847E|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802848C|
	LDR      r1, [pc, #0x23c]
	STR      r1, [r0]
|loc_0802848C|
	ADD      r5, r0, #0
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
|loc_0802849E|
	LDR      r0, [r6]
	CMP      r0, #0
	BLE      |loc_080283D4|
	SUB      r0, #1
	STR      r0, [r6]
	POP      {r4, r5, r6, pc}
	LDRH     r0, [r1, #0x12]
	LDR      r2, [pc, #0x21c]
	ADD      r1, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x16
	LDR      r0, [r2, r0]
|unk_080284B6|
	INCBIN	baserom.gba_0x284b6_0x284b8.extracted
	ASR      r0, r0, #0xd
	ADD      r1, #0x61
	STRH     r0, [r1, #0x16]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDRH     r0, [r1, #0x12]
	ADD      r7, r1, #0
	MOV      r2, #0x47
	LSL      r2, r2, #3
	ADD      r7, #0xff
	ADD      r7, #0xa1
	ADD      r6, r1, r2
	ADD      r4, r1, #0
	CMP      r0, #0
	SUB      sp, #0xc
	BNE      |loc_080285B6|
	LDR      r0, [pc, #0x1dc]
	LDR      r0, [r0]
	CMP      r0, #0
	BNE      |sub_0802851E|
	LDR      r0, [pc, #0x1d8]
	MOV      r3, #0x68
	LDR      r0, [r0, #4]
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x1c8]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_0802851E|
|unk_0802851E|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		STR r0, [sp, #8]
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1c
		DCW     0xD053
		MOV r0, #0
		STR r0, [r5, #4]
		LDR r0, [sp, #8]
		LDRH r0, [r0, #2]
		LSL r1, r0, #0x1a
		LSR r1, r1, #0x1f
		BEQ      |loc_08028566|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #4]
		ADD r0, r1, #0
		STR r1, [sp]
		LDR r1, [r6]
		MOV r2, #2
		SUB r0, r0, r1
		STR r0, [sp]
		ADD r0, r4, #0
		MOV r1, sp
		BL       |inc_0x0158_0x143f2| + 0x12808
		LDR r0, [r5, #4]
		ADD r0, #1
		STR r0, [r5, #4]
		B        |loc_0802858C|
|loc_08028566|
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BEQ      |loc_0802858C|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #4]
		ADD r0, r1, #0
		STR r1, [sp]
		LDR r1, [r6]
		MOV r2, #2
		ADD r0, r0, r1
		STR r0, [sp]
		ADD r0, r4, #0
		MOV r1, sp
		BL       |inc_0x0158_0x143f2| + 0x12808
		LDR r0, [r5, #4]
		ADD r0, #2
		STR r0, [r5, #4]
|loc_0802858C|
		LDR r0, [sp, #8]
		LDRH r0, [r0, #2]
		LSL r1, r0, #0x19
		LSR r1, r1, #0x1f
		DCW     0xD010
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #4]
		STR r1, [sp]
		LDR r2, [r6]
		MOV r1, sp
		SUB r0, r0, r2
		STR r0, [sp, #4]
		MOV r2, #1
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x12808
		LDR r0, [r5, #4]
		ADD r0, #3
		STR r0, [r5, #4]
		B        |loc_0802869C|
|loc_080285B6|
|unk_080285B6|
; cited by 0x08028392 (a pc-relative load targets 0x080286B8)
		B        |loc_08028600|
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1f
		BEQ      |loc_0802869C|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #4]
		STR r1, [sp]
		LDR r2, [r6]
		MOV r1, sp
		ADD r0, r0, r2
		STR r0, [sp, #4]
		MOV r2, #1
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x12808
		LDR r0, [r5, #4]
		ADD r0, #6
		STR r0, [r5, #4]
		B        |loc_0802869C|
		MOV r0, #4
		DCD     0xFFEAF014
		CMP r0, #0
		BEQ      |loc_080285EC|
		LDR r1, [pc, #0xe4]
		STR r1, [r0]
|loc_080285EC|
		ADD r5, r0, #0
		MOV r1, #0
		ADD r0, r4, #0
		BL       |loc_0800ECDA|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800ED18|
		B        |loc_0802869C|
|loc_08028600|
		LDR r0, [r5, #4]
		CMP r0, #1
		BEQ      |loc_0802860E|
		CMP r0, #4
		BEQ      |loc_0802860E|
		CMP r0, #7
		BNE      |loc_08028628|
|loc_0802860E|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [r6]
		MOV r2, #2
		SUB r0, r0, r1
		STR r0, [sp, #4]
		ADD r0, r4, #0
		ADD r1, sp, #4
		BL       |inc_0x0158_0x143f2| + 0x12808
|loc_08028628|
		LDR r0, [r5, #4]
		CMP r0, #2
		BEQ      |loc_08028636|
		CMP r0, #5
		BEQ      |loc_08028636|
		CMP r0, #8
		BNE      |loc_08028650|
|loc_08028636|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [r6]
		MOV r2, #2
		ADD r0, r0, r1
		STR r0, [sp, #4]
		ADD r0, r4, #0
		ADD r1, sp, #4
		BL       |inc_0x0158_0x143f2| + 0x12808
|loc_08028650|
		LDR r0, [r5, #4]
		CMP r0, #3
		BEQ      |loc_0802865E|
		CMP r0, #4
		BEQ      |loc_0802865E|
		CMP r0, #5
		BNE      |loc_08028676|
|loc_0802865E|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #8]
		STR r1, [sp, #4]
		LDR r2, [r6]
		ADD r1, sp, #4
		SUB r0, r0, r2
		STR r0, [sp, #8]
		MOV r2, #1
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x12808
|loc_08028676|
		LDR r0, [r5, #4]
		CMP r0, #6
		BEQ      |loc_08028684|
		CMP r0, #7
		BEQ      |loc_08028684|
		CMP r0, #8
		BNE      |loc_0802869C|
|loc_08028684|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #8]
		STR r1, [sp, #4]
		LDR r2, [r6]
		ADD r1, sp, #4
		ADD r0, r0, r2
		STR r0, [sp, #8]
		MOV r2, #1
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x12808
|loc_0802869C|
		LDRH r0, [r4, #0x12]
		LDR r1, [pc, #0x18]
		ADD r0, #8
		LSL r0, r0, #0x19
		LSR r0, r0, #0x19
		STRH r0, [r4, #0x12]
		LDR r0, [r1]
		CMP r0, #0
		BGT      |loc_080286B0|
		DCW     0xE734
|loc_080286B0|
		SUB r0, #1
		STR r0, [r1]
		DCW     0xE731
	INCBIN  baserom.gba_0x286b6_0x286b8.extracted
		DCD     0x03002FE4
	INCBIN  baserom.gba_0x286bc_0x286d2.extracted
|sub_080286D2|
	LSR      r4, r0, #0x20
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_080286F2|
	MOV      r0, #0x50
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080286F2|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_080286F2|
|unk_080286F2|
		LDR r0, [pc, #0x2c8]
		LDR r7, [pc, #0x2c8]
		STR r0, [r4]
		MOV r0, #0xc0
		STRH r0, [r4, #0xe]
		LDR r0, [r7]
		MOV r1, #0xc0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08028718|
		MOV r1, #0xc0
		LDR r0, [r7]
		BL       |sub_08011732|
		MOV r1, #0xc0
		LDR r0, [r7]
		BL       |loc_0801124C|
|loc_08028718|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x2a8]
		STR r0, [r4]
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x28]
		STR r2, [r4, #0x2c]
		MOV r2, #0
		STR r2, [r4, #0x1c]
		MOV r1, #0x38
		STRB r1, [r4, #8]
		SUB r5, #8
		LDR r1, [r5, #4]
		ADD r0, r4, #0
		ADD r0, #0x28
		CMP r6, #0
		STR r1, [r4, #4]
		BNE      |loc_08028740|
		LDR r1, [r5, #4]
		ADD r1, #0x2c
		STR r1, [r4, #4]
|loc_08028740|
		LDR r1, [sp, #0x10]
		STR r1, [r4, #0x4c]
		STR r2, [r4, #0x14]
		STRB r2, [r4, #0x10]
		MOV r1, #8
		STR r1, [r4, #0x40]
		MOV r1, #0
		MVN r1, r1
		STR r1, [r4, #0x18]
		STR r6, [r4, #0x44]
		LDMIA r5!, {r1, r2}
		STMIA r0!, {r1, r2}
		SUB r5, #8
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x20]
		STR r2, [r4, #0x24]
		LDR r0, [r4, #0x44]
		LDR r2, [pc, #0x264]
		LSL r1, r0, #4
		SUB r1, r1, r0
		LSL r1, r1, #2
		ADD r1, r1, r2
		STR r1, [r4, #0x48]
		LDR r1, [pc, #0x250]
		LSL r0, r0, #3
		ADD r1, #0x14
		ADD r0, r0, r1
		LDR r1, [r0]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x3c]
		STR r1, [r4, #0x38]
		ADD r0, r4, #0
		DCW     0xE7B5
|sub_08028782|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x234]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x23c]
	CMP      r1, r0
	BEQ      |loc_0802879C|
	LDR      r0, [pc, #0x228]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0802879C|
	LDR      r0, [pc, #0x230]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080287AA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080287AA|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r2, [r4, #0x10]
	ADD      r0, r1, #0
	SUB      sp, #0x3c
	CMP      r2, #0
	BEQ      |sub_080287EE|
	CMP      r2, #1
	BNE      |loc_080288A4|
	LDR      r0, [r4, #0x38]
	LDR      r1, [r4, #0x3c]
	LSL      r0, r0, #2
	LSL      r1, r1, #2
	STR      r1, [sp, #0x38]
	STR      r0, [sp, #0x34]
	LDR      r2, [r4, #0x20]
	ADD      r0, r2, r0
	STR      r0, [r4, #0x20]
	LDR      r0, [r4, #0x24]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x40]
	SUB      r0, #4
	STR      r0, [r4, #0x40]
	CMP      r0, #0
	BGT      |loc_080288A4|
	LDR      r5, [pc, #0x1dc]
	ADD      r1, r4, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
|sub_080287EE|
|unk_080287EE|
		LDR r1, [pc, #0x1d0]
		MOV r6, #1
		LDR r1, [r1, #8]
		ADD r1, #0x80
		CMP r0, #0
		DCW     0xD064
		LDR r0, [r4, #0x4c]
		CMP r0, #0
		DCW     0xD061
		LDR r0, [r4, #0x40]
		LDR r2, [r4, #0x38]
		LDR r3, [r4, #0x3c]
		MUL r2, r0
		MUL r3, r0
		ADD r0, r2, #0
		STR r2, [sp, #0x34]
		ADD r2, r3, #0
		STR r3, [sp, #0x38]
		LDR r3, [r4, #0x20]
		ADD r7, sp, #8
		ADD r0, r3, r0
		LDR r3, [r4, #0x24]
		STR r0, [sp, #0x34]
		ADD r2, r3, r2
		STR r2, [sp, #0x38]
		LDR r5, [sp, #0x38]
		ADD r2, r0, #0
		LDR r0, [r4, #0x4c]
		ADD r3, sp, #0
		STR r0, [sp, #0x28]
		LDR r0, [r4, #0x44]
		STRB r0, [r3, #0x1c]
		LDR r0, [pc, #0x1a4]
		STR r0, [sp, #0x24]
		MOV r0, #0
		STR r0, [sp, #0x20]
		STRB r0, [r3, #8]
		ADD r3, r2, #0
		ADD r0, r7, #4
		ADD r7, r5, #0
		SUB r7, #8
		SUB r3, #8
		ADD r2, #8
		ADD r5, #8
		STR r4, [sp, #0x38]
		STR r5, [sp, #0x18]
		STR r2, [sp, #0x14]
		STR r3, [sp, #0xc]
		STR r7, [sp, #0x10]
		LDR r1, [r1, #0x2c]
		LDR r5, [pc, #0x16c]
		BL       |loc_08009324|
		CMP r0, #0
		DCW     0xD047
		ADD r2, sp, #8
		MOV r1, #0
		LDR r0, [r5]
		BL       |loc_08011C0C|
		CMP r0, #0
		DCW     0xD026
		MOV r0, #0x36
		BL       |inc_0x0158_0x143f2|
		LDR r5, [pc, #0x164]
		ADD r1, r0, #0
		LDR r0, [r5]
		BL       |loc_0800EDF8|
		LDR r5, [r5]
		MOV r0, #4
		DCW     0xF014
		DCW     0xFE9B
		CMP r0, #0
		BEQ      |loc_0802888A|
		LDR r1, [pc, #0x154]
		STR r1, [r0]
|loc_0802888A|
		ADD r7, r0, #0
		MOV r1, #0
		ADD r0, r5, #0
		BL       |loc_0800ECDA|
		ADD r1, r7, #0
		ADD r0, r5, #0
		BL       |loc_0800ED18|
		MOV r0, #3
		BL       |inc_0x03d784_0x041118| + 0x2348
		DCW     0xE000
|loc_080288A4|
|unk_080288A4|
; cited by 0x080286F2 (a pc-relative load targets 0x080289BC)
		B        |loc_08028962|
		LDR r5, [pc, #0x130]
		LDR r1, [r5]
		STRB r0, [r1, #0x11]
		MOV r0, #0xff
		LDR r1, [pc, #0x130]
		ADD r0, #0x2d
		STR r0, [r1]
		STRB r6, [r4, #0x10]
		B        |loc_08028962|
		LDR r0, [r4, #0x40]
		CMP r0, #0x40
		BGE      |loc_080288C6|
		ADD r0, #4
		STR r0, [r4, #0x40]
		B        |loc_080288DE|
		B        |loc_080288F0|
|loc_080288C6|
		LDR r0, [r4, #0x38]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #2
		LSL r1, r1, #2
		STR r1, [sp, #4]
		STR r0, [sp]
		LDR r2, [r4, #0x20]
		ADD r0, r2, r0
		STR r0, [r4, #0x20]
		LDR r0, [r4, #0x24]
		ADD r0, r0, r1
		STR r0, [r4, #0x24]
|loc_080288DE|
		LDR r0, [r4, #0x1c]
		ADD r0, #1
		STR r0, [r4, #0x1c]
		CMP r0, #0xf0
		BLE      |loc_08028962|
		STRB r6, [r4, #0x10]
		B        |loc_08028962|
		STRB r6, [r4, #0x10]
		B        |loc_08028962|
|loc_080288F0|
		LDR r0, [r4, #0x40]
		LDR r2, [r4, #0x38]
		LDR r3, [r4, #0x3c]
		MUL r2, r0
		MUL r3, r0
		ADD r0, r2, #0
		STR r2, [sp, #0x34]
		ADD r2, r3, #0
		STR r3, [sp, #0x38]
		LDR r3, [r4, #0x20]
		ADD r0, r3, r0
		LDR r3, [r4, #0x24]
		STR r0, [sp, #0x34]
		ADD r2, r3, r2
		ADD r3, r0, #0
		ADD r0, #8
		ADD r5, r2, #0
		SUB r5, #8
		SUB r3, #8
		STR r2, [sp, #0x38]
		ADD r2, #8
		STR r0, [sp, #0x34]
		STR r2, [sp, #0x38]
		STR r3, [sp, #0x2c]
		STR r5, [sp, #0x30]
		LDR r1, [r1, #0x2c]
		ADD r0, sp, #0x2c
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_08028932|
		STRB r6, [r4, #0x10]
		B        |loc_08028962|
|loc_08028932|
		LDR r0, [r4, #0x40]
		CMP r0, #0x40
		BGE      |loc_0802893E|
		ADD r0, #4
		STR r0, [r4, #0x40]
		B        |loc_08028956|
|loc_0802893E|
		LDR r0, [r4, #0x38]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #2
		LSL r1, r1, #2
		STR r1, [sp, #0x28]
		STR r0, [sp, #0x24]
		LDR r2, [r4, #0x20]
		ADD r0, r2, r0
		STR r0, [r4, #0x20]
		LDR r0, [r4, #0x24]
		ADD r0, r0, r1
		STR r0, [r4, #0x24]
|loc_08028956|
		LDR r0, [r4, #0x1c]
		ADD r0, #1
		STR r0, [r4, #0x1c]
		CMP r0, #0xf0
		BLE      |loc_08028962|
		STRB r6, [r4, #0x10]
|loc_08028962|
		LDR r0, [r4, #0x14]
		ADD r0, #1
		ASR r2, r0, #2
		STR r0, [r4, #0x14]
		LDR r0, [r4, #0x18]
		CMP r0, r2
		BNE      |loc_08028972|
		DCW     0xE73B
|loc_08028972|
		STR r2, [r4, #0x18]
		LDRH r0, [r4, #0xc]
		LSL r2, r2, #0x1f
		LSR r2, r2, #0x1f
		LSL r6, r2, #1
		LDR r5, [pc, #0x64]
		ADD r6, r6, r2
		LDR r1, [r4, #0x48]
		LSL r0, r0, #5
		ADD r0, r0, r5
		LSL r6, r6, #2
		ADD r1, r1, r6
		LDR r1, [r1, #8]
		MOV r2, #0x40
		BL       |sub_08049138|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x48]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, #0x40
		MOV r2, #0x40
		LDR r1, [r1, #0x20]
		BL       |sub_08049138|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x48]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, #0x80
		ADD r1, r1, r6
		LDR r1, [r1, #0x2c]
		MOV r2, #0x40
		BL       |sub_08049138|
		DCW     0xE717
	INCBIN  baserom.gba_0x289ba_0x289de.extracted
|sub_080289DE|
	LSR      r4, r0, #0x20
	CMP      r7, #0xe4
	LSL      r0, r0, #0xc
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4}
	LDR      r1, [pc, #0x200]
	LDR      r3, [r0, #0x20]
	LDR      r1, [r1, #8]
	ADD      r2, r0, #0
	ADD      r1, #0x18
	LDR      r4, [r1]
	LDR      r0, [r0, #0x24]
	LDR      r1, [r1, #4]
	SUB      r3, r3, r4
	ADD      r2, #0x30
	SUB      sp, #8
	SUB      r0, r0, r1
	STR      r0, [sp, #4]
	LDR      r1, [sp, #4]
	STR      r3, [sp]
	STR      r1, [r2, #4]
	STR      r3, [r2]
	ADD      sp, #8
	POP      {r4}
	MOV      r0, #1
	BX       lr
|loc_08028A24|
	PUSH     {r4, r5, r6, r7}
	MOV      ip, r3
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r5, [sp, #0x10]
	LDR      r4, [r0, #0x48]
	LSL      r1, r1, #2
	ADD      r1, r4, r1
	MOV      r3, #0
	LDRSB    r6, [r1, r3]
	LDR      r4, [r0, #0x30]
	ADD      r3, r4, r6
	LDR      r4, [r5]
	LDR      r6, [r0, #0x34]
	ADD      r4, r3, r4
	MOV      r3, #1
	LDRSB    r7, [r1, r3]
	LDR      r5, [r5, #4]
	ADD      r3, r6, r7
	ADD      r3, r3, r5
	LDR      r7, [pc, #0x1ac]
	LDRB     r5, [r1, #2]
	LDRB     r6, [r1, #3]
	ADD      r7, #0x34
	LDR      r7, [r7, #8]
	ADD      r5, r4, r5
	ADD      r6, r3, r6
	CMP      r4, r7
	BGE      |loc_08028ACE|
	LDR      r7, [pc, #0x19c]
	ADD      r7, #0x34
	LDR      r7, [r7]
	CMP      r7, r5
	BGE      |loc_08028ACE|
	LDR      r5, [pc, #0x190]
	ADD      r5, #0x34
	LDR      r7, [r5, #0xc]
	CMP      r3, r7
	BGE      |loc_08028ACE|
	LDR      r5, [r5, #4]
	CMP      r5, r6
	BGE      |loc_08028ACE|
	LDR      r5, [r2]
	LDR      r1, [r1, #4]
	LDR      r6, [pc, #0x180]
	STR      r1, [r5]
	LDR      r1, [r2]
	LSL      r4, r4, #0x17
	LDR      r5, [r1]
	LSR      r4, r4, #7
	AND      r5, r6
	ORR      r4, r5
	STR      r4, [r1]
	LSR      r4, r4, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r4, r4, #8
	LDR      r1, [r2]
	ORR      r3, r4
	STR      r3, [r1]
	LDRH     r1, [r0, #0xc]
	ADD      r3, r1, #0
	LDR      r1, [r2]
	ADD      r3, ip
	ADD      r1, #4
	LDR      r4, [r1]
	LSL      r3, r3, #0x16
	LSR      r4, r4, #0xa
	LSL      r4, r4, #0xa
	LSR      r3, r3, #0x16
	ORR      r3, r4
	STR      r3, [r1]
	LDRB     r0, [r0, #8]
	MOV      r4, #3
	LSL      r4, r4, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r3, r4
	LDR      r1, [r2]
	ORR      r0, r3
	STR      r0, [r1, #4]
	LDR      r0, [r2]
	ADD      r0, #8
	STR      r0, [r2]
|loc_08028ACE|
	POP      {r4, r5, r6, r7}
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0x1c
	STR      r0, [sp, #0x18]
	LDR      r0, [r4, #0x40]
	ADD      r6, r1, #0
	CMP      r0, #0x40
	ADD      r7, sp, #0x18
	BGE      |loc_08028AF8|
	LDR      r2, [pc, #0x114]
	MOV      r3, #0
	ADD      r2, #0xc
	STR      r2, [sp]
	ADD      r2, r7, #0
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |loc_08028A24|
|loc_08028AF8|
	LDR      r0, [r4, #0x40]
	LDR      r1, [r4, #0x38]
	LDR      r2, [r4, #0x3c]
	MUL      r1, r0
	MUL      r2, r0
	STR      r2, [sp, #0xc]
	STR      r2, [sp, #0x14]
	ADD      r2, sp, #0x10
	ADD      r0, r1, #0
	STR      r2, [sp]
	STR      r1, [sp, #8]
	MOV      r1, #3
	ADD      r2, r7, #0
	STR      r0, [sp, #0x10]
	MOV      r3, #4
	ADD      r0, r4, #0
	BL       |loc_08028A24|
	LDR      r0, [r4, #0x40]
	MOV      r5, #0
	SUB      r0, #1
	CMP      r0, #0
	BLE      |loc_08028B50|
|loc_08028B26|
	LDR      r0, [r4, #0x38]
	LDR      r1, [r4, #0x3c]
	MUL      r0, r5
	MUL      r1, r5
	STR      r0, [sp]
	ADD      r2, sp, #8
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	MOV      r1, #2
	ADD      r2, r7, #0
	STR      r0, [sp, #8]
	MOV      r3, #2
	ADD      r0, r4, #0
	BL       |loc_08028A24|
	LDR      r0, [r4, #0x40]
	ADD      r5, #8
	SUB      r0, #1
	CMP      r0, r5
	BGT      |loc_08028B26|
|loc_08028B50|
	LDR      r0, [sp, #0x18]
	STR      r0, [r6]
	ADD      sp, #0x1c
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0xc
	CMP      r1, #0
	BEQ      |sub_08028B7C|
	CMP      r1, #0xb
	BEQ      |loc_08028BE6|
	CMP      r1, #0xc
	BNE      |loc_08028BEA|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0
	ADD      sp, #0xc
	POP      {r4, r5, pc}
|sub_08028B7C|
|unk_08028B7C|
		LDR r1, [r2, #0x30]
		ADD r5, r2, #0
		CMP r1, r0
		BNE      |loc_08028B88|
		MOV r0, #0
		DCW     0xE7F7
|loc_08028B88|
		LDRB r1, [r5, #0x14]
		LDR r2, [r0, #0x44]
		MOV r3, #1
		EOR r2, r3
		CMP r1, r2
		BEQ      |loc_08028B98|
		MOV r0, #0
		DCW     0xE7EF
|loc_08028B98|
		LDR r1, [r0, #0x40]
		LDR r2, [r0, #0x38]
		LDR r3, [r0, #0x3c]
		MUL r2, r1
		MUL r3, r1
		ADD r1, r2, #0
		STR r2, [sp, #4]
		ADD r2, r3, #0
		STR r3, [sp, #8]
		LDR r3, [r0, #0x20]
		LDR r0, [r0, #0x24]
		ADD r1, r3, r1
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ADD r2, r0, #0
		ADD r4, r0, #0
		ADD r0, r5, #4
		STR r1, [sp, #4]
		ADD r3, r1, #0
		LDR r5, [r5, #4]
		ADD r3, #0xc
		SUB r1, #0xc
		ADD r4, #0xc
		SUB r2, #0xc
		CMP r5, r3
		BGE      |loc_08028BE2|
		LDR r3, [r0, #8]
		CMP r1, r3
		BGE      |loc_08028BE2|
		LDR r1, [r0, #4]
		CMP r1, r4
		BGE      |loc_08028BE2|
		LDR r0, [r0, #0xc]
		CMP r2, r0
		BGE      |loc_08028BE2|
		MOV r0, #1
		DCW     0xE7CA
|loc_08028BE2|
		MOV r0, #0
		DCW     0xE7C8
|loc_08028BE6|
|unk_08028BE6|
		MOV r0, #0
		DCW     0xE7C6
|loc_08028BEA|
|unk_08028BEA|
		MOV r0, #0
		DCW     0xE7C4
|sub_08028BEE|
	CMP      r1, #3
	BLT      |sub_08028BF6|
	MOV      r0, #1
	BX       lr
|sub_08028BF6|
|unk_08028BF6|
; cited by 0x080289FA (a pc-relative load targets 0x08028BFC)
		MOV r0, #0
		BX       lr
	INCBIN  baserom.gba_0x28bfa_0x28c02.extracted
|sub_08028C02|
|unk_08028C02|
	INCBIN  baserom.gba_0x28c02_0x28c04.extracted
		PUSH {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_08028C22|
	MOV      r0, #0x44
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08028C22|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_08028C22|
|unk_08028C22|
		LDR r0, [pc, #0x274]
		LDR r7, [pc, #0x274]
		STR r0, [r4]
		MOV r0, #0xc0
		STRH r0, [r4, #0xe]
		LDR r0, [r7]
		MOV r1, #0xc0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08028C48|
		MOV r1, #0xc0
		LDR r0, [r7]
		BL       |sub_08011732|
		MOV r1, #0xc0
		LDR r0, [r7]
		BL       |loc_0801124C|
|loc_08028C48|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x254]
		STR r0, [r4]
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x1c]
		STR r2, [r4, #0x20]
		MOV r1, #0x38
		STRB r1, [r4, #8]
		SUB r5, #8
		LDR r1, [r5, #4]
		ADD r0, r4, #0
		ADD r0, #0x1c
		CMP r6, #0
		STR r1, [r4, #4]
		BNE      |loc_08028C6C|
		LDR r1, [r5, #4]
		ADD r1, #0x2c
		STR r1, [r4, #4]
|loc_08028C6C|
		LDR r1, [sp, #0x10]
		STR r1, [r4, #0x40]
		MOV r1, #0
		STR r1, [r4, #0x14]
		STRB r1, [r4, #0x10]
		MOV r1, #8
		STR r1, [r4, #0x34]
		MOV r1, #0
		MVN r1, r1
		STR r1, [r4, #0x18]
		STR r6, [r4, #0x38]
		LDMIA r5!, {r1, r2}
		STMIA r0!, {r1, r2}
		LDR r0, [r4, #0x38]
		LDR r2, [pc, #0x218]
		LSL r1, r0, #1
		ADD r1, r1, r0
		LSL r1, r1, #3
		ADD r1, r1, r2
		LDR r2, [pc, #0x208]
		LSL r0, r0, #3
		ADD r2, #8
		ADD r0, r0, r2
		STR r1, [r4, #0x3c]
		LDR r2, [r0]
		LDR r0, [r0, #4]
		LDR r5, [pc, #0x204]
		STR r0, [r4, #0x30]
		STR r2, [r4, #0x2c]
		LDRH r0, [r4, #0xc]
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r5
		MOV r2, #0x40
		BL       |sub_08049138|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, #0x40
		MOV r2, #0x80
		LDR r1, [r1, #0x14]
		BL       |sub_08049138|
		ADD r0, r4, #0
		DCW     0xE7A9
|sub_08028CCA|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1c8]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x1d4]
	CMP      r1, r0
	BEQ      |loc_08028CE4|
	LDR      r0, [pc, #0x1bc]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08028CE4|
	LDR      r0, [pc, #0x1c8]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08028CF2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08028CF2|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0, #0x10]
	SUB      sp, #0x38
	LDR      r6, [pc, #0x19c]
	CMP      r0, #0
	BEQ      |sub_08028D1C|
	CMP      r0, #1
	BNE      |loc_08028D18|
	LDR      r0, [r4, #0x34]
	SUB      r0, #4
	STR      r0, [r4, #0x34]
	CMP      r0, #0
	BGT      |loc_08028D18|
	ADD      r1, r4, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08028D18|
	ADD      sp, #0x38
	POP      {r4, r5, r6, pc}
|sub_08028D1C|
|unk_08028D1C|
		CMP r1, #0
		BEQ      |loc_08028D18|
		LDR r0, [r4, #0x34]
		LDR r1, [r4, #0x2c]
		LDR r2, [r4, #0x30]
		MUL r1, r0
		MUL r2, r0
		ADD r0, r1, #0
		STR r1, [sp, #0x30]
		ADD r1, r2, #0
		STR r2, [sp, #0x34]
		LDR r2, [r4, #0x1c]
		ADD r3, sp, #0
		ADD r0, r2, r0
		LDR r2, [r4, #0x20]
		STR r0, [sp, #0x30]
		ADD r1, r2, r1
		STR r1, [sp, #0x34]
		LDR r2, [sp, #0x34]
		ADD r1, r0, #0
		LDR r0, [r4, #0x40]
		ADD r5, sp, #4
		STR r0, [sp, #0x24]
		LDR r0, [r4, #0x38]
		STRB r0, [r3, #0x18]
		LDR r0, [pc, #0x164]
		MOV r3, #0
		STR r0, [sp, #0x20]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x1c]
		ADD r0, r3, #0
		ADD r3, sp, #0
		STRB r0, [r3, #4]
		ADD r0, r5, #4
		ADD r5, r2, #0
		ADD r3, r1, #0
		SUB r3, #8
		ADD r1, #8
		SUB r5, #8
		ADD r2, #8
		STR r4, [sp, #0x34]
		STR r2, [sp, #0x14]
		STR r5, [sp, #0xc]
		STR r1, [sp, #0x10]
		STR r3, [sp, #8]
		LDR r1, [r6, #4]
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		MOV r5, #1
		CMP r0, #0
		BEQ      |loc_08028DAA|
		ADD r2, sp, #4
		MOV r1, #0
		LDR r0, [r6]
		BL       |loc_08011C0C|
		CMP r0, #0
		BEQ      |loc_08028D9A|
		STRB r5, [r4, #0x10]
		B        |loc_08028D18|
|loc_08028D9A|
		LDR r0, [r4, #0x34]
		CMP r0, #0x50
		BGE      |loc_08028DA6|
		ADD r0, #4
		STR r0, [r4, #0x34]
		B        |loc_08028D18|
|loc_08028DA6|
		STRB r5, [r4, #0x10]
		B        |loc_08028D18|
|loc_08028DAA|
		STRB r5, [r4, #0x10]
		B        |loc_08028D18|
|sub_08028DAE|
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4}
	LDR      r1, [pc, #0xd8]
	LDR      r3, [r0, #0x1c]
	LDR      r1, [r1, #4]
	ADD      r2, r0, #0
	ADD      r1, #0x18
	LDR      r4, [r1]
	LDR      r0, [r0, #0x20]
	LDR      r1, [r1, #4]
	SUB      r3, r3, r4
	ADD      r2, #0x24
	SUB      sp, #8
	SUB      r0, r0, r1
	STR      r0, [sp, #4]
	LDR      r1, [sp, #4]
	STR      r3, [sp]
	STR      r1, [r2, #4]
	STR      r3, [r2]
	ADD      sp, #8
	POP      {r4}
	MOV      r0, #1
	BX       lr
|loc_08028DEA|
	PUSH     {r4, r5, r6, r7}
	MOV      ip, r3
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r5, [sp, #0x10]
	LDR      r4, [r0, #0x3c]
	LSL      r1, r1, #2
	ADD      r1, r4, r1
	MOV      r3, #0
	LDRSB    r6, [r1, r3]
	LDR      r4, [r0, #0x24]
	ADD      r3, r4, r6
	LDR      r4, [r5]
	LDR      r6, [r0, #0x28]
	ADD      r4, r3, r4
	MOV      r3, #1
	LDRSB    r7, [r1, r3]
	LDR      r5, [r5, #4]
	ADD      r3, r6, r7
	ADD      r3, r3, r5
	LDR      r7, [pc, #0x88]
	LDRB     r5, [r1, #2]
	LDRB     r6, [r1, #3]
	ADD      r7, #0x28
	LDR      r7, [r7, #8]
	ADD      r5, r4, r5
	ADD      r6, r3, r6
	CMP      r4, r7
	BGE      |loc_08028E94|
	LDR      r7, [pc, #0x74]
	ADD      r7, #0x28
	LDR      r7, [r7]
	CMP      r7, r5
	BGE      |loc_08028E94|
	LDR      r5, [pc, #0x6c]
	ADD      r5, #0x28
	LDR      r7, [r5, #0xc]
	CMP      r3, r7
	BGE      |loc_08028E94|
	LDR      r5, [r5, #4]
	CMP      r5, r6
	BGE      |loc_08028E94|
	LDR      r5, [r2]
	LDR      r1, [r1, #4]
	LDR      r6, [pc, #0x74]
	STR      r1, [r5]
	LDR      r1, [r2]
	LSL      r4, r4, #0x17
	LDR      r5, [r1]
	LSR      r4, r4, #7
	AND      r5, r6
	ORR      r4, r5
	STR      r4, [r1]
	LSR      r4, r4, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r4, r4, #8
	LDR      r1, [r2]
	ORR      r3, r4
	STR      r3, [r1]
	LDRH     r1, [r0, #0xc]
	ADD      r3, r1, #0
	LDR      r1, [r2]
	ADD      r3, ip
	ADD      r1, #4
	LDR      r4, [r1]
	LSL      r3, r3, #0x16
	LSR      r4, r4, #0xa
	LSL      r4, r4, #0xa
	LSR      r3, r3, #0x16
	ORR      r3, r4
	STR      r3, [r1]
	LDRB     r0, [r0, #8]
	MOV      r4, #3
	LSL      r4, r4, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r3, r4
	LDR      r1, [r2]
	ORR      r0, r3
	STR      r0, [r1, #4]
	LDR      r0, [r2]
	ADD      r0, #8
	STR      r0, [r2]
|loc_08028E94|
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_08028E98|
	DCW      0x9680
	DCW      0x0804,0xeac4,0x0874,0xcdd4,0x0804,0xefec,0x0874,0x0000
	DCW      0x0601,0xffff,0x0000,0xe454,0x0804,0x8088,0x086b,0xffff
|sub_08028EBA|
|unk_08028EBA|
	INCBIN  baserom.gba_0x28eba_0x28ebc.extracted
		PUSH {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0x1c
	STR      r0, [sp, #0x18]
	ADD      r6, r1, #0
	LDR      r1, [r4, #0x2c]
	LDR      r0, [r4, #0x34]
	LDR      r2, [r4, #0x30]
	MUL      r1, r0
	MUL      r2, r0
	STR      r2, [sp, #0xc]
	STR      r2, [sp, #0x14]
	ADD      r2, sp, #0x10
	ADD      r0, r1, #0
	STR      r2, [sp]
	STR      r1, [sp, #8]
	ADD      r7, sp, #0x18
	ADD      r2, r7, #0
	MOV      r1, #1
	STR      r0, [sp, #0x10]
	MOV      r3, #2
	ADD      r0, r4, #0
	BL       |loc_08028DEA|
	LDR      r0, [r4, #0x34]
	MOV      r5, #0
	SUB      r0, #1
	CMP      r0, #0
	BLE      |loc_08028F22|
|loc_08028EF8|
	LDR      r0, [r4, #0x2c]
	LDR      r1, [r4, #0x30]
	MUL      r0, r5
	MUL      r1, r5
	STR      r0, [sp]
	ADD      r2, sp, #8
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	MOV      r1, #0
	ADD      r2, r7, #0
	STR      r0, [sp, #8]
	MOV      r3, #0
	ADD      r0, r4, #0
	BL       |loc_08028DEA|
	LDR      r0, [r4, #0x34]
	ADD      r5, #8
	SUB      r0, #1
	CMP      r0, r5
	BGT      |loc_08028EF8|
|loc_08028F22|
	LDR      r0, [sp, #0x18]
	STR      r0, [r6]
	ADD      sp, #0x1c
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	CMP      r1, #0
	SUB      sp, #0xc
	BEQ      |sub_08028F56|
	CMP      r1, #0xb
	BEQ      |loc_08028FC0|
	CMP      r1, #0xc
	BEQ      |loc_08028FE8|
	CMP      r1, #0x26
	BNE      |loc_08028FFA|
	CMP      r4, r2
	BNE      |loc_08028FBC|
	LDR      r0, [pc, #0xc4]
	ADD      r1, r4, #0
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r0, #1
	ADD      sp, #0xc
	POP      {r4, r5, pc}
|sub_08028F56|
|unk_08028F56|
		LDR r0, [r2, #0x30]
		CMP r0, r4
		BNE      |loc_08028F60|
		MOV r0, #0
		DCW     0xE7F8
|loc_08028F60|
		LDRB r0, [r2, #0x14]
		LDR r1, [r4, #0x38]
		MOV r3, #1
		EOR r1, r3
		CMP r0, r1
		BEQ      |loc_08028F70|
		MOV r0, #0
		DCW     0xE7F0
|loc_08028F70|
		LDR r0, [r4, #0x34]
		LDR r1, [r4, #0x2c]
		LDR r3, [r4, #0x30]
		MUL r1, r0
		MUL r3, r0
		ADD r0, r1, #0
		STR r1, [sp, #4]
		ADD r1, r3, #0
		STR r3, [sp, #8]
		LDR r3, [r4, #0x1c]
		ADD r2, #4
		ADD r0, r3, r0
		LDR r3, [r4, #0x20]
		STR r0, [sp, #4]
		ADD r1, r3, r1
		STR r1, [sp, #8]
		ADD r4, r1, #0
		ADD r3, r0, #0
		LDR r5, [r2]
		ADD r3, #0xc
		SUB r0, #0xc
		ADD r4, #0xc
		SUB r1, #0xc
		CMP r5, r3
		BGE      |loc_08028FB8|
		LDR r3, [r2, #8]
		CMP r0, r3
		BGE      |loc_08028FB8|
		LDR r0, [r2, #4]
		CMP r0, r4
		BGE      |loc_08028FB8|
		LDR r0, [r2, #0xc]
		CMP r1, r0
		BGE      |loc_08028FB8|
		MOV r0, #1
		DCW     0xE7CC
|loc_08028FB8|
		MOV r0, #0
		DCW     0xE7CA
|loc_08028FBC|
|unk_08028FBC|
		MOV r0, #0
		DCW     0xE7C8
|loc_08028FC0|
|unk_08028FC0|
		LDRH r0, [r4, #0xc]
		LDR r5, [pc, #0x4c]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #5
		ADD r0, r0, r5
		MOV r2, #0x40
		LDR r1, [r1, #8]
		BL       |sub_08049138|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, #0x40
		MOV r2, #0x80
		LDR r1, [r1, #0x14]
		BL       |sub_08049138|
		MOV r0, #0
		DCW     0xE7B4
|loc_08028FE8|
|unk_08028FE8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #0
		DCW     0xE7AB
|loc_08028FFA|
|unk_08028FFA|
		MOV r0, #0
		DCW     0xE7A9
|sub_08028FFE|
	CMP      r1, #3
	BLT      |sub_08029006|
	MOV      r0, #1
	BX       lr
|sub_08029006|
|unk_08029006|
		MOV r0, #0
		BX       lr
	INCBIN  baserom.gba_0x2900a_0x2900e.extracted
|sub_0802900E|
	LSR      r4, r6, #1
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
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
|sub_08029272|
	MOV      r2, #0
	SUB      r2, r3, r2
	STR      r2, [r1, #8]
	ADD      r0, r3, #0
	ADD      r3, sp, #0x100
	MOV      r1, #3
	STRB     r1, [r3, #0x1f]
	MOV      r1, #0xa9
	STR      r1, [sp, #0x120]
	MOV      r1, #0x58
	STR      r1, [sp, #0x124]
	STRB     r0, [r3, #0x1c]
	LDR      r0, [r4, #0x18]
	LSL      r0, r0, #1
	ADD      r0, r0, r5
	ADD      r0, #0x2e
	LDRB     r2, [r0]
	ADD      r2, #1
	ADD      r0, r7, #0
	ADD      r1, pc, #0x3C
	BL       |inc_0x03d784_0x041118| + 0x512
	ADD      r1, r7, #0
	LDR      r0, [sp, #0x150]
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x20]
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	ADD      r0, sp, #0x11c
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x154
	POP      {r4, r5, r6, r7, pc}
|sub_080292BA|
	DCW      0x0000
	DCW      0xbce8,0x0806,0xf04c,0x0874,0xf800,0x0600,0x9640,0x0600
	DCW      0x0259,0x0000,0x1f83,0x0000,0xf5a5,0x0803
|loc_080292D8|
|unk_080292D8|
	INCBIN  baserom.gba_0x292d8_0x292e0.extracted
		PUSH {r4, r5, r6, lr}
		ADD r3, r2, #0
		MOV r2, #0
		CMP r3, #1
		LDR r5, [pc, #0x8c]
		BEQ      |sub_0802931C|
		MOV r1, #0x9f
		ADD r0, #0xff
		ADD r0, #1
		LSL r1, r1, #3
		MOV r4, #1
		CMP r3, #4
		DCW     0xD01D
		CMP r3, #5
		BNE      |sub_0802936E|
		LDR r6, [r0, #0x14]
		MOV r3, #0x68
		LDR r5, [r5, #8]
		MUL r3, r6
		ADD r3, r3, r5
		ADD r1, r3, r1
		LDR r3, [r0, #0x18]
		LSL r3, r3, #1
		ADD r1, r3, r1
		ADD r1, #0x2e
		LDRB r3, [r1]
		ADD r3, r3, r4
		LSL r3, r3, #0x18
		LSR r3, r3, #0x18
		B        |loc_08029360|
|sub_0802931C|
	ADD      r3, r2, #0
	LDR      r4, [pc, #0x60]
	LDR      r0, [r5]
	MOV      r2, #0x40
	ADD      r0, r0, r4
	LDR      r1, [pc, #0x54]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
	LDR      r6, [r0, #0x14]
	MOV      r3, #0x68
	LDR      r5, [r5, #8]
	MUL      r3, r6
	ADD      r3, r3, r5
	ADD      r1, r3, r1
	LDR      r3, [r0, #0x18]
	LSL      r3, r3, #1
	ADD      r1, r3, r1
	ADD      r1, #0x2e
	LDRB     r3, [r1]
	SUB      r3, r3, r4
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
|loc_08029352|
	STRB     r3, [r1]
	LDRB     r4, [r1]
	CMP      r4, r3
	BNE      |loc_08029352|
	STR      r2, [r0, #0x10]
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|loc_08029360|
	STRB     r3, [r1]
	LDRB     r4, [r1]
	CMP      r4, r3
	BNE      |loc_08029360|
	STR      r2, [r0, #0x10]
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|sub_0802936E|
|unk_0802936E|
		MOV r0, #0
		POP {r4, r5, r6, pc}
		MOV r0, #0
		BX       lr
|sub_08029376|
	LSL      r0, r0, #0
	DCW      0xf04c,0x0874
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
|loc_08029384|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r7, r3, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r6, [sp, #0x28]
	BNE      |sub_080293A4|
	MOV      r0, #0x58
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080293A4|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_080293A4|
|unk_080293A4|
		MOV r1, #1
		LSL r1, r1, #0xa
		ADD r0, r4, #0
		LDR r2, [sp, #0xc]
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x208]
		LDR r2, [pc, #0x20c]
		STR r0, [r4]
		STR r7, [r4, #0x50]
		LDR r3, [r5]
		LDR r5, [r5, #4]
		LSL r3, r3, #8
		STR r3, [r4, #0x20]
		LSL r5, r5, #8
		STR r5, [r4, #0x24]
		MOV r3, #0
		STR r3, [r4, #0x48]
		STR r2, [r4, #0x54]
		ADD r0, r4, #0
		ADD r0, #0x40
		STR r3, [r4, #0x4c]
		STR r2, [r4, #0x18]
		STR r3, [r0]
		ADD r1, r0, #4
		STR r3, [r1]
		STRB r6, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		DCW     0xE7DD
|sub_080293E4|
	PUSH     {r4, lr}
	LDRB     r1, [r0, #0x10]
	LDR      r3, [pc, #0x1d8]
	LDR      r4, [pc, #0x1e0]
	LSL      r1, r1, #3
	LDR      r2, [r3, r1]
	ADD      r1, r1, r3
	STR      r2, [r0, #0x40]
	LDR      r1, [r1, #4]
	MOV      r2, #0x40
	STR      r1, [r0, #0x44]
	LDR      r0, [pc, #0x1c8]
	MOV      r3, #0
	SUB      r0, #0xc
	LDR      r0, [r0]
	LDR      r1, [pc, #0x1c4]
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xbf4
	POP      {r4, pc}
	MOV      r1, #0x10
	STR      r1, [r0, #0x4c]
	LDR      r1, [pc, #0x1bc]
	STR      r1, [r0, #0x54]
	ADD      r0, #0x40
	MOV      r1, #0
	STMIA    r0!, {r1}
	STR      r1, [r0]
	BX       lr
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r5, #0x40
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x20]
	LDR      r1, [r5]
	SUB      sp, #0x34
	ADD      r0, r0, r1
	STR      r0, [r4, #0x20]
	LDR      r0, [r4, #0x24]
	LDR      r1, [r5, #4]
	ADD      r6, r5, #4
	ADD      r0, r0, r1
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x48]
	ADD      r0, #1
	STR      r0, [r4, #0x48]
	LSL      r0, r0, #0x1c
	LSR      r1, r0, #0x1f
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r0, [r4, #0x54]
	LSL      r1, r1, #2
	ADD      r0, r0, r1
	STR      r0, [r4, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r7, [pc, #0x16c]
	LDR      r0, [r4, #0x4c]
	SUB      r7, #0xc
	CMP      r0, #0
	BEQ      |sub_08029472|
	SUB      r0, #1
	STR      r0, [r4, #0x4c]
	BNE      |loc_0802946E|
	ADD      r1, r4, #0
	LDR      r0, [r7, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_0802946E|
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
|sub_08029472|
|unk_08029472|
		LDR r0, [r4, #0x40]
		LDR r1, [r4, #0x44]
		ORR r0, r1
		BEQ      |loc_0802946E|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x478a
		CMP r0, #0
		BNE      |loc_0802948E|
		ADD r1, r4, #0
		LDR r0, [r7, #4]
		BL       |loc_08011944|
		B        |loc_0802946E|
|loc_0802948E|
		LDR r7, [pc, #0x134]
		ADD r0, r4, #0
		SUB r7, #0xc
		LDR r1, [r7, #8]
		ADD r0, #0x28
		ADD r7, r0, #0
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_080294B6|
		MOV r0, #0x10
		STR r0, [r4, #0x4c]
		LDR r0, [pc, #0x124]
		STR r0, [r4, #0x54]
		MOV r0, #0
		STR r0, [r5]
		STR r0, [r6]
		B        |loc_0802946E|
|loc_080294B6|
		LDR r0, [sp, #0x38]
		CMP r0, #0
		BEQ      |loc_0802946E|
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		BEQ      |loc_0802946E|
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x104]
		STR r0, [sp, #0x1c]
		LDR r0, [r4, #0x50]
		STR r0, [sp, #0x18]
		ADD r0, sp, #4
		LDMIA r7!, {r1, r2, r3, r7}
		STMIA r0!, {r1, r2, r3, r7}
		LDRB r0, [r4, #0x11]
		LDR r7, [pc, #0xe4]
		ADD r3, sp, #0
		STRB r0, [r3]
		MOV r1, #0
		SUB r7, #0xc
		STR r4, [sp, #0x30]
		LDR r0, [r7, #4]
		MOV r2, sp
		BL       |loc_08011C70|
		CMP r0, #0
		BEQ      |loc_0802946E|
		LDR r7, [r7]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0xd4]
		LSL r0, r0, #2
		ADD r1, r0, r1
		ADD r0, r7, #0
		LDR r7, [pc, #0xc0]
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r0, r7
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #0x10
		STR r0, [r4, #0x4c]
		LDR r0, [pc, #0xb4]
		MOV r3, #0
		STR r0, [r4, #0x54]
		STR r3, [r5]
		STR r3, [r6]
		B        |loc_0802946E|
|sub_08029526|
	PUSH     {r3, lr}
	CMP      r1, #0
	BNE      |loc_0802957E|
	LDR      r1, [r0, #0x4c]
	CMP      r1, #0
	BNE      |loc_0802957A|
	LDR      r1, [r2, #0x30]
	CMP      r1, r0
	BNE      |sub_0802953C|
	MOV      r0, #0
	POP      {r3, pc}
|sub_0802953C|
|unk_0802953C|
		LDR r1, [r2, #0x1c]
		LDRB r1, [r1]
		CMP r1, #1
		BNE      |loc_0802957A|
		ADD r1, r2, #4
		LDR r2, [r2, #4]
		LDR r3, [r0, #0x30]
		CMP r2, r3
		BGE      |loc_0802957A|
		LDR r2, [r0, #0x28]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_0802957A|
		LDR r2, [r1, #4]
		LDR r3, [r0, #0x34]
		CMP r2, r3
		BGE      |loc_0802957A|
		LDR r2, [r0, #0x2c]
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BGE      |loc_0802957A|
		MOV r1, #0x10
		STR r1, [r0, #0x4c]
		LDR r1, [pc, #0x64]
		STR r1, [r0, #0x54]
		ADD r0, #0x40
		MOV r1, #0
		STMIA r0!, {r1}
		STR r1, [r0]
		MOV r0, #1
		DCW     0xE7DF
|loc_0802957A|
|unk_0802957A|
		MOV r0, #0
		DCW     0xE7DD
|loc_0802957E|
|unk_0802957E|
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		DCW     0xE7DA
|sub_08029584|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	LDR      r4, [pc, #0x3c]
	ADD      r7, r3, #0
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	SUB      r4, #0xc
	LDR      r0, [r4, #4]
	SUB      sp, #4
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_080295B6|
	ADD      r3, r5, #0
	ADD      r2, r6, #0
	MOV      r0, #0
	STR      r7, [sp]
	LDR      r1, [sp, #4]
	BL       |loc_08029384|
	ADD      r1, r0, #0
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_080295B6|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
|unk_080295BC|
	INCBIN	baserom.gba_0x295bc_0x295be.extracted
	LSR      r4, r0, #0x20
	LSL      r4, r5, #7
	LSR      r5, r6, #1
	DCW      0xf08c,0x0874
	STR      r4, [sp, #0x100]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LSL      r4, r0, #8
	LSR      r5, r6, #1
	STRH     r0, [r3, #6]
	LSR      r3, r5, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0xa0]
	ADD      r6, r1, #0
	LDR      r1, [r0]
	MOV      r4, #0
	CMP      r1, #0
	SUB      sp, #0x40
	BEQ      |loc_0802965A|
	ADD      r0, sp, #8
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x10]
	LDR      r2, [sp, #0x14]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0xc]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r1, [sp]
	STR      r1, [sp, #0x18]
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x1c]
	ADD      r0, sp, #0x20
	ADD      r1, r6, #0
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [sp, #0x20]
	LDR      r1, [sp, #0x28]
	LDR      r2, [sp, #0x2c]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x24]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x34]
	ASR      r1, r1, #1
	LDR      r0, [sp, #0x18]
	STR      r1, [sp]
	STR      r1, [sp, #0x30]
	SUB      r1, r0, r1
	LDR      r0, [sp, #0x1c]
	LDR      r2, [sp, #0x34]
	STR      r1, [sp]
	SUB      r0, r0, r2
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x3c]
	ADD      r0, r1, #0
	MUL      r0, r1
	STR      r1, [sp, #0x38]
	LDR      r1, [sp, #0x3c]
	ADD      r2, r1, #0
	MUL      r1, r2
	ADD      r0, r0, r1
	LDR      r1, [r5, #0xc]
	CMP      r0, r1
	BLE      |loc_0802965A|
	MOV      r4, #1
|loc_0802965A|
	ADD      r0, r4, #0
	ADD      sp, #0x40
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029680|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_08029680|
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	ADD      r6, pc, #0x3A0
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080296A0|
	LDR      r1, [pc, #0x14]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_080296A0|
	POP      {r4, pc}
	LDR      r0, [r0, #0xc]
	ADD      r1, #0xff
	ADD      r1, #0xc1
	STR      r0, [r1, #0x24]
	MOV      r0, #0
	BX       lr
|sub_080296AE|
|unk_080296AE|
	INCBIN	baserom.gba_0x296ae_0x296b2.extracted
|sub_080296B2|
	LSR      r4, r0, #0x20
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDRH     r0, [r1, #0x12]
	SUB      sp, #8
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x18
	BCC      |sub_080296E8|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #8
	POP      {r4, r5, r6, pc}
|sub_080296E8|
|unk_080296E8|
		LSL r0, r0, #0x15
		LSR r0, r0, #0x18
		STRB r0, [r4, #0x11]
		CMP r0, #1
		DCW     0xD3F8
		MOV r0, #1
		STRB r0, [r4, #0x11]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		LDR r0, [r5, #4]
		ADD r6, r4, #0
		LDR r2, [pc, #0x13c]
		ADD r6, #0xff
		LSL r0, r0, #3
		LDR r0, [r2, r0]
		ADD r6, #0xa1
		LDR r1, [r6]
		LSL r0, r0, #8
		ADD r0, r1, r0
		STR r0, [sp]
		LDR r1, [r5, #4]
		MOV r0, #0xff
		LSL r1, r1, #3
		ADD r1, r1, r2
		LDR r1, [r1, #4]
		ADD r0, #0xa5
		LDR r0, [r0, r4]
		LSL r1, r1, #8
		ADD r0, r0, r1
		STR r0, [sp, #4]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		MOV r3, sp
		ADD r2, r2, r1
		ADD r1, r3, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0802974C|
		LDR r0, [sp]
		STR r0, [r6]
		LDR r1, [sp, #4]
		STR r1, [r6, #4]
		B        |loc_08029768|
|loc_0802974C|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
|loc_08029768|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		DCW     0xE7B5
		PUSH {r4, r5, r6, r7, lr}
		ADD r6, r0, #0
		LDR r0, [pc, #0xcc]
		SUB sp, #0xc
		ADD r4, r1, #0
		LDR r0, [r0]
		MOV r1, #0
		LDR r2, [pc, #0xcc]
		STR r1, [sp, #4]
		CMP r4, #0
		LDR r7, [pc, #0xc0]
		STR r0, [sp, #8]
		STR r2, [sp]
		BEQ      |loc_0802979A|
		ADD r1, r4, #0
		ADD r1, #0xff
		ADD r1, #0x8d
|loc_0802979A|
		MOV r0, sp
		BL       |loc_0801599C|
		LDR r0, [pc, #0xa8]
		LDR r1, [r0]
		LDRB r0, [r1, #0x10]
		CMP r0, #0
		BEQ      |loc_080297CC|
		CMP r0, #1
		BEQ      |loc_080297CC|
		CMP r0, #2
		BEQ      |loc_080297B6|
		CMP r0, #3
		DCW     0xD118
|loc_080297B6|
		ADD r0, r1, #0
		ADD r0, #0xff
		ADD r0, #0xa5
		MOV r1, #0xff
		ADD r1, #0xa5
		LDR r0, [r0]
		LDR r1, [r1, r4]
		CMP r0, r1
		BLE      |sub_080297E6|
		MOV r5, #1
		DCW     0xE00D
|loc_080297CC|
		ADD r0, r1, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		MOV r1, #0xff
		ADD r1, #0xa1
		LDR r0, [r0]
		LDR r1, [r1, r4]
		CMP r0, r1
		BLE      |loc_080297E2|
		MOV r5, #2
		DCW     0xE002
|loc_080297E2|
		MOV r5, #3
		DCW     0xE000
|sub_080297E6|
	MOV      r5, #0
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080297F8|
	LDR      r1, [pc, #0x64]
	STMIA    r0!, {r1, r5}
	SUB      r0, #8
|loc_080297F8|
	ADD      r5, r0, #0
	MOV      r1, #0x12
	STR      r0, [r6, #4]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [sp, #4]
	STR      r7, [sp]
	CMP      r0, #0
	BEQ      |loc_08029820|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08029820|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	LDR      r2, [r0, #4]
	LDR      r1, [r1, #0x14]
	MOV      r3, #1
	ADD      r0, r3, #0
	CMP      r1, r2
	BEQ      |loc_08029832|
	MOV      r0, #0
|loc_08029832|
	SUB      r0, r3, r0
	BX       lr
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029846|
	LDR      r1, [pc, #0x18]
	STR      r1, [r0]
|loc_08029846|
	POP      {r3, pc}
	LSL      r4, r3, #8
	LSR      r5, r6, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	ADD      r7, pc, #0x160
	LSR      r4, r0, #0x20
	STR      r7, [sp, #0x2d0]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r1, #0
	LDR      r3, [pc, #0xfc]
	ADD      r2, r4, #0
	LDR      r3, [r3]
	ADD      r2, #0xff
	ADD      r2, #0xa1
	ADD      r3, #0xff
	ADD      r3, #0xa1
	LDMIA    r2!, {r5}
	LDMIA    r3!, {r6}
	LDR      r2, [r2]
	LDR      r3, [r3]
	SUB      sp, #0x10
	SUB      r2, r2, r3
	STR      r2, [sp, #4]
	LDR      r3, [sp, #4]
	SUB      r5, r5, r6
	ADD      r1, r0, #0
	ADD      r1, #8
	STR      r5, [sp]
	STR      r5, [sp, #8]
	STR      r3, [sp, #0xc]
	STMIA    r1!, {r5}
	LDR      r2, [sp, #0xc]
	STR      r2, [r1]
	ADD      r1, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xdd08
	MOV      r0, #0x37
	STRB     r0, [r4, #8]
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r4}
	LDR      r2, [pc, #0xbc]
	ADD      r0, #8
	LDR      r2, [r2]
	LDMIA    r0!, {r4}
	ADD      r2, #0xff
	ADD      r2, #0xa1
	LDMIA    r2!, {r3}
	LDR      r2, [r2]
	LDR      r0, [r0]
	SUB      sp, #0x10
	ADD      r0, r2, r0
	STR      r0, [sp, #4]
	ADD      r3, r3, r4
	LDR      r2, [sp, #4]
	ADD      r1, #0xff
	ADD      r1, #0xa1
	STR      r3, [sp]
	STR      r3, [sp, #8]
	STR      r2, [sp, #0xc]
	STR      r3, [r1]
	ADD      r0, r1, #4
	LDR      r1, [sp, #0xc]
	STR      r1, [r0]
	ADD      sp, #0x10
	POP      {r4}
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080298EE|
	MOV      r1, #3
	STRB     r1, [r0, #4]
	LDR      r1, [pc, #0x7c]
	STR      r1, [r0]
|loc_080298EE|
	ADD      r5, r0, #0
	MOV      r1, #1
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, lr}
	LDR      r0, [pc, #0x64]
	MOV      r5, #0
	LDR      r0, [r0]
	SUB      sp, #0x1c
	CMP      r0, #0
	BEQ      |loc_0802991A|
	MOV      r1, #0xff
	ADD      r1, #0xcd
	LDR      r1, [r1, r0]
	CMP      r1, #0
	BNE      |sub_08029920|
|loc_0802991A|
	MOV      r0, #1
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
|sub_08029920|
|unk_08029920|
		LDR r1, [r0]
		MOV r2, #0x80
		LDR r2, [r2, r1]
		ADD r4, r0, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		ADD r0, #0x16
		MOV r3, #0
		LDRSH r0, [r0, r3]
		CMP r0, #0
		BGT      |loc_0802993C|
		MOV r0, #1
		DCW     0xE7EF
|loc_0802993C|
		LDR r0, [pc, #0x30]
		LDR r0, [r0, #4]
		LSL r0, r0, #0x1a
		BNE      |loc_0802995A|
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x18]
		STR r5, [sp, #0x10]
		LDR r2, [r4]
		ADD r0, r4, #0
		LDR r3, [r2, #0x5c]
		MOV r1, sp
		ADD r2, r3, r2
		BL       |loc_08046AA4|
|loc_0802995A|
		MOV r0, #0
		DCW     0xE7DE
	INCBIN  baserom.gba_0x2995e_0x29962.extracted
|sub_08029962|
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STMIA    r3!, {r2, r4}
	LSR      r4, r0, #0x20
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	CMP      r7, #0xe8
	LSL      r0, r0, #0xc
	MOV      r0, #0x8b
	LSL      r0, r0, #2
	PUSH     {r3, lr}
	ADD      r0, r1, r0
	BL       |inc_0x0158_0x143f2| + 0xa802
	MOV      r0, #0
	POP      {r3, pc}
	MOV      r0, #0x8b
	LSL      r0, r0, #2
	ADD      r0, r1, r0
	PUSH     {r3, lr}
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_080299A0|
	LDR      r2, [r0]
	LDR      r3, [r2, #0xc]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080299A0|
	POP      {r3, pc}
|sub_080299A2|
|unk_080299A2|
	INCBIN	baserom.gba_0x299a2_0x299a6.extracted
|sub_080299A6|
	LSL      r0, r0, #0
	CMP      r7, #0xec
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r4, #0
	LDR      r1, [pc, #0x24]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	ADD      r0, r4, #0
|unk_080299BA|
	INCBIN	baserom.gba_0x299ba_0x299bc.extracted
|loc_080299BC|
|unk_080299BC|
	INCBIN	baserom.gba_0x299bc_0x299be.extracted
	POP      {r4, pc}
|sub_080299C0|
|unk_080299C0|
		MOV r0, #1
		BX       lr
|sub_080299C4|
	LDR      r0, [pc, #0x10]
	ADD      r0, #4
	BX       lr
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [pc, #8]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	MOV      r0, #1
	POP      {r3, pc}
|sub_080299D8|
|unk_080299D8|
	INCBIN	baserom.gba_0x299d8_0x299da.extracted
|sub_080299DA|
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080299FC|
	LDR      r1, [pc, #0x44]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_080299FC|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r6, [r0, #0xc]
	ADD      r5, r0, #0
	ADD      r0, r1, #0
	ADD      r4, r1, #0
	LDR      r1, [r1]
	ADD      r7, r2, #0
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r1, #0xa3
	LSL      r1, r1, #2
	ADD      r1, r4, r1
	MUL      r6, r0
	ASR      r0, r6, #0x10
	LDR      r1, [r1]
	LSL      r0, r0, #0xa
	CMP      r1, r0
	BGE      |sub_08029A36|
	LDR      r0, [r5, #0x10]
	ADD      r2, r7, #0
|loc_08029A2C|
	ADD      r1, r4, #0
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08029A36|
|unk_08029A36|
		MOV r0, #0
		DCW     0xE7FC
|sub_08029A3A|
	LSL      r0, r0, #0
	ADD      r2, sp, #0x2f0
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [r2, #8]
	LDRB     r3, [r0, #0xc]
	LDRB     r5, [r4, #1]
	CMP      r3, r5
	BEQ      |loc_08029A52|
	LDRB     r4, [r4]
	CMP      r3, r4
	BNE      |sub_08029A5C|
|loc_08029A52|
	LDR      r0, [r0, #0x10]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, r4, r5, pc}
|sub_08029A5C|
|unk_08029A5C|
		MOV r0, #0
		DCW     0xE7FC
|sub_08029A60|
	PUSH     {r4, r5, lr}
	LDR      r0, [pc, #0xec]
	ADD      r5, r1, #0
	LDR      r4, [r0]
	SUB      sp, #0x24
	CMP      r4, #0
	BNE      |sub_08029A74|
	MOV      r0, #0
	ADD      sp, #0x24
	POP      {r4, r5, pc}
|sub_08029A74|
|unk_08029A74|
		LDRB r0, [r5, #0x10]
		LDRB r1, [r4, #0x10]
		MOV r2, #1
		EOR r1, r2
		CMP r0, r1
		BEQ      |loc_08029A84|
		MOV r0, #0
		DCW     0xE7F5
|loc_08029A84|
		LDR r0, [r4, #0x14]
		LDR r1, [r0]
		LDR r2, [r1, #0x1c]
		ADD r2, r2, r1
		ADD r1, r4, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_08029A98|
		DCW     0xE7EB
|loc_08029A98|
		ADD r1, r4, #0
		ADD r0, sp, #0x14
		BL       |loc_0800FE78|
		ADD r1, r5, #0
		ADD r0, sp, #4
		BL       |loc_0800FE78|
		LDRB r0, [r4, #0x10]
		CMP r0, #0
		BEQ      |loc_08029AF0|
		CMP r0, #1
		BEQ      |loc_08029B04|
		CMP r0, #2
		BEQ      |loc_08029B18|
		CMP r0, #3
		BNE      |loc_08029ACC|
		LDR r0, [sp, #0x18]
		SUB r0, #4
		STR r0, [sp, #0x18]
		LDR r0, [sp, #0x20]
		ADD r0, #4
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x1c]
		ADD r0, #0xf0
		STR r0, [sp, #0x1c]
|loc_08029ACC|
		LDR r0, [sp, #4]
		LDR r1, [sp, #0x1c]
		CMP r0, r1
		BGE      |loc_08029B2C|
		LDR r0, [sp, #0x14]
		LDR r1, [sp, #0xc]
		CMP r0, r1
		BGE      |loc_08029B2C|
		LDR r0, [sp, #8]
		LDR r1, [sp, #0x20]
		CMP r0, r1
		BGE      |loc_08029B2C|
		LDR r0, [sp, #0x18]
		LDR r1, [sp, #0x10]
		CMP r0, r1
		BGE      |loc_08029B2C|
		MOV r0, #1
		DCW     0xE7BF
|loc_08029AF0|
		LDR r0, [sp, #0x14]
		SUB r0, #4
		STR r0, [sp, #0x14]
		LDR r0, [sp, #0x1c]
		ADD r0, #4
		STR r0, [sp, #0x1c]
		LDR r0, [sp, #0x20]
		ADD r0, #0xf0
		STR r0, [sp, #0x20]
		B        |loc_08029ACC|
|loc_08029B04|
		LDR r0, [sp, #0x14]
		SUB r0, #4
		STR r0, [sp, #0x14]
		LDR r0, [sp, #0x1c]
		ADD r0, #4
		STR r0, [sp, #0x1c]
		LDR r0, [sp, #0x18]
		SUB r0, #0xf0
		STR r0, [sp, #0x18]
		B        |loc_08029ACC|
|loc_08029B18|
		LDR r0, [sp, #0x18]
		SUB r0, #4
		STR r0, [sp, #0x18]
		LDR r0, [sp, #0x20]
		ADD r0, #4
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x14]
		SUB r0, #0xf0
		STR r0, [sp, #0x14]
		B        |loc_08029ACC|
|loc_08029B2C|
		MOV r0, #0
		DCW     0xE79F
|sub_08029B30|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029B4C|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08029B4C|
	POP      {r4, pc}
|sub_08029B4E|
	DCW      0x0000
	DCW      0x1b94,0x0300,0xb6b8
|sub_08029B56|
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x78]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x20
	CMP      r1, #0
	BNE      |sub_08029B6C|
	MOV      r0, #0
	ADD      sp, #0x20
	POP      {r4, pc}
|sub_08029B6C|
|unk_08029B6C|
		LDR r2, [pc, #0x68]
		LDR r0, [r1, #0x14]
		CMP r0, r2
		BEQ      |loc_08029B78|
		MOV r0, #0
		DCW     0xE7F7
|loc_08029B78|
		ADD r0, sp, #0x10
		BL       |loc_0800FE78|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |loc_0800FE78|
		LDR r0, [sp]
		LDR r1, [sp, #4]
		LDR r2, [sp, #8]
		LDR r3, [sp, #0xc]
		LDR r4, [sp, #0x18]
		SUB r0, #8
		SUB r1, #8
		ADD r2, #8
		ADD r3, #8
		CMP r0, r4
		BGE      |loc_08029BB2|
		LDR r0, [sp, #0x10]
		CMP r0, r2
		BGE      |loc_08029BB2|
		LDR r0, [sp, #0x1c]
		CMP r1, r0
		BGE      |loc_08029BB2|
		LDR r0, [sp, #0x14]
		CMP r0, r3
		BGE      |loc_08029BB2|
		MOV r0, #1
		DCW     0xE7DA
|loc_08029BB2|
		MOV r0, #0
		DCW     0xE7D8
|sub_08029BB6|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029BD2|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08029BD2|
	POP      {r4, pc}
|sub_08029BD4|
|unk_08029BD4|
	INCBIN	baserom.gba_0x29bd4_0x29bd6.extracted
|sub_08029BD6|
	LSL      r0, r0, #0xc
	SUB      r0, r2, r5
	LSL      r0, r0, #0xc
|unk_08029BDC|
	INCBIN	baserom.gba_0x29bdc_0x29bde.extracted
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0xa0]
	ADD      r6, r1, #0
	LDR      r1, [r0]
	MOV      r4, #0
	CMP      r1, #0
	SUB      sp, #0x40
	BEQ      |loc_08029C5E|
	ADD      r0, sp, #8
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x10]
	LDR      r2, [sp, #0x14]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0xc]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r1, [sp]
	STR      r1, [sp, #0x18]
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x1c]
	ADD      r0, sp, #0x20
	ADD      r1, r6, #0
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [sp, #0x20]
	LDR      r1, [sp, #0x28]
	LDR      r2, [sp, #0x2c]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x24]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x34]
	ASR      r1, r1, #1
	LDR      r0, [sp, #0x18]
	STR      r1, [sp]
	STR      r1, [sp, #0x30]
	SUB      r1, r0, r1
	LDR      r0, [sp, #0x1c]
	LDR      r2, [sp, #0x34]
	STR      r1, [sp]
	SUB      r0, r0, r2
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x3c]
	ADD      r0, r1, #0
	MUL      r0, r1
	STR      r1, [sp, #0x38]
	LDR      r1, [sp, #0x3c]
	ADD      r2, r1, #0
	MUL      r1, r2
	ADD      r0, r0, r1
	LDR      r1, [r5, #0xc]
	CMP      r0, r1
	BGT      |loc_08029C5E|
	MOV      r4, #1
|loc_08029C5E|
	ADD      r0, r4, #0
	ADD      sp, #0x40
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029C84|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_08029C84|
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	LDR      r4, [sp, #0xa0]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0xa0]
	ADD      r6, r1, #0
	LDR      r1, [r0]
	MOV      r4, #0
	CMP      r1, #0
	SUB      sp, #0x40
	BEQ      |loc_08029D0E|
	ADD      r0, sp, #8
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x10]
	LDR      r2, [sp, #0x14]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0xc]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r1, [sp]
	STR      r1, [sp, #0x18]
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x1c]
	ADD      r0, sp, #0x20
	ADD      r1, r6, #0
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [sp, #0x20]
	LDR      r1, [sp, #0x28]
	LDR      r2, [sp, #0x2c]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x24]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x34]
	ASR      r1, r1, #1
	LDR      r0, [sp, #0x18]
	STR      r1, [sp]
	STR      r1, [sp, #0x30]
	SUB      r1, r0, r1
	LDR      r0, [sp, #0x1c]
	LDR      r2, [sp, #0x34]
	STR      r1, [sp]
	SUB      r0, r0, r2
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x3c]
	ADD      r0, r1, #0
	MUL      r0, r1
	STR      r1, [sp, #0x38]
	LDR      r1, [sp, #0x3c]
	ADD      r2, r1, #0
	MUL      r1, r2
	ADD      r0, r0, r1
	LDR      r1, [r5, #0xc]
	CMP      r0, r1
	BGT      |loc_08029D0E|
	MOV      r4, #1
|loc_08029D0E|
	ADD      r0, r4, #0
	ADD      sp, #0x40
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029D34|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_08029D34|
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	LDR      r4, [sp, #0x100]
	LSR      r4, r0, #0x20
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	MOV      r0, #0x29
	LSL      r0, r0, #4
	ADD      r0, r1, r0
	LDRB     r4, [r0]
	MOV      r0, #1
	ADD      r5, r1, #0
	EOR      r4, r0
	ASR      r6, r4, #1
	ADD      r1, r6, #0
	EOR      r1, r0
	SUB      sp, #0xc
	STR      r1, [sp, #4]
	MOV      r0, #0x40
	BL       |inc_0x03d784_0x041118| + 0x2348
	LDR      r1, [sp, #0xc]
	ADD      r0, #0x60
	LDR      r1, [r1, #0xc]
	LDR      r2, [pc, #0x10c]
	MUL      r0, r1
	LSR      r7, r0, #7
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #4]
	ADD      r0, #4
	STR      r0, [sp, #8]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LSL      r1, r4, #2
	LDR      r1, [r2, r1]
	MUL      r1, r7
	STR      r1, [r0]
	MOV      r0, #1
	LSL      r0, r0, #0xf
	BL       |inc_0x03d784_0x041118| + 0x2348
	MOV      r1, #1
	LSL      r1, r1, #0xe
	SUB      r0, r0, r1
	MUL      r0, r7
	ASR      r1, r0, #0xc
	LDR      r0, [sp, #8]
	LSL      r2, r6, #2
	ADD      r0, r2, r0
	STR      r1, [r0]
	STRB     r4, [r5, #0x10]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	ADD      r0, r1, #0
	ADD      r4, r1, #0
	LDR      r1, [r1]
	SUB      sp, #0x2c
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |sub_08029DCE|
	MOV      r0, #1
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
|sub_08029DCE|
|unk_08029DCE|
		ADD r1, r4, #0
		ADD r5, sp, #0x14
		ADD r0, r5, #0
		BL       |sub_0800FDFA|
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		ADD r2, r6, #4
		STR r2, [sp, #0x24]
		STR r0, [sp, #0x28]
		LDR r1, [r0]
		LDR r3, [r6, #4]
		ADD r7, r2, #4
		ADD r1, r1, r3
		STR r1, [r0]
		LDR r1, [r0, #4]
		LDR r2, [r6, #8]
		ADD r6, sp, #4
		ADD r1, r1, r2
		STR r1, [r0, #4]
		ADD r1, r4, #0
		ADD r0, r6, #0
		BL       |sub_0800FDFA|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x4c]
		ADD r3, r2, r1
		MOV r2, #1
		ADD r1, r5, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x50]
		ADD r2, r2, r1
		ADD r1, r6, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_08029E34|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x4c]
		ADD r3, r2, r1
		MOV r2, #0
		ADD r1, r6, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		B        |loc_08029E58|
|loc_08029E34|
		LDR r0, [sp, #0x28]
		LDR r2, [sp, #0x24]
		LDR r1, [r0]
		LDR r2, [r2]
		SUB r1, r1, r2
		STR r1, [r0]
		LDR r1, [r0, #4]
		LDR r2, [r7]
		SUB r1, r1, r2
		STR r1, [r0, #4]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x4c]
		ADD r3, r2, r1
		MOV r2, #0
		ADD r1, r5, #0
		BL       |inc_0x046118_0x049114| + 0x98e
|loc_08029E58|
		MOV r0, #0
		DCW     0xE7B6
|sub_08029E5C|
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029E70|
	LDR      r1, [pc, #0xc]
	STR      r1, [r0]
	STR      r4, [r0, #0xc]
|loc_08029E70|
	POP      {r4, pc}
	LSL      r0, r0, #0
	LSL      r4, r5, #9
	LSR      r5, r6, #1
	STMIA    r6!, {r6}
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029E9C|
	LDR      r1, [pc, #0x24]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_08029E9C|
	POP      {r3, r4, r5, pc}
	MOV      r3, #0xff
	ADD      r3, #0xe5
	PUSH     {r4, lr}
	LDR      r3, [r3, r1]
	LDR      r4, [r0, #0xc]
	CMP      r3, r4
	BNE      |sub_08029EB6|
	LDR      r0, [r0, #0x10]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r4, pc}
|sub_08029EB6|
|unk_08029EB6|
		MOV r0, #0
		POP {r4, pc}
|sub_08029EBA|
	LSL      r0, r0, #0
	LDMIA    r3!, {r4, r5, r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0x10]
	BX       lr
	ADD      r0, r1, #0
	ADD      r0, #0xff
	ADD      r0, #0xc1
	LDR      r1, [r0, #0x24]
	ADD      r1, #1
	STR      r1, [r0, #0x24]
	MOV      r0, #0
	BX       lr
|sub_08029ED4|
|unk_08029ED4|
	INCBIN	baserom.gba_0x29ed4_0x29ed6.extracted
|sub_08029ED6|
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x128]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x3c
	CMP      r1, #0
	BEQ      |loc_08029EF0|
	MOV      r0, #0xff
	ADD      r0, #0xcd
	LDR      r0, [r0, r1]
	CMP      r0, #0
	BNE      |sub_08029EF6|
|loc_08029EF0|
	MOV      r0, #0
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
|sub_08029EF6|
|unk_08029EF6|
		ADD r0, sp, #0x2c
		BL       |loc_0800FE78|
		ADD r1, r4, #0
		ADD r0, sp, #0x1c
		BL       |loc_0800FE78|
		LDR r0, [sp, #0x1c]
		LDR r1, [sp, #0x24]
		LDR r2, [sp, #0x28]
		ADD r0, r0, r1
		LDR r1, [sp, #0x20]
		STR r0, [sp, #0xc]
		ADD r1, r1, r2
		STR r1, [sp, #0x10]
		ASR r1, r1, #1
		ASR r0, r0, #1
		STR r0, [sp, #0xc]
		STR r0, [sp, #0x14]
		MOV ip, r1
		STR r1, [sp, #0x10]
		STR r1, [sp, #0x18]
		LDR r1, [sp, #0x24]
		LDR r0, [sp, #0x1c]
		LDR r5, [sp, #0x28]
		LDR r2, [sp, #0x34]
		ADD r1, #3
		SUB r0, #4
		SUB r5, #6
		CMP r0, r2
		LDR r6, [sp, #0x20]
		BGE      |loc_08029F48|
		LDR r2, [sp, #0x2c]
		CMP r2, r1
		BGE      |loc_08029F48|
		LDR r2, [sp, #0x38]
		CMP r6, r2
		BGE      |loc_08029F48|
		LDR r2, [sp, #0x30]
		CMP r2, r5
		BLT      |loc_08029F4C|
|loc_08029F48|
		MOV r0, #0
		DCW     0xE7D2
|loc_08029F4C|
		LDR r2, [sp, #0x2c]
		LDR r3, [sp, #0x34]
		LDR r7, [sp, #0x38]
		ADD r3, r2, r3
		LDR r2, [sp, #0x30]
		STR r3, [sp]
		ADD r2, r2, r7
		STR r2, [sp, #4]
		ASR r2, r2, #1
		ASR r3, r3, #1
		STR r2, [sp, #4]
		STR r2, [sp, #0xc]
		ADD r2, r3, #0
		STR r3, [sp]
		STR r3, [sp, #8]
		LDR r3, [sp, #0x14]
		LDR r7, [sp, #0x18]
		SUB r2, r2, r3
		LDR r3, [sp, #0xc]
		STR r2, [sp]
		SUB r7, r3, r7
		ADD r3, r2, #0
		CMP r2, #0
		STR r7, [sp, #4]
		STR r7, [sp, #0x10]
		BGE      |loc_08029F82|
		NEG r3, r2
|loc_08029F82|
		LDR r7, [sp, #0x10]
		CMP r7, #0
		BGE      |loc_08029F8A|
		NEG r7, r7
|loc_08029F8A|
		CMP r3, r7
		BLE      |loc_08029FA8|
		LDR r5, [sp, #0x28]
		MOV r6, ip
		ADD r5, #3
		CMP r2, #0
		BLE      |loc_08029FA0|
		MOV r0, #3
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x14]
		B        |loc_08029FC6|
|loc_08029FA0|
		MOV r1, #2
		STRB r1, [r4, #0x10]
		LDR r1, [sp, #0x14]
		B        |loc_08029FC6|
|loc_08029FA8|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |sub_0800FDFA|
		LDR r7, [sp, #0x10]
		LDR r0, [sp]
		LDR r1, [sp, #8]
		CMP r7, #0
		BLE      |loc_08029FC0|
		MOV r2, #0
		STRB r2, [r4, #0x10]
		B        |loc_08029FC6|
|loc_08029FC0|
		MOV r2, #1
		STRB r2, [r4, #0x10]
		LDR r5, [sp, #4]
|loc_08029FC6|
		LDR r2, [sp, #0x34]
		CMP r0, r2
		BGE      |loc_08029FE2|
		LDR r0, [sp, #0x2c]
		CMP r0, r1
		BGE      |loc_08029FE2|
		LDR r0, [sp, #0x38]
		CMP r6, r0
		BGE      |loc_08029FE2|
		LDR r0, [sp, #0x30]
		CMP r0, r5
		BGE      |loc_08029FE2|
		MOV r0, #1
		DCW     0xE787
|loc_08029FE2|
		MOV r0, #0
		DCW     0xE785
|sub_08029FE6|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802A002|
	LDR      r1, [pc, #8]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0802A002|
	POP      {r4, pc}
|sub_0802A004|
|unk_0802A004|
	INCBIN	baserom.gba_0x2a004_0x2a006.extracted
|sub_0802A006|
	LSL      r0, r0, #0xc
	LDR      r5, [sp, #0x3c0]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xac]
	PUSH     {r4, lr}
	LDR      r3, [r2]
	CMP      r3, #0
	BEQ      |loc_0802A026|
	ADD      r3, #0xff
	ADD      r3, #0xa1
	LDMIA    r3!, {r4}
	STR      r4, [r0, #0x1c]
	LDR      r3, [r3]
	STR      r3, [r0, #0x20]
	BL       |inc_0x351c0_0x3d4d0| + 0x6940
|loc_0802A026|
	POP      {r4, pc}
	LDR      r2, [pc, #0x90]
	PUSH     {r4, r5, lr}
	LDR      r2, [r2]
	SUB      sp, #0x1c
	CMP      r2, #0
	BNE      |sub_0802A03A|
	MOV      r0, #0
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
|sub_0802A03A|
|unk_0802A03A|
		ADD r2, #0xff
		ADD r2, #0xa1
		LDMIA r2!, {r4}
		ADD r3, r0, #0
		STR r4, [r0, #0x1c]
		LDR r2, [r2]
		ADD r3, #0x1c
		STR r2, [r0, #0x20]
		ADD r2, r1, #0
		ADD r2, #0xff
		ADD r2, #0xa1
		ADD r4, r3, #4
		LDR r3, [r0, #0x1c]
		LDMIA r2!, {r5}
		LDR r4, [r4]
		LDR r2, [r2]
		SUB r3, r3, r5
		SUB r2, r4, r2
		STR r2, [sp, #8]
		ADD r2, r3, #0
		STR r3, [sp, #4]
		LDR r3, [sp, #8]
		STR r2, [sp, #0xc]
		STR r3, [sp, #0x10]
		STR r3, [sp, #0x18]
		ADD r3, r2, #0
		STR r2, [sp, #0x14]
		MUL r2, r3
		ASR r3, r2, #8
		LDR r2, [sp, #0x18]
		ADD r4, r2, #0
		MUL r2, r4
		ASR r2, r2, #8
		ADD r3, r3, r2
		MOV r2, #1
		LSL r2, r2, #0xa
		CMP r3, r2
		DCW     0xDC08
		ADD r0, r1, #0
		LDR r1, [r1]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #0
		DCW     0xE7CE
	INCBIN  baserom.gba_0x2a098_0x2a09a.extracted
|sub_0802A09A|
|unk_0802A09A|
	INCBIN	baserom.gba_0x2a09a_0x2a09e.extracted
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802A0BA|
	MOV      r1, #0x32
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	MOV      r1, #0
	STR      r1, [r0, #0x14]
	LDR      r1, [pc, #8]
	STR      r1, [r0]
|loc_0802A0BA|
	POP      {r4, pc}
|sub_0802A0BC|
|unk_0802A0BC|
; cited by 0x0802A00C (a pc-relative load targets 0x0802A0BC)
		DCD     0x03001C34
		DCD     0x08049DA8
		PUSH {r0, r1, r4, r5, r6, r7, lr}
		LDR r0, [pc, #0x208]
		MOV r7, #0
		LDR r5, [r0]
		ADD r4, r1, #0
		CMP r5, #0
		SUB sp, #0x6c
		BEQ      |loc_0802A1B8|
		MOV r0, #0xff
		ADD r0, #0xcd
		LDR r0, [r0, r5]
		CMP r0, #0
		BEQ      |loc_0802A1B8|
		ADD r1, r5, #0
		ADD r0, sp, #0x5c
		BL       |loc_0800FE78|
		ADD r1, r4, #0
		ADD r0, sp, #0x4c
		BL       |loc_0800FE78|
		LDR r0, [sp, #0x4c]
		LDR r1, [sp, #0x54]
		LDR r2, [sp, #0x58]
		ADD r0, r0, r1
		LDR r1, [sp, #0x50]
		STR r0, [sp, #0x3c]
		ADD r1, r1, r2
		ASR r0, r0, #1
		ASR r3, r1, #1
		STR r0, [sp, #0x44]
		STR r0, [sp, #0x3c]
		STR r1, [sp, #0x40]
		LDR r1, [sp, #0x64]
		LDR r0, [sp, #0x5c]
		STR r3, [sp, #0x40]
		ADD r1, r0, r1
		LDR r0, [sp, #0x60]
		STR r3, [sp, #0x48]
		LDR r2, [sp, #0x68]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r0, [sp, #4]
		STR r0, [sp, #0xc]
		ADD r0, r1, #0
		STR r1, [sp]
		STR r1, [sp, #8]
		LDR r1, [sp, #0x44]
		LDR r2, [sp, #0x48]
		SUB r0, r0, r1
		LDR r1, [sp, #0xc]
		STR r0, [sp]
		SUB r6, r1, r2
		ADD r1, r0, #0
		CMP r0, #0
		STR r6, [sp, #4]
		BGE      |loc_0802A13E|
		NEG r1, r0
|loc_0802A13E|
		ADD r2, r6, #0
		CMP r6, #0
		BGE      |loc_0802A146|
		NEG r2, r2
|loc_0802A146|
		CMP r1, r2
		BLE      |loc_0802A176|
		STR r3, [sp, #0x18]
		LDR r1, [sp, #0x58]
		ADD r1, #3
		STR r1, [sp, #0x20]
		CMP r0, #0
		BLE      |loc_0802A166|
		MOV r0, #3
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x44]
		STR r0, [sp, #0x14]
		LDR r0, [sp, #0x54]
		ADD r0, #3
		STR r0, [sp, #0x1c]
		B        |loc_0802A1A4|
|loc_0802A166|
		MOV r0, #2
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x4c]
		SUB r0, #4
		STR r0, [sp, #0x14]
		LDR r0, [sp, #0x44]
		STR r0, [sp, #0x1c]
		B        |loc_0802A1A4|
|loc_0802A176|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |sub_0800FDFA|
		LDR r0, [sp]
		CMP r6, #0
		STR r0, [sp, #0x14]
		LDR r0, [sp, #8]
		STR r0, [sp, #0x1c]
		BLE      |loc_0802A198|
		STRB r7, [r4, #0x10]
		LDR r0, [sp, #0x50]
		STR r0, [sp, #0x18]
		LDR r0, [sp, #0x58]
		SUB r0, #6
		STR r0, [sp, #0x20]
		B        |loc_0802A1A4|
|loc_0802A198|
		MOV r0, #1
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x50]
		STR r0, [sp, #0x18]
		LDR r0, [sp, #4]
		STR r0, [sp, #0x20]
|loc_0802A1A4|
		STR r4, [sp, #0x30]
		LDRB r0, [r4, #0x10]
		ADD r3, sp, #0x20
		ADD r2, sp, #0x10
		STRB r0, [r3, #4]
		LDR r0, [pc, #0x124]
		STR r0, [sp, #0x2c]
		MOV r0, #1
		LSL r0, r0, #0xa
		B        |loc_0802A1BA|
|loc_0802A1B8|
		DCW     0xE05B
|loc_0802A1BA|
		STR r0, [sp, #0x28]
		ADD r3, sp, #0
		STRB r7, [r3, #0x10]
		STR r4, [sp, #0x40]
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r3, [r1, #0x24]
		ADD r3, r3, r1
		MOV r1, #0
		BL       |inc_0x042118_0x049114| + 0x498e
		CMP r0, #0
		DCW     0xD041
		MOV r0, #0x60
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		LDR r2, [pc, #0xfc]
		LDR r1, [pc, #0xf8]
		LDR r2, [r2]
		ADD r6, r2, r1
		CMP r0, r5
		BEQ      |loc_0802A1FC|
		MOV r0, #0xe5
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BEQ      |loc_0802A1FC|
		MOV r0, #0xdc
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BNE      |loc_0802A20A|
|loc_0802A1FC|
		ADD r3, r7, #0
		MOV r2, #0x40
		ADD r0, r6, #0
		LDR r1, [pc, #0xdc]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		DCW     0xE026
|loc_0802A20A|
		MOV r0, #0xee
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BEQ      |loc_0802A228|
		MOV r0, #0xf4
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BEQ      |loc_0802A228|
		MOV r0, #0xed
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		DCW     0xD109
|loc_0802A228|
		MOV r0, #0x5d
		LDR r1, [pc, #0xb8]
		LSL r0, r0, #3
		ADD r1, r0, r1
		ADD r3, r7, #0
		MOV r2, #0x40
		ADD r0, r6, #0
	INCBIN  baserom.gba_0x2a236_0x2a238.extracted
|sub_0802A238|
|unk_0802A238|
	INCBIN	baserom.gba_0x2a238_0x2a23c.extracted
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r0, #0x30
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0x98]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	ADD      r3, r7, #0
	MOV      r2, #0x40
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [sp, #0x6c]
	LDR      r0, [r0, #4]
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r0, #4
	LSL      r1, r0, #0x18
	LDR      r0, [r4]
	LSR      r1, r1, #0x18
	LDR      r2, [r0, #0x28]
	ADD      r2, r2, r0
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x74
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4, lr}
	LDR      r0, [r1, #0x58]
	MOV      r4, #3
	LDRB     r1, [r0]
	CMP      r1, #6
	BLS      |loc_0802A29A|
	LDR      r2, [r0, #0x6c]
	CMP      r2, #0
	BNE      |loc_0802A29C|
|loc_0802A29A|
	MOV      r4, #2
|loc_0802A29C|
	CMP      r4, #2
	BLT      |loc_0802A2AC|
	CMP      r1, #5
	BLS      |loc_0802A2AA|
	LDR      r2, [r0, #0x68]
	CMP      r2, #0
	BNE      |loc_0802A2AC|
|loc_0802A2AA|
	MOV      r4, #1
|loc_0802A2AC|
	CMP      r4, #1
	BLT      |loc_0802A2BC|
	CMP      r1, #4
	BLS      |loc_0802A2BA|
	LDR      r0, [r0, #0x64]
	CMP      r0, #0
	BNE      |loc_0802A2BC|
|loc_0802A2BA|
	MOV      r4, #0
|loc_0802A2BC|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802A2CC|
	LDR      r1, [pc, #0x20]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0802A2CC|
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	STRH     r0, [r3, #4]
	LSR      r3, r5, #1
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LSL      r0, r1, #0xa
	LSR      r5, r6, #1
	STR      r4, [sp, #0x40]
	LSR      r1, r6, #0x20
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	STR      r7, [sp, #0x310]
	LSR      r4, r0, #0x20
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_0802A30A|
	MOV      r0, #0x50
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802A30A|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_0802A30A|
|unk_0802A30A|
		LDR r0, [pc, #0x274]
		LDR r7, [pc, #0x274]
		STR r0, [r4]
		MOV r0, #0x80
		STRH r0, [r4, #0xe]
		LDR r0, [r7, #4]
		MOV r1, #0x80
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0802A330|
		MOV r1, #0x80
		LDR r0, [r7, #4]
		BL       |sub_08011732|
		MOV r1, #0x80
		LDR r0, [r7, #4]
		BL       |loc_0801124C|
|loc_0802A330|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x254]
		STR r0, [r4]
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x28]
		STR r2, [r4, #0x2c]
		MOV r2, #0
		STR r2, [r4, #0x1c]
		MOV r1, #0x38
		STRB r1, [r4, #8]
		SUB r5, #8
		LDR r1, [r5, #4]
		ADD r0, r4, #0
		ADD r0, #0x28
		CMP r6, #0
		STR r1, [r4, #4]
		BNE      |loc_0802A358|
		LDR r1, [r5, #4]
		ADD r1, #0x2c
		STR r1, [r4, #4]
|loc_0802A358|
		LDR r1, [sp, #0x10]
		STR r1, [r4, #0x4c]
		STR r2, [r4, #0x14]
		STRB r2, [r4, #0x10]
		MOV r1, #8
		STR r1, [r4, #0x40]
		MOV r1, #0
		MVN r1, r1
		STR r1, [r4, #0x18]
		STR r6, [r4, #0x44]
		LDMIA r5!, {r1, r3}
		STMIA r0!, {r1, r3}
		SUB r5, #8
		LDMIA r5!, {r1, r3}
		STR r1, [r4, #0x20]
		STR r3, [r4, #0x24]
		LDR r0, [r4, #0x44]
		LDR r3, [pc, #0x210]
		LSL r1, r0, #3
		ADD r1, r1, r0
		LSL r1, r1, #2
		ADD r1, r1, r3
		STR r1, [r4, #0x48]
		LDR r1, [pc, #0x208]
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [r0]
		LDR r0, [r0, #4]
		ADD r3, r2, #0
		STR r0, [r4, #0x3c]
		STR r1, [r4, #0x38]
		LDR r0, [r7]
		LDR r5, [pc, #0x1fc]
		MOV r2, #0x40
		ADD r0, r0, r5
		LDR r1, [pc, #0x1f4]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		DCW     0xE7AE
|sub_0802A3A8|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1d0]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x1e4]
	CMP      r1, r0
	BEQ      |loc_0802A3C2|
	LDR      r0, [pc, #0x1c8]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0802A3C2|
	LDR      r0, [pc, #0x1dc]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0802A3D0|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0802A3D0|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0, #0x10]
	SUB      sp, #0x4c
	CMP      r0, #0
	BEQ      |sub_0802A412|
	CMP      r0, #1
	BNE      |loc_0802A4C8|
	LDR      r0, [r4, #0x38]
	LDR      r1, [r4, #0x3c]
	LSL      r0, r0, #2
	LSL      r1, r1, #2
	STR      r1, [sp, #0x48]
	STR      r0, [sp, #0x44]
	LDR      r2, [r4, #0x20]
	ADD      r0, r2, r0
	STR      r0, [r4, #0x20]
	LDR      r0, [r4, #0x24]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x40]
	SUB      r0, #4
	STR      r0, [r4, #0x40]
	CMP      r0, #0
	BGT      |loc_0802A4C8|
	LDR      r6, [pc, #0x17c]
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
|sub_0802A412|
|unk_0802A412|
		CMP r1, #0
		BEQ      |loc_0802A4C8|
		LDR r0, [r4, #0x40]
		LDR r1, [r4, #0x38]
		LDR r2, [r4, #0x3c]
		MUL r1, r0
		MUL r2, r0
		ADD r0, r1, #0
		STR r1, [sp, #0x3c]
		ADD r1, r2, #0
		STR r2, [sp, #0x40]
		LDR r2, [r4, #0x20]
		ADD r3, sp, #0x20
		ADD r0, r2, r0
		LDR r2, [r4, #0x24]
		STR r0, [sp, #0x3c]
		ADD r1, r2, r1
		STR r1, [sp, #0x40]
		STR r1, [sp, #0x48]
		STR r0, [sp, #0x44]
		LDR r0, [r4, #0x4c]
		MOV r5, #1
		STR r0, [sp, #0x30]
		LDR r0, [r4, #0x44]
		ADD r2, sp, #0x44
		STRB r0, [r3, #4]
		LDR r0, [pc, #0x15c]
		ADD r3, sp, #0
		STR r0, [sp, #0x2c]
		LSL r0, r5, #0xa
		STR r0, [sp, #0x28]
		MOV r0, #0
		STRB r0, [r3, #0x10]
		STR r4, [sp, #0x40]
		LDR r0, [sp, #0x44]
		LDR r1, [r4, #0x20]
		ADD r3, r4, #0
		ADD r3, #0x20
		CMP r0, r1
		BGE      |loc_0802A466|
		ADD r0, r2, #0
		B        |loc_0802A468|
|loc_0802A466|
		ADD r0, r3, #0
|loc_0802A468|
		LDR r0, [r0]
		LDR r6, [sp, #0x48]
		SUB r0, #4
		STR r0, [sp, #0x14]
		ADD r0, r4, #0
		LDR r7, [r4, #0x24]
		ADD r0, #0x24
		ADD r1, r2, #4
		CMP r6, r7
		BGE      |loc_0802A480|
		ADD r6, r1, #0
		B        |loc_0802A482|
|loc_0802A480|
		ADD r6, r0, #0
|loc_0802A482|
		LDR r6, [r6]
		SUB r6, #4
		STR r6, [sp, #0x18]
		LDR r6, [sp, #0x44]
		LDR r7, [r3]
		CMP r6, r7
		BLE      |loc_0802A492|
		ADD r3, r2, #0
|loc_0802A492|
		LDR r3, [r3]
		LDR r2, [sp, #0x48]
		ADD r3, #4
		STR r3, [sp, #0x1c]
		LDR r3, [r0]
		CMP r2, r3
		BLE      |loc_0802A4A2|
		ADD r0, r1, #0
|loc_0802A4A2|
		LDR r0, [r0]
		LDR r6, [pc, #0xdc]
		ADD r0, #4
		STR r0, [sp, #0x20]
		LDR r1, [r6, #8]
		ADD r7, sp, #0x10
		ADD r0, r7, #4
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		DCW     0xD03E
		ADD r2, r7, #0
		MOV r1, #0
		LDR r0, [r6, #4]
		BL       |loc_08011C0C|
		DCW     0xE000
|loc_0802A4C8|
|unk_0802A4C8|
		B        |loc_0802A53C|
		CMP r0, #0
		BEQ      |loc_0802A508|
		LDR r0, [r6, #4]
		BL       |loc_080116FC|
		MOV r6, #1
		LSL r6, r6, #0xa
		CMP r0, r6
		BLT      |loc_0802A504|
		LSL r7, r6, #2
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0x2348
		MOV r2, #0x37
		ADD r0, r0, r7
		STR r0, [sp]
		STR r2, [sp, #8]
		MOV r3, #4
		MOV r0, #0
		LDR r2, [pc, #0xb4]
		STR r6, [sp, #4]
		ADD r1, sp, #0x44
		BL       |loc_0802A81C|
		LDR r6, [pc, #0x88]
		ADD r1, r0, #0
		LDR r0, [r6, #4]
		BL       |sub_0801191A|
|loc_0802A504|
		STRB r5, [r4, #0x10]
		B        |loc_0802A53C|
|loc_0802A508|
		LDR r0, [r4, #0x40]
		CMP r0, #0x30
		BGE      |loc_0802A514|
		ADD r0, #4
		STR r0, [r4, #0x40]
		B        |loc_0802A52C|
|loc_0802A514|
		LDR r0, [r4, #0x38]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #2
		LSL r1, r1, #2
		STR r1, [sp, #0xc]
		STR r0, [sp, #8]
		LDR r2, [r4, #0x20]
		ADD r0, r2, r0
		STR r0, [r4, #0x20]
		LDR r0, [r4, #0x24]
		ADD r0, r0, r1
		STR r0, [r4, #0x24]
|loc_0802A52C|
		LDR r0, [r4, #0x1c]
		ADD r0, #1
		STR r0, [r4, #0x1c]
		CMP r0, #0xf0
		BLE      |loc_0802A53C|
		STRB r5, [r4, #0x10]
		B        |loc_0802A53C|
		STRB r5, [r4, #0x10]
|loc_0802A53C|
		LDR r0, [r4, #0x14]
		ADD r0, #1
		ASR r2, r0, #2
		STR r0, [r4, #0x14]
		LDR r0, [r4, #0x18]
		CMP r0, r2
		BNE      |loc_0802A54C|
		DCW     0xE760
|loc_0802A54C|
|unk_0802A54C|
; cited by 0x0802A30A (a pc-relative load targets 0x0802A580)
		STR r2, [r4, #0x18]
		LDRH r0, [r4, #0xc]
		LSL r2, r2, #0x1f
		LSR r2, r2, #0x1f
		LSL r3, r2, #1
		LDR r5, [pc, #0x54]
		ADD r2, r3, r2
		LDR r1, [r4, #0x48]
		LSL r0, r0, #5
		ADD r0, r0, r5
		LSL r2, r2, #2
		ADD r1, r1, r2
		LDR r1, [r1, #8]
		MOV r2, #0x40
		BL       |sub_08049138|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x48]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, #0x40
		MOV r2, #0x40
		LDR r1, [r1, #0x20]
		BL       |sub_08049138|
		DCW     0xE746
	INCBIN  baserom.gba_0x2a580_0x2a5a2.extracted
|sub_0802A5A2|
	LSR      r4, r0, #0x20
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	BLS      |loc_0802A54C|
	LSR      r7, r5, #1
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4}
	LDR      r1, [pc, #0x1e8]
	LDR      r3, [r0, #0x20]
	LDR      r1, [r1, #8]
	ADD      r2, r0, #0
	ADD      r1, #0x18
	LDR      r4, [r1]
	LDR      r0, [r0, #0x24]
	LDR      r1, [r1, #4]
	SUB      r3, r3, r4
	ADD      r2, #0x30
	SUB      sp, #8
	SUB      r0, r0, r1
	STR      r0, [sp, #4]
	LDR      r1, [sp, #4]
	STR      r3, [sp]
	STR      r1, [r2, #4]
	STR      r3, [r2]
	ADD      sp, #8
	POP      {r4}
	MOV      r0, #1
	BX       lr
|loc_0802A5EC|
	PUSH     {r4, r5, r6, r7}
	MOV      ip, r3
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r5, [sp, #0x10]
	LDR      r4, [r0, #0x48]
	LSL      r1, r1, #2
	ADD      r1, r4, r1
	MOV      r3, #0
	LDRSB    r6, [r1, r3]
	LDR      r4, [r0, #0x30]
	ADD      r3, r4, r6
	LDR      r4, [r5]
	LDR      r6, [r0, #0x34]
	ADD      r4, r3, r4
	MOV      r3, #1
	LDRSB    r7, [r1, r3]
	LDR      r5, [r5, #4]
	ADD      r3, r6, r7
	ADD      r3, r3, r5
	LDR      r7, [pc, #0x194]
	LDRB     r5, [r1, #2]
	LDRB     r6, [r1, #3]
	ADD      r7, #0x14
	LDR      r7, [r7, #8]
	ADD      r5, r4, r5
	ADD      r6, r3, r6
	CMP      r4, r7
	BGE      |loc_0802A696|
	LDR      r7, [pc, #0x184]
	ADD      r7, #0x14
	LDR      r7, [r7]
	CMP      r7, r5
	BGE      |loc_0802A696|
	LDR      r5, [pc, #0x178]
	ADD      r5, #0x14
	LDR      r7, [r5, #0xc]
	CMP      r3, r7
	BGE      |loc_0802A696|
	LDR      r5, [r5, #4]
	CMP      r5, r6
	BGE      |loc_0802A696|
	LDR      r5, [r2]
	LDR      r1, [r1, #4]
	LDR      r6, [pc, #0x168]
	STR      r1, [r5]
	LDR      r1, [r2]
	LSL      r4, r4, #0x17
	LDR      r5, [r1]
	LSR      r4, r4, #7
	AND      r5, r6
	ORR      r4, r5
	STR      r4, [r1]
	LSR      r4, r4, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r4, r4, #8
	LDR      r1, [r2]
	ORR      r3, r4
	STR      r3, [r1]
	LDRH     r1, [r0, #0xc]
	ADD      r3, r1, #0
	LDR      r1, [r2]
	ADD      r3, ip
	ADD      r1, #4
	LDR      r4, [r1]
	LSL      r3, r3, #0x16
	LSR      r4, r4, #0xa
	LSL      r4, r4, #0xa
	LSR      r3, r3, #0x16
	ORR      r3, r4
	STR      r3, [r1]
	LDRB     r0, [r0, #8]
	MOV      r4, #3
	LSL      r4, r4, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r3, r4
	LDR      r1, [r2]
	ORR      r0, r3
	STR      r0, [r1, #4]
	LDR      r0, [r2]
	ADD      r0, #8
	STR      r0, [r2]
|loc_0802A696|
	POP      {r4, r5, r6, r7}
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0x14
	STR      r0, [sp, #0x10]
	LDR      r0, [r4, #0x40]
	ADD      r6, r1, #0
	CMP      r0, #0x30
	ADD      r7, sp, #0x10
	BGE      |loc_0802A6C6|
	LDRB     r0, [r4, #0x10]
	CMP      r0, #0
	BNE      |loc_0802A6C6|
	LDR      r2, [pc, #0xf4]
	MOV      r3, #0
	ADD      r2, #0xc
	STR      r2, [sp]
	ADD      r2, r7, #0
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |loc_0802A5EC|
|loc_0802A6C6|
	LDR      r0, [r4, #0x40]
	MOV      r5, #0
	SUB      r0, #1
	CMP      r0, #0
	BLE      |loc_0802A6FA|
|loc_0802A6D0|
	LDR      r0, [r4, #0x38]
	LDR      r1, [r4, #0x3c]
	MUL      r0, r5
	MUL      r1, r5
	STR      r0, [sp]
	ADD      r2, sp, #8
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	MOV      r1, #2
	ADD      r2, r7, #0
	STR      r0, [sp, #8]
	MOV      r3, #2
	ADD      r0, r4, #0
	BL       |loc_0802A5EC|
	LDR      r0, [r4, #0x40]
	ADD      r5, #8
	SUB      r0, #1
	CMP      r0, r5
	BGT      |loc_0802A6D0|
|loc_0802A6FA|
	LDR      r0, [sp, #0x10]
	STR      r0, [r6]
	ADD      sp, #0x14
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	ADD      r3, r1, #0
	ADD      r1, r2, #0
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0xc
	CMP      r3, #0
	BEQ      |sub_0802A72A|
	CMP      r3, #0xb
	BEQ      |loc_0802A792|
	CMP      r3, #0xc
	BNE      |loc_0802A79C|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_0802A72A|
|unk_0802A72A|
		LDR r2, [r1, #0x30]
		CMP r2, r0
		BNE      |loc_0802A734|
		MOV r0, #0
		DCW     0xE7F8
|loc_0802A734|
		LDRB r2, [r1, #0x14]
		LDR r3, [r0, #0x44]
		MOV r7, #1
		EOR r3, r7
		CMP r2, r3
		BEQ      |loc_0802A744|
		MOV r0, #0
		DCW     0xE7F0
|loc_0802A744|
		LDR r2, [r0, #0x40]
		LDR r3, [r0, #0x38]
		LDR r4, [r0, #0x3c]
		MUL r3, r2
		MUL r4, r2
		ADD r2, r3, #0
		STR r3, [sp, #4]
		ADD r3, r4, #0
		STR r4, [sp, #8]
		LDR r4, [r0, #0x20]
		ADD r1, #4
		ADD r2, r4, r2
		LDR r4, [r0, #0x24]
		STR r2, [sp, #4]
		ADD r3, r4, r3
		STR r3, [sp, #8]
		ADD r5, r3, #0
		ADD r4, r2, #0
		LDR r6, [r1]
		ADD r4, #0xc
		SUB r2, #0xc
		ADD r5, #0xc
		SUB r3, #0xc
		CMP r6, r4
		BGE      |loc_0802A78E|
		LDR r4, [r1, #8]
		CMP r2, r4
		BGE      |loc_0802A78E|
		LDR r2, [r1, #4]
		CMP r2, r5
		BGE      |loc_0802A78E|
		LDR r1, [r1, #0xc]
		CMP r3, r1
		BGE      |loc_0802A78E|
		STRB r7, [r0, #0x10]
		MOV r0, #1
		DCW     0xE7CB
|loc_0802A78E|
		MOV r0, #0
		DCW     0xE7C9
|loc_0802A792|
|unk_0802A792|
		MOV r1, #0
		MVN r1, r1
		STR r1, [r0, #0x18]
		MOV r0, #0
		DCW     0xE7C4
|loc_0802A79C|
|unk_0802A79C|
		MOV r0, #0
		DCW     0xE7C2
|sub_0802A7A0|
	CMP      r1, #3
	BLT      |sub_0802A7A8|
	MOV      r0, #1
	BX       lr
|sub_0802A7A8|
|unk_0802A7A8|
; cited by 0x0802A5C2 (a pc-relative load targets 0x0802A7AC)
		MOV r0, #0
		BX       lr
	INCBIN  baserom.gba_0x2a7ac_0x2a7b2.extracted
|sub_0802A7B2|
|unk_0802A7B2|
	INCBIN  baserom.gba_0x2a7b2_0x2a7b4.extracted
		PUSH {r4, lr}
	ADD      r4, r0, #0
	LDR      r1, [r4, #0x40]
	LDR      r0, [r0, #0x38]
	ADD      r1, r0, r1
	STR      r1, [r4, #0x38]
	LSR      r0, r1, #0x10
	BEQ      |loc_0802A7EA|
	ASR      r1, r1, #0x10
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r0, [r4, #0x34]
	LSL      r1, r1, #2
	ADD      r1, r0, r1
	STR      r1, [r4, #0x34]
	LDR      r0, [r4, #0x44]
	LDR      r2, [r4, #0x3c]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LSL      r2, r2, #2
	ADD      r2, r0, r2
	CMP      r2, r1
	BHI      |loc_0802A7E4|
	STR      r0, [r4, #0x34]
|loc_0802A7E4|
	ADD      r0, r4, #0
	BL       |loc_0802A7F4|
|loc_0802A7EA|
	LDR      r0, [r4, #0x38]
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STR      r0, [r4, #0x38]
	POP      {r4, pc}
|loc_0802A7F4|
	PUSH     {r4, r5}
	LDR      r1, [r0, #0x34]
	MOV      r3, #0
	LDRSB    r4, [r1, r3]
	LDR      r2, [r0, #0x10]
	MOV      r3, #1
	SUB      r2, r2, r4
	STR      r2, [r0, #0x20]
	LDRSB    r5, [r1, r3]
	LDR      r4, [r0, #0x14]
	SUB      r4, r4, r5
	STR      r4, [r0, #0x24]
	LDRB     r3, [r1, #2]
	LDRB     r1, [r1, #3]
	ADD      r2, r2, r3
	ADD      r1, r4, r1
	STR      r1, [r0, #0x2c]
	STR      r2, [r0, #0x28]
	POP      {r4, r5}
	BX       lr
|loc_0802A81C|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	LDR      r5, [sp, #0x2c]
	LDR      r6, [sp, #0x30]
	LDR      r7, [sp, #0x28]
	ADD      r4, r0, #0
	BNE      |sub_0802A83A|
	MOV      r0, #0x44
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802A83A|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_0802A83A|
|unk_0802A83A|
		LDR r0, [pc, #0x1bc]
		ADD r1, r5, #0
		STR r0, [r4]
		LDR r0, [pc, #0x1b8]
		STRH r5, [r4, #0xe]
		LDR r0, [r0]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0802A862|
		LDR r0, [pc, #0x1ac]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |sub_08011732|
		LDR r0, [pc, #0x1a0]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |loc_0801124C|
|loc_0802A862|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x198]
		MOV r3, #0
		STR r0, [r4]
		LDR r1, [sp, #8]
		LDR r2, [r1]
		LDR r1, [r1, #4]
		STR r1, [r4, #0x14]
		STR r2, [r4, #0x10]
		LDR r0, [sp, #0xc]
		STR r0, [r4, #0x34]
		LDR r1, [sp, #0x10]
		STR r1, [r4, #0x3c]
		STR r7, [r4, #0x40]
		MOV r1, #0
		STR r1, [r4, #0x38]
		STR r1, [r4, #0x30]
		STRB r6, [r4, #8]
		LDR r2, [r4, #0x14]
		STR r2, [r4, #4]
		LDRSB r5, [r0, r3]
		LDR r1, [r4, #0x10]
		MOV r3, #1
		SUB r1, r1, r5
		STR r1, [r4, #0x20]
		LDRSB r5, [r0, r3]
		SUB r3, r2, r5
		STR r3, [r4, #0x24]
		LDRB r2, [r0, #2]
		LDRB r0, [r0, #3]
		ADD r1, r1, r2
		ADD r0, r3, r0
		STR r0, [r4, #0x2c]
		STR r1, [r4, #0x28]
		ADD r0, r4, #0
		DCW     0xE7C5
|sub_0802A8AA|
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0, #0x38]
	LDR      r2, [r0, #0x40]
	ADD      r2, r1, r2
	STR      r2, [r0, #0x38]
	LSR      r1, r2, #0x10
	BEQ      |loc_0802A8FC|
	ASR      r4, r2, #0x10
	LSL      r3, r4, #1
	ADD      r3, r3, r4
	LDR      r1, [r0, #0x34]
	LSL      r3, r3, #2
	ADD      r1, r1, r3
	STR      r1, [r0, #0x34]
	LDR      r3, [r0, #0x3c]
	SUB      r3, r3, r4
	STR      r3, [r0, #0x3c]
	CMP      r3, #0
	BGT      |loc_0802A8DC|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x128]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	POP      {r4, r5, r6, pc}
|loc_0802A8DC|
	MOV      r3, #0
	LDRSB    r5, [r1, r3]
	LDR      r4, [r0, #0x10]
	MOV      r3, #1
	SUB      r4, r4, r5
	STR      r4, [r0, #0x20]
	LDRSB    r6, [r1, r3]
	LDR      r5, [r0, #0x14]
	SUB      r5, r5, r6
	STR      r5, [r0, #0x24]
	LDRB     r3, [r1, #2]
	LDRB     r1, [r1, #3]
	ADD      r3, r4, r3
	ADD      r1, r5, r1
	STR      r1, [r0, #0x2c]
	STR      r3, [r0, #0x28]
|loc_0802A8FC|
	LSL      r1, r2, #0x10
	LSR      r1, r1, #0x10
	STR      r1, [r0, #0x38]
	POP      {r4, r5, r6, pc}
	LDR      r1, [pc, #0xf4]
	PUSH     {r4, r5}
	LDR      r1, [r1, #4]
	LDR      r3, [r0, #0x20]
	ADD      r1, #0x18
	LDR      r4, [r1]
	SUB      sp, #8
	SUB      r3, r3, r4
	LDR      r4, [r0, #0x24]
	LDR      r5, [r1, #4]
	ADD      r2, r0, #0
	SUB      r4, r4, r5
	STR      r4, [sp, #4]
	ADD      r2, #0x18
	STR      r3, [sp]
	STMIA    r2!, {r3, r4}
	LDR      r2, [r0, #0x20]
	LDR      r3, [r1, #8]
	CMP      r2, r3
	BGE      |sub_0802A94C|
	LDR      r2, [r1]
	LDR      r3, [r0, #0x28]
	CMP      r2, r3
	BGE      |sub_0802A94C|
	LDR      r2, [r0, #0x24]
	LDR      r3, [r1, #0xc]
	CMP      r2, r3
	BGE      |sub_0802A94C|
	LDR      r1, [r1, #4]
	LDR      r0, [r0, #0x2c]
	CMP      r1, r0
	BGE      |sub_0802A94C|
	MOV      r0, #1
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
|sub_0802A94C|
|unk_0802A94C|
		MOV r0, #0
		DCW     0xE7FA
|sub_0802A950|
	PUSH     {r4}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	LDR      r4, [pc, #0xac]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	LDR      r2, [r0, #0x34]
	LDR      r2, [r2, #4]
	STR      r2, [r1]
	LDR      r3, [r0, #0x18]
	AND      r2, r4
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x1c]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r2, [r1, #4]
	MOV      r3, #3
	LSL      r3, r3, #0xa
	ORR      r2, r3
	STR      r2, [r1, #4]
	LDRH     r3, [r0, #0xc]
	LSR      r2, r2, #0xa
	LSL      r2, r2, #0xa
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	ORR      r2, r3
	STR      r2, [r1, #4]
	ADD      r0, #0x30
	LDMIA    r0!, {r0, r1}
	CMP      r1, r0
	BEQ      |sub_0802A9A4|
	MOV      r0, #1
	POP      {r4}
	BX       lr
|sub_0802A9A4|
|unk_0802A9A4|
		MOV r0, #0
		DCW     0xE7FB
|sub_0802A9A8|
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x34]
	STR      r1, [r0, #0x30]
	LDRB     r3, [r1, #2]
	LDRB     r4, [r1, #3]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r1, #8]
	MUL      r3, r4
	ADD      r2, r3, #0
	LDR      r3, [pc, #0x4c]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
	POP      {r4, pc}
	ADD      r2, r1, #0
	MOV      r1, #0
	CMP      r2, #0xb
	PUSH     {r3, lr}
	BEQ      |sub_0802A9E2|
	CMP      r2, #0xc
	BNE      |loc_0802A9E8|
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #0
	POP      {r3, pc}
|sub_0802A9E2|
|unk_0802A9E2|
		STR r1, [r0, #0x30]
		MOV r0, #0
		DCW     0xE7FB
|loc_0802A9E8|
|unk_0802A9E8|
		ADD r0, r1, #0
		DCW     0xE7F9
|sub_0802A9EC|
	CMP      r1, #2
	BLT      |sub_0802A9F4|
	MOV      r0, #1
	BX       lr
|sub_0802A9F4|
|unk_0802A9F4|
; cited by 0x0802A83A (a pc-relative load targets 0x0802A9F8)
		MOV r0, #0
		BX       lr
	INCBIN  baserom.gba_0x2a9f8_0x2aa06.extracted
|sub_0802AA06|
|unk_0802AA06|
	INCBIN	baserom.gba_0x2aa06_0x2aa0a.extracted
	LSL      r1, r0, #0x18
	LDR      r0, [pc, #0x24]
	ADD      r1, #0xff
	LDR      r0, [r0, #4]
	ADD      r1, #0xc1
	STR      r0, [r1, #0x28]
	MOV      r0, #0
	BX       lr
|sub_0802AA1A|
|unk_0802AA1A|
	INCBIN	baserom.gba_0x2aa1a_0x2aa1e.extracted
|sub_0802AA1E|
	LDR      r0, [pc, #0x14]
	ADD      r1, #0xff
	LDR      r0, [r0, #4]
	ADD      r1, #0xc1
	STR      r0, [r1, #0x2c]
	MOV      r0, #0
	BX       lr
	LDR      r0, [pc, #8]
	ADD      r0, #4
	BX       lr
	LSL      r0, r0, #0
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	CMP      r7, #0xfc
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802AA5C|
	LDR      r1, [pc, #0x6c]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_0802AA5C|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	MOV      r4, #0xff
	LDR      r3, [pc, #0x64]
	ADD      r4, #0xe9
	LDR      r4, [r4, r1]
	LDR      r3, [r3, #4]
	SUB      r3, r3, r4
	LDR      r4, [r0, #0xc]
	CMP      r3, r4
	BLE      |sub_0802AA7C|
	LDR      r0, [r0, #0x10]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r4, pc}
|sub_0802AA7C|
|unk_0802AA7C|
		MOV r0, #0
		POP {r4, pc}
|sub_0802AA80|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802AAA0|
	LDR      r1, [pc, #0x30]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_0802AAA0|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	MOV      r4, #0xff
	LDR      r3, [pc, #0x20]
	ADD      r4, #0xed
	LDR      r4, [r4, r1]
	LDR      r3, [r3, #4]
	SUB      r3, r3, r4
	LDR      r4, [r0, #0xc]
	CMP      r3, r4
	BLE      |sub_0802AAC0|
	LDR      r0, [r0, #0x10]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r4, pc}
|sub_0802AAC0|
|unk_0802AAC0|
		MOV r0, #0
		POP {r4, pc}
	INCBIN  baserom.gba_0x2aac4_0x2aac6.extracted
|sub_0802AAC6|
	LSR      r4, r0, #0x20
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x170
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802AAEC|
	LDR      r1, [pc, #0x20]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0802AAEC|
	POP      {r4, pc}
	PUSH     {r3, lr}
	LDR      r3, [pc, #0x18]
	LDR      r3, [r3]
	CMP      r3, #0
	BLE      |sub_0802AB02|
	LDR      r0, [r0, #0xc]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, pc}
|sub_0802AB02|
|unk_0802AB02|
		MOV r0, #0
		DCW     0xE7FC
|sub_0802AB06|
	LSL      r0, r0, #0
|unk_0802AB08|
	INCBIN	baserom.gba_0x2ab08_0x2ab0a.extracted
	LSR      r4, r0, #0x20
	CMP      r7, #0xe4
	LSL      r0, r0, #0xc
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x1c
	ADD      r6, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	ADD      r4, r1, #0
	CMP      r0, #8
	STRH     r0, [r1, #0x12]
	BCS      |sub_0802AB3A|
	MOV      r3, #0
	STRB     r3, [r4, #0x11]
|loc_0802AB36|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|sub_0802AB3A|
|unk_0802AB3A|
		CMP r0, #0x38
		BHS      |loc_0802AB4A|
		ADD r0, #8
		LSL r0, r0, #0x1c
		LSR r0, r0, #0x1f
		ADD r0, #1
		STRB r0, [r4, #0x11]
		B        |loc_0802AB36|
|loc_0802AB4A|
		CMP r0, #0x48