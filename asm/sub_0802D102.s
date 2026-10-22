	CODE16
|sub_0802D102|
|unk_0802D102|
		LSR r0, r0, #3
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #8
		BNE      |inc_0x2bb4c_0x2d1c0| + 0x15b2
		LDR r5, [pc, #0xc4]
		LDR r0, [r5]
		BL       |loc_080116FC|
		CMP r0, #0x80
		BLT      |inc_0x2bb4c_0x2d1c0| + 0x15b2
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
		ADD r1, r5, #4
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
		MOV r2, #0
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x18]
		STR r2, [sp]
		ADD r3, r4, #0
		MOV r0, #0
		LDRB r2, [r4, #0x10]
		ADD r1, sp, #0x14
		BL       |sub_0802d79c|
		ADD r1, r0, #0
		LDR r0, [r5]
	INCBIN  baserom.gba_0x2d166_0x2d168.extracted
|sub_0802D168|
|unk_0802D168|
	INCBIN	baserom.gba_0x2d168_0x2d16c.extracted
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x68]
	SUB      sp, #0x10
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x60]
	STR      r1, [sp, #8]
	CMP      r4, #0
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	BEQ      |loc_0802D18A|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_0802D18A|
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x44]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x40]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0802D1B6|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802D1B6|
	ADD      sp, #0x10
	POP      {r4, pc}
|sub_0802D1BA|
|unk_0802D1BA|
		MOV r2, #1
		LDR r1, [r1, #0x14]
		LDR r3, [pc, #0x20]