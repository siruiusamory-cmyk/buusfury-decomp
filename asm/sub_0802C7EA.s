	CODE16
|sub_0802C7EA|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r0, #0x40
	ADD      r7, r1, #0
	LDR      r1, [r4, #0x20]
	LDMIA    r0!, {r2}
	SUB      sp, #0x34
	ADD      r1, r1, r2
	STR      r1, [r4, #0x20]
	LDR      r1, [r4, #0x24]
	LDR      r0, [r0]
	ADD      r0, r1, r0
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x48]
	LDR      r1, [pc, #0xf8]
	ADD      r0, #1
	STR      r0, [r4, #0x48]
	LSL      r0, r0, #0x1c
	LSR      r0, r0, #0x1f
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	STR      r0, [r4, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r5, [pc, #0xe0]
	SUB      r5, #8
	LDR      r0, [r5, #4]
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r2, [r4, #0x30]
	CMP      r1, r2
	BGE      |loc_0802C85C|
	LDR      r1, [r4, #0x28]
	LDR      r2, [r0, #8]
	CMP      r1, r2
	BGE      |loc_0802C85C|
	LDR      r1, [r0, #4]
	LDR      r2, [r4, #0x34]
	CMP      r1, r2
	BGE      |loc_0802C85C|
	LDR      r1, [r4, #0x2c]
	LDR      r0, [r0, #0xc]
	CMP      r1, r0
	BGE      |loc_0802C85C|
	ADD      r0, r4, #0
	ADD      r0, #0x28
	LDR      r1, [r5, #4]
	ADD      r6, r0, #0
	ADD      r1, #0x80
	LDR      r1, [r1, #0x2c]
	BL       |inc_0x0158_0x143f2| + 0x91cc
	CMP      r0, #0
	BNE      |sub_0802C868|
|loc_0802C85C|
	ADD      r1, r4, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
