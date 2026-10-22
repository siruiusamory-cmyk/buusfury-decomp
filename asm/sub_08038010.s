	CODE16
|sub_08038010|
	CMP      r1, #0
	BEQ      |loc_080380A6|
	LDR      r0, [r4, #0x3c]
	LDR      r1, [r4, #0x2c]
	LDR      r2, [r4, #0x30]
	MUL      r1, r0
	MUL      r2, r0
	ADD      r0, r1, #0
	STR      r1, [sp, #0x38]
	ADD      r1, r2, #0
	STR      r2, [sp, #0x3c]
	LDR      r2, [r4, #0x1c]
	ADD      r3, sp, #0x20
	ADD      r0, r2, r0
	LDR      r2, [r4, #0x20]
	STR      r0, [sp, #0x38]
	ADD      r1, r2, r1
	STR      r1, [sp, #0x3c]
	STR      r1, [sp, #0x40]
	ADD      r7, r0, #0
	LDR      r0, [r4, #0x58]
	ADD      r1, sp, #0xc
	STR      r0, [sp, #0x2c]
	LDR      r0, [r4, #0x40]
	ADD      r2, r7, #0
	STRB     r0, [r3]
	LDR      r0, [pc, #0x150]
	ADD      r3, sp, #0
	STR      r0, [sp, #0x28]
	MOV      r0, #1
	LSL      r0, r0, #0xa
	STR      r0, [sp, #0x24]
	MOV      r0, #0
	STRB     r0, [r3, #0xc]
	ADD      r0, r1, #4
	LDR      r1, [sp, #0x40]
	LDR      r3, [sp, #0x40]
	SUB      r1, #0xc
	STR      r1, [sp, #0x14]
	LDR      r1, [pc, #0x11c]
	STR      r4, [sp, #0x3c]
	ADD      r2, #0x20
	ADD      r3, #0xc
	STR      r3, [sp, #0x1c]
	STR      r2, [sp, #0x18]
	STR      r7, [sp, #0x10]
	LDR      r1, [r1, #4]
	ADD      r1, #0x80
	LDR      r1, [r1, #0x2c]
	BL       |inc_0x0158_0x143f2| + 0x91cc
	CMP      r0, #0
	BEQ      |loc_08038136|
	LDR      r0, [pc, #0x100]
	ADD      r2, sp, #0xc
	MOV      r1, #0
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11ab4
	CMP      r0, #0
	BEQ      |loc_08038124|
	LDR      r1, [r5]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r5, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r0, #0x16
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	CMP      r0, #0
	BGT      |loc_080380AC|
	MOV      r2, #1
	STRB     r2, [r4, #0x10]
|loc_080380A6|
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
|sub_080380AA|
|unk_080380AA|
		B        |loc_0803814E|
