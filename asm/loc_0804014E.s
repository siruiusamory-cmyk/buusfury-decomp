	CODE16
|loc_0804014E|
	LDR      r0, [pc, #0xd4]
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0xc0]
	ADD      r5, r0, #0
	LDR      r0, [r4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x10]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	STR      r5, [r4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x9c]
	LDR      r0, [r4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x10]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [pc, #0x8c]
	ADD      r0, #4
	STR      r0, [r4]
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x84]
	ADD      r5, r0, #0
	LDR      r0, [r4, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [pc, #0x70]
	LDR      r0, [r0, #0x14]
	STR      r0, [r4, #0xc]
	STR      r5, [r4, #4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x5c]
	LDR      r0, [r4, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [pc, #0x4c]
	ADD      r0, #8
	STR      r0, [r4, #4]
	POP      {r4, pc}
