	CODE16
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
