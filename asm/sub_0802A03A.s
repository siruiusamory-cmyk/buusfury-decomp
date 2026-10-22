	CODE16
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
		BL       |Thunk_JumpRegister1|
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
		BL       |Object_WriteBounds1|
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
