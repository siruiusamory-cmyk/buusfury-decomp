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
