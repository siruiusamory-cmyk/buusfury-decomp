	CODE16
|sub_08012F8C|
|unk_08012F8C|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1f
		BEQ      |inc_0x0158_0x143f2| + 0x12e30
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x12fa4_0x12fa6.extracted
|sub_08012FA6|
|unk_08012FA6|
	INCBIN	baserom.gba_0x12fa6_0x12faa.extracted
	LSL      r0, r0, #0
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	MOV      r6, #0x8c
	LSR      r7, r0, #0x20
	ADD      r3, #0xf8
	LSR      r4, r7, #0x20
	BVC      |loc_08013074|
	LSR      r4, r0, #0x20
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	BL       |loc_0800DEB0|
	LDRH     r0, [r4, #0x12]
	LSL      r0, r0, #0x1c
	BNE      |loc_08012FE4|
	LDR      r0, [pc, #0x358]
	LDR      r4, [pc, #0x35c]
	LDR      r0, [r0]
	MOV      r3, #0
	MOV      r2, #0x20
	ADD      r0, r0, r4
	LDR      r1, [pc, #0x350]
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08012FE4|
	POP      {r4, pc}
|sub_08012FE6|
|unk_08012FE6|
		PUSH {r3, r4, r5, lr}
		ADD r5, r0, #0
		ADD r4, r1, #0
		BL       |inc_0x0158_0x143f2| + 0xde66
		MOV r0, #0
		STR r0, [r5, #4]
		LDR r1, [r4]
		MOV r2, #0x80
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		ADD r0, #0x67
		LDRB r0, [r0]
		CMP r0, #0
		BNE      |sub_0801300E|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x12eb8
