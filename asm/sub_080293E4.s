	CODE16
|sub_080293E4|
	PUSH     {r4, lr}
	LDRB     r1, [r0, #0x10]
	LDR      r3, [pc, #0x1d8]
	LDR      r4, [pc, #0x1e0]
	LSL      r1, r1, #3
	LDR      r2, [r3, r1]
	ADD      r1, r1, r3
	STR      r2, [r0, #0x40]
	LDR      r1, [r1, #4]
	MOV      r2, #0x40
	STR      r1, [r0, #0x44]
	LDR      r0, [pc, #0x1c8]
	MOV      r3, #0
	SUB      r0, #0xc
	LDR      r0, [r0]
	LDR      r1, [pc, #0x1c4]
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xbf4
	POP      {r4, pc}
	MOV      r1, #0x10
	STR      r1, [r0, #0x4c]
	LDR      r1, [pc, #0x1bc]
	STR      r1, [r0, #0x54]
	ADD      r0, #0x40
	MOV      r1, #0
	STMIA    r0!, {r1}
	STR      r1, [r0]
	BX       lr
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r5, #0x40
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x20]
	LDR      r1, [r5]
	SUB      sp, #0x34
	ADD      r0, r0, r1
	STR      r0, [r4, #0x20]
	LDR      r0, [r4, #0x24]
	LDR      r1, [r5, #4]
	ADD      r6, r5, #4
	ADD      r0, r0, r1
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x48]
	ADD      r0, #1
	STR      r0, [r4, #0x48]
	LSL      r0, r0, #0x1c
	LSR      r1, r0, #0x1f
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r0, [r4, #0x54]
	LSL      r1, r1, #2
	ADD      r0, r0, r1
	STR      r0, [r4, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r7, [pc, #0x16c]
	LDR      r0, [r4, #0x4c]
	SUB      r7, #0xc
	CMP      r0, #0
	BEQ      |sub_08029472|
	SUB      r0, #1
	STR      r0, [r4, #0x4c]
	BNE      |loc_0802946E|
	ADD      r1, r4, #0
	LDR      r0, [r7, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_0802946E|
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
