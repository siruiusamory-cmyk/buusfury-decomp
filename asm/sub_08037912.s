	CODE16
|sub_08037912|
|unk_08037912|
		LDR r0, [r2, #0x1c]
		LDRB r0, [r0, #1]
		CMP r0, #4
		BNE      |loc_080379AE|
		LDR r0, [r2, #4]
		LDR r1, [r4, #0x30]
		ADD r6, r2, #4
		CMP r0, r1
		BGE      |loc_080379AE|
		LDR r0, [r4, #0x28]
		LDR r1, [r6, #8]
		CMP r0, r1
		BGE      |loc_080379AE|
		LDR r0, [r6, #4]
		LDR r1, [r4, #0x34]
		CMP r0, r1
		BGE      |loc_080379AE|
		LDR r0, [r4, #0x2c]
		LDR r1, [r6, #0xc]
		CMP r0, r1
		BGE      |loc_080379AE|
		LDR r0, [r4, #0x58]
		LDR r1, [pc, #0x7c]
		LSL r0, r0, #2
		ADD r1, #0x14
		LDR r0, [r1, r0]
		ADD r1, r4, #0
		LSL r3, r0, #1
		ADD r0, r3, r0
		ASR r5, r0, #2
		ADD r0, sp, #0x20
		ADD r1, #0x28
		BL       |inc_0x049120_0x055620| + 0x67e0
		ADD r0, sp, #0x18
		MOV r1, #0
		MOV r2, #0
		STMIA r0!, {r1, r2}
		LDR r0, [sp, #0x20]
		STR r5, [sp, #0x18]
		SUB r1, r0, r5
		LDR r0, [sp, #0x24]
		STR r1, [sp]
		SUB r0, r0, r5
		STR r0, [sp, #4]
		STR r0, [sp, #0xc]
		STR r1, [sp, #8]
		LDR r1, [sp, #0x18]
		LDR r0, [sp, #0x20]
		STR r5, [sp, #0x1c]
		ADD r1, r0, r1
		LDR r0, [sp, #0x24]
		LDR r2, [sp, #0x1c]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x10]
		LDR r0, [r6]
		CMP r0, r1
		BGE      |loc_080379AE|
		LDR r0, [sp, #8]
		LDR r1, [r6, #8]
		CMP r0, r1
		BGE      |loc_080379AE|
		LDR r0, [r6, #4]
		LDR r1, [sp, #0x14]
		CMP r0, r1
		BGE      |loc_080379AE|
		LDR r0, [sp, #0xc]
		LDR r1, [r6, #0xc]
		CMP r0, r1
		BGE      |loc_080379AE|
		ADD r0, r4, #0
		BL       |inc_0x351c0_0x3d4d0| + 0x23ae
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x274e
|loc_080379AE|
|unk_080379AE|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x274e
|loc_080379B2|
|unk_080379B2|
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x379b4_0x379b6.extracted
|sub_080379B6|
|unk_080379B6|
	INCBIN	baserom.gba_0x379b6_0x379ba.extracted
	LSL      r0, r0, #0
	ADD      r4, sp, #0x3c0
	LSR      r6, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LDR      r0, [pc, #0x58]
	PUSH     {r4, lr}
	LDR      r0, [r0]
	SUB      sp, #0x10
	ADD      r4, r0, #0
	ADD      r4, #0x18
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0xfd20
	LDR      r0, [r4]
	LDR      r1, [sp, #8]
	CMP      r0, r1
	BGE      |sub_08037A00|
	LDR      r0, [sp]
	LDR      r1, [r4, #8]
	CMP      r0, r1
	BGE      |sub_08037A00|
	LDR      r0, [r4, #4]
	LDR      r1, [sp, #0xc]
	CMP      r0, r1
	BGE      |sub_08037A00|
	LDR      r0, [sp, #4]
	LDR      r1, [r4, #0xc]
	CMP      r0, r1
	BGE      |sub_08037A00|
	MOV      r0, #1
	ADD      sp, #0x10
	POP      {r4, pc}
