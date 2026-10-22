	CODE16
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
