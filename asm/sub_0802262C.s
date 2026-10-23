|sub_0802262C|
	EXPORT |sub_0802262C|
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
	CODE16
|dat_08022672|
	DCW      0x0000
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
		BL       |Thunk_JumpRegister1|
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

