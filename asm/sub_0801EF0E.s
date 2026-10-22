	CODE16
|sub_0801EF0E|
	MOV      r0, #0
	ADD      r1, r6, #0
	STR      r0, [r2, #8]
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	MOV      r0, #0
	ADD      r3, sp, #0
	STRB     r0, [r3]
	MOV      r0, #0x10
	STR      r0, [sp, #4]
	STR      r0, [sp, #8]
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r1, r6, #0
	ADD      r0, #0x15
	BL       |sub_0801F810|
	ADD      r3, sp, #0
	STRB     r7, [r3]
	MOV      r0, #0x44
	STR      r0, [sp, #4]
	MOV      r0, #0x2f
	STR      r0, [sp, #8]
	LDR      r2, [r4, #0x1c]
	ADD      r0, r6, #0
	ADD      r1, pc, #0x138
	BL       |inc_0x03d784_0x041118| + 0x512
	LDR      r1, [pc, #0x120]
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
	MOV      r1, #0
	MVN      r1, r1
	CMP      r2, #0
	PUSH     {r3, lr}
	BEQ      |sub_0801EF74|
	CMP      r2, #1
	BNE      |loc_0801EF8A|
	ADD      r0, r1, #0
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r3, pc}
