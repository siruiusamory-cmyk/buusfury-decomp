	CODE16
|sub_0803BC1A|
	LSL      r0, r0, #0xc
	ADD      r2, #0xe5
	LSL      r0, r0, #0xc
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
|unk_0803BC24|
	INCBIN	baserom.gba_0x3bc24_0x3bc26.extracted
	LSR      r7, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	SUB      sp, #0x1c
	STR      r1, [sp, #0x10]
	ADD      r4, r0, #0
	ADD      r4, #0x20
	ADD      r1, #4
	STR      r1, [sp, #0x18]
	SUB      r5, r4, #4
	ADD      r6, r0, #0
	ADD      r1, r5, #4
	STR      r1, [sp, #0x14]
|loc_0803BC48|
	MOV      r0, #0xff
	ADD      r0, #0x27
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r0, #0x60
	LSL      r0, r0, #8
	STR      r0, [r6, #0x1c]
	MOV      r0, #0xf0
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r0, #0x70
	LSL      r0, r0, #8
	STR      r0, [r4]
	LDR      r1, [r7]
	ADD      r0, r7, #0
	LDR      r2, [r1, #0x54]
	ADD      r2, r2, r1
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_0803BC48|
	LDR      r1, [sp, #0x10]
	LDR      r0, [r5]
	LDR      r1, [r1]
	ADD      r2, sp, #0x14
	SUB      r0, r0, r1
	LDMIA    r2!, {r1, r2}
	LDR      r1, [r1]
	LDR      r2, [r2]
	STR      r0, [sp]
	SUB      r1, r1, r2
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	ADD      r1, r0, #0
	STR      r0, [sp, #8]
	MUL      r0, r1
	ASR      r1, r0, #8
	LDR      r0, [sp, #0xc]
	ADD      r2, r0, #0
	MUL      r0, r2
	ASR      r0, r0, #8
	ADD      r0, r1, r0
	MOV      r1, #5
	LSL      r1, r1, #0xc
	CMP      r0, r1
	BLT      |loc_0803BC48|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|sub_0803BCAA|
|unk_0803BCAA|
		PUSH {r4, r5, lr}
		ADD r4, r0, #0
		ADD r5, r1, #0
		SUB sp, #0x1c
		BL       |inc_0x351c0_0x3d4d0| + 0x6988
		ADD r1, r5, #0
		ADD r1, #0xff
		ADD r1, #0xa1
		LDMIA r1!, {r3}
		LDR r2, [r4, #0x1c]
		LDR r0, [r4, #0x20]
		LDR r1, [r1]
		SUB r2, r2, r3
		SUB r0, r0, r1
		STR r0, [sp, #8]
		LDR r1, [sp, #8]
		CMP r2, #0
		STR r2, [sp, #4]
		STR r2, [sp, #0xc]
		STR r2, [sp, #0x14]
		STR r1, [sp, #0x10]
		STR r1, [sp, #0x18]
		BLT      |loc_0803BCDE|
		LDR r1, [sp, #0x14]
		B        |loc_0803BCE2|
|loc_0803BCDE|
		LDR r0, [sp, #0x14]
		NEG r1, r0
|loc_0803BCE2|
		MOV r0, #1
		LSL r0, r0, #0xb
		CMP r1, r0
		BGE      |sub_0803BD02|
		LDR r1, [sp, #0x18]
		CMP r1, #0
		BLT      |sub_0803BCF4|
		LDR r1, [sp, #0x18]
		B        |inc_0x351c0_0x3d4d0| + 0x6b38
