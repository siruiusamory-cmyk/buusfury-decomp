	CODE16
|sub_0803D7FA|
	PUSH     {r4, r5, r6, lr}
	LDR      r5, [pc, #0x130]
	LDR      r4, [pc, #0x12c]
	MOV      r6, #1
|loc_0803D802|
	LDR      r0, [r5]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #0xc]
	BL       |loc_0803F296|
	ADD      r1, r6, #0
	LDR      r0, [r4, #4]
	BL       |loc_0803F3F4|
	LDR      r0, [r5, #4]
	ADD      r0, #1
	STR      r0, [r5, #4]
	LDR      r0, [r4, #8]
	BL       |inc_0x351c0_0x3d4d0| + 0x82e0
	LDR      r0, [r4, #0x10]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BNE      |loc_0803D83E|
	BL       |loc_0804014E|
|loc_0803D83E|
	LDR      r0, [r5]
	LDR      r1, [r0]
|loc_0803D842|
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0803D802|
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0xdc]
	ADD      r4, r0, #0
	LDR      r1, [pc, #0xe4]
	LDR      r0, [r5]
	STR      r1, [r5]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	STR      r4, [r5]
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0xc0]
	LDR      r5, [pc, #0xb4]
	ADD      r4, #4
	STR      r0, [r4, #4]
	LDR      r0, [r5]
	SUB      r1, r4, #4
	STR      r1, [r5]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4]
	LDR      r1, [r0, #4]
	ADD      r1, r1, r0
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98a
	STR      r4, [r5]
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r4, [pc, #0x8c]
	ADD      r5, r0, #0
	LDR      r0, [r4, #8]
	LDR      r2, [r4]
	ADD      r1, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	STR      r1, [r4, #8]
	LDR      r6, [pc, #0x88]
	STR      r2, [r0, #0xc]
	STR      r6, [r4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	STR      r5, [r4]
	BL       |sub_0803D7FA|
	ADD      r5, r0, #0
	LDR      r0, [r4, #8]
	CMP      r0, #0
	BEQ      |loc_0803D8EE|
	LDR      r0, [r4]
	STR      r6, [r4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #8]
	SUB      r0, #1
	STR      r0, [r4, #8]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #0xc]
	STR      r0, [r4]
|loc_0803D8EE|
	ADD      r0, r5, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x38]
	LDR      r1, [pc, #0x44]
	LDR      r0, [r4]
	STR      r1, [r4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #8]
	CMP      r0, #0
	BEQ      |loc_0803D928|
|loc_0803D90C|
	LDR      r0, [r4, #8]
	SUB      r0, #1
	STR      r0, [r4, #8]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #8]
	CMP      r0, #0
	BNE      |loc_0803D90C|
|loc_0803D928|
	POP      {r4, pc}
	LSL      r0, r0, #0
	LDRH     r0, [r0, r6]
	LSR      r3, r7, #1
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	BVC      |loc_0803D842|
	LSR      r3, r0, #0x20
	LSL      r0, r0, #8
	LSL      r0, r0, #0x10
	ADD      r4, #0x8c
	LSL      r0, r0, #0xc
	ADD      r2, r0, #0
	ADD      r0, r1, #0
	PUSH     {r3, lr}
	LDR      r3, [r2]
	ADD      r1, r2, #0
	ADD      r1, #8
	CMP      r3, #0
	BEQ      |sub_0803D95E|
	CMP      r3, #1
	BEQ      |loc_0803D958|
	CMP      r3, #2
	BNE      |loc_0803D95C|
|loc_0803D958|
	BL       |inc_0x049120_0x055620|
|loc_0803D95C|
	POP      {r3, pc}
