	CODE16
|sub_08023C22|
	EXPORT |sub_08023C22|
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
		BL       |Thunk_SignedDivide|
		STR r0, [sp]
		LDR r0, [sp, #0x18]
		LSL r1, r0, #8
		ADD r0, r6, #0
		BL       |Thunk_SignedDivide|
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
