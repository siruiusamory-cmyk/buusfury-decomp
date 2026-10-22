	CODE16
|sub_08035208|
	STR      r4, [sp, #0x2b0]
	LSR      r5, r6, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	LDMIA    r5!, {r2, r3, r4, r5}
	LSR      r4, r0, #0x20
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	ADD      r2, #0x50
	LSL      r0, r0, #0xc
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
|sub_0803522C|
|unk_0803522C|
		PUSH {r4, r5}
		LDRH r2, [r1, #0x12]
		MOV r4, #0
		STRB r4, [r1, #0x11]
		CMP r2, #0x80
		BLO      |inc_0x351c0_0x3d4d0| + 0xa0
		ADD r0, r2, #0
		SUB r0, #0x80
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LSL r3, r0, #0x18
		LDR r5, [pc, #0x380]
		LSR r3, r3, #0x16
		LDR r3, [r5, r3]
		MOV r5, #0xff
		NEG r3, r3
		ASR r3, r3, #0xd
		ADD r5, #0x77
		STRH r3, [r5, r1]
		CMP r0, #0x40
		BHS      |sub_0803525C|
		MOV r0, #1
		STRB r0, [r1, #0x11]
		B        |inc_0x351c0_0x3d4d0| + 0xa0
