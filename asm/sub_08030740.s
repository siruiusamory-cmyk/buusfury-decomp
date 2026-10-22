	CODE16
|sub_08030740|
	STRH     r1, [r4, #0x12]
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r7, r4, #0
	LDRB     r0, [r5, #0xc]
	ADD      r7, #0xff
	ADD      r7, #0xa1
	CMP      r0, #0
	BEQ      |loc_0803076E|
	LDR      r0, [r6]
	LDR      r3, [sp, #0x40]
	LSL      r0, r0, #9
	LDR      r1, [r3]
	ASR      r0, r0, #8
	LSL      r1, r1, #9
	ASR      r1, r1, #8
	STR      r1, [sp, #0x24]
	STR      r1, [sp, #0x2c]
	STR      r0, [sp, #0x20]
	STR      r0, [sp, #0x28]
	ADD      r6, sp, #0x28
|loc_0803076E|
	LDR      r0, [r7]
	LDR      r1, [r6]
	LDR      r2, [r7, #4]
	ADD      r0, r0, r1
	LDR      r1, [r6, #4]
	STR      r0, [sp, #0x20]
	ADD      r1, r2, r1
	STR      r1, [sp, #0x24]
	STR      r1, [sp, #0x34]
	STR      r1, [sp, #0x3c]
	STR      r0, [sp, #0x30]
	STR      r0, [sp, #0x38]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r5, r7, #4
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x54]
	ADD      r2, r2, r1
	ADD      r1, sp, #0x38
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_080307B0|
	LDR      r0, [sp, #0x38]
	STR      r0, [r7]
	LDR      r0, [sp, #0x3c]
	STR      r0, [r5]
|loc_080307B0|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r4, #0
	ADD      r0, sp, #0x18
	BL       |inc_0x0158_0x143f2| + 0xfd20
	LDR      r0, [pc, #0x8c]
	LDR      r1, [r0]
	ADD      r0, sp, #0x28
	BL       |inc_0x0158_0x143f2| + 0xfd20
	LDR      r0, [sp, #0x18]
	LDR      r1, [sp, #0x30]
	CMP      r0, r1
	BGE      |loc_080307F6|
	LDR      r0, [sp, #0x28]
	LDR      r1, [sp, #0x20]
	CMP      r0, r1
	BGE      |loc_080307F6|
	LDR      r0, [sp, #0x1c]
	LDR      r1, [sp, #0x34]
	CMP      r0, r1
	BGE      |loc_080307F6|
	LDR      r0, [sp, #0x2c]
	LDR      r1, [sp, #0x24]
	CMP      r0, r1
	BGE      |loc_080307F6|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed20
|loc_080307F6|
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
|sub_080307FA|
|unk_080307FA|
		PUSH {r4}
		LDRB r3, [r0, #0xc]
		ADD r2, r1, #0
		ADD r2, #0xff
		ADD r2, #0x61
		CMP r3, #0
		LDRH r0, [r1, #0x12]
		LDR r4, [pc, #0x4c]
		BEQ      |loc_08030826|
		CMP r3, #1
		BNE      |loc_08030840|
		LSL r3, r0, #0x18
		LSR r3, r3, #0x16
		LDR r3, [r4, r3]
		NEG r3, r3
		ASR r3, r3, #0xb
		STRH r3, [r2, #0x16]
		CMP r0, #0x30
		BNE      |sub_08030838|
		MOV r2, #1
		STRB r2, [r1, #0x11]
		B        |loc_08030840|
|loc_08030826|
		MOV r3, #0
		STRB r3, [r1, #0x11]
		LSL r3, r0, #0x18
		LSR r3, r3, #0x16
		LDR r3, [r4, r3]
		NEG r3, r3
		ASR r3, r3, #0xd
		STRH r3, [r2, #0x16]
		B        |loc_08030840|
