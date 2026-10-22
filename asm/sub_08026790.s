	CODE16
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
		BL       |List_Append|
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
