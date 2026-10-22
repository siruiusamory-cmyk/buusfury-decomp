	CODE16
|loc_08012CA2|
		MOV r1, #0x80
		STRB r1, [r0, #9]
		STRB r1, [r0, #8]
		B        |inc_0x0158_0x143f2| + 0x12b26
|loc_08012CAA|
		LDR r1, [r1, #4]
		ADD r0, r5, #0
		ADD r1, r1, r2
		BL       |inc_0x042118_0x049114| + 0x498a
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x17
		LSR r0, r0, #0x1f
		BNE      |loc_08012CCC|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		B        |inc_0x0158_0x143f2| + 0x12b26
|loc_08012CCC|
		LDR r1, [r5]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r5, #0
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1f
		BEQ      |inc_0x0158_0x143f2| + 0x12b26
		LDR r1, [r5]
		MOV r2, #0x80
		LDR r2, [r2, r1]
		ADD r0, r5, #0
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		ADD r0, #0x1a
		MOV r3, #0
		LDRSH r0, [r0, r3]
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0x12b26
		ADD r1, r5, #0
		MOV r0, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x1bee
		ADD r1, r0, #0
		STR r0, [r4, #8]
		LDR r0, [pc, #8]
		LDR r0, [r0, #4]
	INCBIN  baserom.gba_0x12d0a_0x12d0c.extracted
|sub_08012D0C|
|unk_08012D0C|
	INCBIN	baserom.gba_0x12d0c_0x12d10.extracted
	ADD      r3, #0xf8
	LSR      r4, r7, #0x20
	STRH     r0, [r3, #4]
	LSR      r3, r5, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r2, #0x77
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	BL       |Record_InitFields|
	LDR      r1, [r4]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r4, r0, #0
	LDRB     r0, [r0, #0x14]
	LDR      r5, [pc, #0x26c]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r5
	LDRB     r1, [r0]
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	BEQ      |loc_08012D62|
	BL       |inc_0x153f2_0x1a3f2| + 0x1d3a
	LDRB     r0, [r4, #0x14]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r5
	LDRB     r0, [r0, #0x17]
	STRB     r0, [r4, #0x14]
|loc_08012D62|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	BL       |Record_InitFields|
	MOV      r0, #0
	ADD      r4, #0xff
	ADD      r4, #0xb1
	STRB     r0, [r4, #9]
	STRB     r0, [r4, #8]
	POP      {r4, pc}
	MOV      r2, #0x80
	ADD      r1, #0xff
	ADD      r1, #0xb1
	PUSH     {r3, lr}
	STRB     r2, [r1, #9]
	STRB     r2, [r1, #8]
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1c
	BEQ      |loc_08012DB4|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08012DB4|
	LDR      r1, [r5]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r0, r5, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |sub_08012DD0|
	ADD      r0, r4, #0
	BL       |sub_08012A24|
	POP      {r3, r4, r5, pc}
