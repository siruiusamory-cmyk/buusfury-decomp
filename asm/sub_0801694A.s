	CODE16
|sub_0801694A|
|unk_0801694A|
		MOV r0, #0x14
		STR r0, [r1]
		LDR r0, [r2, #0x24]
		LDR r2, [r2, #0x20]
		SUB r0, r0, r2
		LSL r3, r0, #3
		ADD r0, r3, r0
		LSL r0, r0, #1
		ADD r0, #0x36
		STR r0, [r1, #4]
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x1554
		PUSH {r4, r5, r6, r7, lr}
		SUB sp, #0x1fc
		SUB sp, #0x28
		ADD r5, sp, #0x1f0
		ADD r4, r0, #0
		MOV r2, #0xa0
		MOV r1, #0xf0
		ADD r0, r5, #0
		BL       |loc_0803F540|
		MOV r3, #0
		MOV r2, #0x21
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_08006718|
		MOV r0, #0xff
		ADD r0, #0x1d
		LDR r0, [r0, r4]
		CMP r0, #0
		BNE      |inc_0x153f2_0x1a3f2| + 0x15aa
		ADD r2, r4, #0
		ADD r2, #0xff
		ADD r2, #0x35
		ADD r1, r5, #0
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x16996_0x16998.extracted
|sub_08016998|
|unk_08016998|
	INCBIN	baserom.gba_0x16998_0x1699c.extracted
	MOV      r0, #0xa1
	LSL      r0, r0, #2
	ADD      r2, r4, r0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_080167A0|
	ADD      r1, sp, #0x1f0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	ADD      r7, sp, #0x10
	LDR      r0, [pc, #0xe0]
	ADD      r1, r7, #0
	ADD      r0, #0x10
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [pc, #0xd8]
	MOV      r3, #0x68
	LDR      r0, [r0, #0xc]
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	ADD      r0, #0x16
	MOV      r3, #2
	LDRSH    r1, [r0, r3]
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	MOV      r4, #0x29
	MUL      r0, r4
	SWI      6
	ADD      r6, r0, #0
	MOV      r3, #0x68
	LDR      r0, [pc, #0xb0]
	LDR      r0, [r0, #0xc]
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	ADD      r0, #0x1a
	MOV      r3, #2
	LDRSH    r1, [r0, r3]
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	MUL      r0, r4
	SWI      6
	ADD      r5, r0, #0
	SUB      r4, r4, r6
	BEQ      |loc_08016A2E|
	ADD      r6, r7, r6
	ADD      r0, r6, #0
	ADD      r0, #0x3e
	ADD      r2, r4, #0
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0xd28
	ADD      r0, r6, #0
	ADD      r0, #0x72
	ADD      r2, r4, #0
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0xd28
	ADD      r0, r6, #0
	ADD      r0, #0xa6
	ADD      r2, r4, #0
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0xd28
|loc_08016A2E|
	MOV      r4, #0x29
	SUB      r4, r4, r5
	BEQ      |loc_08016A60|
	ADD      r5, r7, r5
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #0xf
	ADD      r2, r4, #0
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0xd28
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #0x43
	ADD      r2, r4, #0
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0xd28
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #0x77
	ADD      r2, r4, #0
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0xd28
|loc_08016A60|
	MOV      r0, #0xac
	STR      r0, [sp]
	MOV      r0, #0x88
	STR      r0, [sp, #4]
	MOV      r0, #0xe1
	STR      r0, [sp, #8]
	MOV      r0, #0x91
	STR      r0, [sp, #0xc]
	ADD      r1, r7, #0
	ADD      r5, sp, #0x1f0
	ADD      r0, r5, #0
	MOV      r2, sp
	BL       |inc_0x03d784_0x041118| + 0x219e
	LDR      r1, [pc, #0x24]
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	ADD      r0, sp, #0x1f0
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x1fc
	ADD      sp, #0x28
	POP      {r4, r5, r6, r7, pc}
|sub_08016A92|
|unk_08016A92|
; cited by 0x080167AE (a pc-relative load targets 0x08016A94)
	INCBIN  baserom.gba_0x16a92_0x16aa8.extracted
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		CMP r2, #8
		BHS      |loc_08016ABA|
		ADR      r3, |sub_08016ABC|
		ADD r3, r3, r2
		LDRH r3, [r3, r2]
		LSL r3, r3, #1
		ADD pc, r3
|loc_08016ABA|
		B        |loc_08016C58|
