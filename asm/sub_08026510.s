	CODE16
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
		BL       |List_Append|
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
