	CODE16
|sub_08029272|
	MOV      r2, #0
	SUB      r2, r3, r2
	STR      r2, [r1, #8]
	ADD      r0, r3, #0
	ADD      r3, sp, #0x100
	MOV      r1, #3
	STRB     r1, [r3, #0x1f]
	MOV      r1, #0xa9
	STR      r1, [sp, #0x120]
	MOV      r1, #0x58
	STR      r1, [sp, #0x124]
	STRB     r0, [r3, #0x1c]
	LDR      r0, [r4, #0x18]
	LSL      r0, r0, #1
	ADD      r0, r0, r5
	ADD      r0, #0x2e
	LDRB     r2, [r0]
	ADD      r2, #1
	ADD      r0, r7, #0
	ADD      r1, pc, #0x3C
	BL       |inc_0x03d784_0x041118| + 0x512
	ADD      r1, r7, #0
	LDR      r0, [sp, #0x150]
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x20]
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	ADD      r0, sp, #0x11c
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x154
	POP      {r4, r5, r6, r7, pc}
|sub_080292BA|
	DCW      0x0000
	DCW      0xbce8,0x0806,0xf04c,0x0874,0xf800,0x0600,0x9640,0x0600
	DCW      0x0259,0x0000,0x1f83,0x0000,0xf5a5,0x0803
|loc_080292D8|
|unk_080292D8|
	INCBIN  baserom.gba_0x292d8_0x292e0.extracted
		PUSH {r4, r5, r6, lr}
		ADD r3, r2, #0
		MOV r2, #0
		CMP r3, #1
		LDR r5, [pc, #0x8c]
		BEQ      |sub_0802931C|
		MOV r1, #0x9f
		ADD r0, #0xff
		ADD r0, #1
		LSL r1, r1, #3
		MOV r4, #1
		CMP r3, #4
		DCW     0xD01D
		CMP r3, #5
		BNE      |sub_0802936E|
		LDR r6, [r0, #0x14]
		MOV r3, #0x68
		LDR r5, [r5, #8]
		MUL r3, r6
		ADD r3, r3, r5
		ADD r1, r3, r1
		LDR r3, [r0, #0x18]
		LSL r3, r3, #1
		ADD r1, r3, r1
		ADD r1, #0x2e
		LDRB r3, [r1]
		ADD r3, r3, r4
		LSL r3, r3, #0x18
		LSR r3, r3, #0x18
		B        |loc_08029360|
