	CODE16
|sub_08012B22|
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08012B28|
	ADD      sp, #0x5c
	POP      {r4, r5, r6, r7, pc}
|sub_08012B2C|
|unk_08012B2C|
		LDR r0, [r6]
		LDR r1, [r7]
		ASR r0, r0, #8
		ASR r1, r1, #8
		STR r1, [sp, #0x3c]
		STR r1, [sp, #0x44]
		STR r0, [sp, #0x38]
		STR r0, [sp, #0x40]
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0x1d0]
		ADD r6, sp, #0x48
		ADD r1, #0x14
		LSL r0, r0, #4
		ADD r1, r0, r1
		ADD r0, r6, #0
		ADD r2, sp, #0x40
		BL       |inc_0x049120_0x055620| + 0x9eb4
		STR r4, [sp, #0x58]
		ADD r2, r6, #0
		MOV r1, #3
		LDR r0, [r5, #4]
|unk_08012B58|
	INCBIN  baserom.gba_0x12b58_0x12b5a.extracted
|sub_08012B5A|
|unk_08012B5A|
	INCBIN	baserom.gba_0x12b5a_0x12b5e.extracted
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r6, r0, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r4, r0, #0
	LDRB     r1, [r0, #0x15]
	BL       |loc_080135A2|
	ADD      r5, r0, #0
	LDR      r1, [r0, #0x10]
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_08012B8E|
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	LDR      r2, [r5, #0x14]
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08012B8E|
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	BL       |Record_InitFields|
	MOV      r0, #1
	ADD      r4, #0xff
	ADD      r4, #0xc1
	STR      r0, [r4, #8]
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r1, #0xff
	ADD      r1, #0xc1
	MOV      r0, #0
	STR      r0, [r1, #8]
	LDR      r0, [r4, #8]
	CMP      r0, #0
	BEQ      |loc_08012BBE|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x158]
	LDR      r0, [r0, #4]
	BL       |loc_08011944|
|loc_08012BBE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
	POP      {r4, pc}
|sub_08012BC6|
|unk_08012BC6|
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r0, [r0, #8]
		LDR r2, [r1]
		ADD r5, r1, #0
		ADD r1, r2, #0
		ADD r1, #0x80
		CMP r0, #0
		BEQ      |loc_08012CA0|
		LDR r1, [r1]
		ADD r0, r5, #0
		ADD r1, r1, r2
		BL       |inc_0x042118_0x049114| + 0x498a
		ADD r6, r0, #0
		MOV r1, #0x57
		LDRB r1, [r1, r6]
		LDR r3, [pc, #0x134]
		LDR r0, [r4, #4]
		MUL r1, r3
		LSR r1, r1, #4
		ADD r0, r0, r1
		ASR r1, r0, #0x10
		STR r0, [r4, #4]
		ADD r0, r6, #0
		BL       |sub_08013504|
		LDR r0, [r4, #4]
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		STR r0, [r4, #4]
		ADD r0, r6, #0
		ADD r0, #0x1a
		MOV r3, #0
		LDRSH r0, [r0, r3]
		MOV r6, #0
		CMP r0, #0
		BNE      |loc_08012C18|
		LDR r0, [r4, #8]
		STR r6, [r0, #0x44]
		B        |inc_0x0158_0x143f2| + 0x12af6
|loc_08012C18|
		LDR r1, [r5]
		LDR r7, [r4, #8]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r5, #0
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1f
		BEQ      |sub_08012C4A|
		LDR r1, [r5]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r5, #0
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x17
		LSR r0, r0, #0x1f
		BEQ      |sub_08012C4A|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x12af4
