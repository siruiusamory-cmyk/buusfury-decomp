	CODE16
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
		BL       |Object_Construct1|
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
		BL       |Object_Construct1|
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
		BL       |Object_Construct1|
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
