	CODE16
|loc_08004F50|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1]
	LDR      r2, [r1, #8]
	SUB      sp, #0x14
	SUB      r5, r2, r0
	LDR      r2, [r1, #0xc]
	LDR      r1, [r1, #4]
	LDR      r7, [pc, #0x240]
	SUB      r3, r2, r1
	STR      r3, [sp, #4]
	LDR      r2, [r4, #0x28]
	MUL      r1, r2
	LDR      r2, [r4, #0x24]
	ADD      r1, r1, r2
	ADD      r6, r1, r0
	ADD      r1, r6, #0
	ADD      r0, r6, r5
	SUB      r0, #5
	MOV      r2, #0
|loc_08004F78|
	LDR      r3, [pc, #0x22c]
	ADD      r2, #1
	STR      r3, [r1]
	LDR      r3, [pc, #0x22c]
	STRH     r3, [r1, #4]
	MOV      r3, #0x30
	STRB     r3, [r0]
	MOV      r3, #1
	STR      r7, [r3, r0]
	LDR      r3, [r4, #0x28]
	ADD      r1, r3, r1
	ADD      r0, r3, r0
	CMP      r2, #3
	BLT      |loc_08004F78|
	LDR      r3, [sp, #4]
	CMP      r2, r3
	BGE      |loc_08004FC4|
|loc_08004F9A|
	LDR      r3, [pc, #0x20c]
	LDR      r7, [pc, #0x204]
	STR      r3, [r1]
	LDR      r3, [pc, #0x208]
	ADD      r2, #1
	STRH     r3, [r1, #4]
	MOV      r3, #0x30
	STRB     r3, [r0]
	ADD      r3, r0, #1
	STR      r7, [r3]
	MOV      r7, #0xff
	ADD      r7, #2
	STRH     r7, [r3, #4]
	MOV      r3, #1
	STRB     r3, [r0, #7]
	LDR      r3, [r4, #0x28]
	ADD      r1, r3, r1
	ADD      r0, r3, r0
	LDR      r3, [sp, #4]
	CMP      r2, r3
	BLT      |loc_08004F9A|
|loc_08004FC4|
	ADD      r2, r5, #0
	MOV      r1, #0x1d
	ADD      r0, r6, #0
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	SUB      r2, r5, #2
	MOV      r1, #0x6e
	ADD      r6, r0, r6
	ADD      r0, r6, #1
	STR      r2, [sp, #0x10]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	SUB      r2, r5, #4
	MOV      r1, #0x3f
	ADD      r6, r0, r6
	ADD      r0, r6, #2
	STR      r2, [sp, #0xc]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	SUB      r2, r5, #6
	ADD      r7, r0, r6
	ADD      r6, r2, #0
	MOV      r1, #1
	ADD      r0, r7, #3
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	ADD      r2, r6, #0
	MOV      r1, #1
	ADD      r7, r0, r7
	ADD      r0, r7, #3
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	SUB      r2, r6, #4
	MOV      r1, #0x30
	ADD      r7, r0, r7
	ADD      r0, r7, #5
	STR      r2, [sp, #8]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	LDR      r1, [sp, #4]
	LDR      r2, [sp, #8]
	SUB      r1, #0xa
	MUL      r0, r1
	ADD      r7, r0, r7
	MOV      r1, #0x30
	ADD      r0, r7, #5
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	ADD      r2, r6, #0
	MOV      r1, #1
	ADD      r7, r0, r7
	ADD      r0, r7, #3
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	MOV      r1, #0x1d
	ADD      r6, r0, r7
	ADD      r0, r6, #2
	LDR      r2, [sp, #0xc]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	MOV      r1, #0x6e
	ADD      r6, r0, r6
	ADD      r0, r6, #1
	LDR      r2, [sp, #0x10]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	ADD      r2, r5, #0
	MOV      r1, #0x3f
	ADD      r6, r0, r6
	ADD      r0, r6, #0
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	ADD      r2, r5, #0
	MOV      r1, #1
	ADD      r6, r0, r6
	ADD      r0, r6, #3
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	ADD      r2, r5, #0
	MOV      r1, #1
	ADD      r6, r0, r6
	ADD      r0, r6, #3
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x28]
	ADD      r2, r5, #0
	MOV      r1, #1
	ADD      r0, r0, r6
	ADD      r0, #3
	BL       |inc_0x046118_0x049114| + 0xd28
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x2c]
	SUB      sp, #0x14
	MOV      r2, #0
	STR      r2, [sp, #4]
	MOV      r2, #8
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	SUB      r0, #8
	STR      r0, [sp, #0x10]
	MOV      r2, #0
	STR      r1, [sp, #8]
	ADD      r1, sp, #4
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x21f0
	LDR      r0, [r4, #0x28]
	LDR      r2, [r4, #0x2c]
	ADD      r1, r0, #0
	SUB      r1, #8
	STR      r1, [sp, #4]
	MOV      r1, #0
	SUB      r2, #8
	STR      r2, [sp, #0x10]
	MOV      r2, #0
	STR      r1, [sp, #8]
	STR      r0, [sp, #0xc]
	ADD      r0, r4, #0
	ADD      r1, sp, #4
	BL       |inc_0x03d784_0x041118| + 0x21f0
	LDR      r0, [r4, #0x2c]
	LDR      r2, [r4, #0x28]
	ADD      r1, r0, #0
	SUB      r1, #8
	MOV      r3, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0
	STR      r1, [sp, #8]
	STR      r0, [sp, #0x10]
	ADD      r0, r4, #0
	ADD      r1, sp, #4
	STR      r3, [sp, #4]
	BL       |inc_0x03d784_0x041118| + 0x21f0
	LDR      r0, [r4, #0x28]
	LDR      r1, [r4, #0x2c]
	MOV      r2, #0xc
	SUB      r0, #0xc
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	SUB      r1, #0xc
	MOV      r2, #4
	SUB      r0, #0xc
	STR      r0, [sp]
	STR      r2, [sp, #8]
	STR      r1, [sp, #0x10]
	LDR      r0, [r4, #0x24]
	SUB      r5, r1, #4
	LDR      r1, [r4, #0x28]
	LDR      r7, [pc, #0x88]
	LSL      r1, r1, #2
	ADD      r6, r0, r1
	ADD      r6, #0xc
	CMP      r5, #0
	BEQ      |loc_08005134|
|loc_0800511C|
	ADD      r1, r7, #0
	ADD      r0, r6, #0
	LDR      r2, [sp]
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [r4, #0x28]
	SUB      r5, #1
	ADD      r6, r0, r6
	LDR      r0, [pc, #0x70]
	EOR      r7, r0
	CMP      r5, #0
	BNE      |loc_0800511C|
|loc_08005134|
	LDR      r0, [r4, #0x28]
	LDR      r1, [r4, #0x2c]
	MOV      r2, #8
	STR      r2, [sp, #4]
	SUB      r1, #8
	MOV      r2, #0
	SUB      r0, #8
	STR      r0, [sp, #0xc]
	STR      r1, [sp, #0x10]
	ADD      r1, sp, #4
	ADD      r0, r4, #0
	STR      r2, [sp, #8]
	BL       |loc_08004F50|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
