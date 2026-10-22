	CODE16
|sub_0800A00E|
	LSL      r0, r0, #0
	LDR      r6, [sp, #0x2f0]
	LSR      r4, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ASR      r0, r5, #0x1b
	LSR      r7, r0, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x2c
	ADD      r6, sp, #0x14
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	ADD      r0, r6, #0
	BL       |Object_WriteBounds1|
	STR      r6, [sp, #0x10]
	ADD      r6, r4, #0
	ADD      r1, r5, #4
	STR      r1, [sp, #0x28]
	ADD      r6, #0xff
	ADD      r6, #0xa1
	LDR      r0, [r6]
	LDR      r2, [r5, #4]
	ADD      r1, #4
	ADD      r0, r0, r2
	STR      r0, [r6]
	STR      r1, [sp, #0x24]
	LDR      r0, [r6, #4]
	LDR      r1, [r1]
	MOV      r7, sp
	ADD      r0, r0, r1
	STR      r0, [r6, #4]
	MOV      r0, sp
	ADD      r1, r4, #0
	BL       |Object_WriteBounds1|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x4c]
	ADD      r3, r2, r1
	MOV      r2, #1
	LDR      r1, [sp, #0x10]
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x50]
	ADD      r2, r2, r1
	ADD      r1, r7, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |sub_0800A0C2|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x4c]
	ADD      r3, r2, r1
	MOV      r2, #0
	LDR      r1, [sp, #0x10]
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_0800A0A8|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800A0A8|
	LDR      r1, [sp, #0x28]
	LDR      r0, [r6]
	LDR      r1, [r1]
	SUB      r0, r0, r1
	STR      r0, [r6]
	LDR      r1, [sp, #0x24]
	LDR      r0, [r6, #4]
	LDR      r1, [r1]
	SUB      r0, r0, r1
	STR      r0, [r6, #4]
	MOV      r0, #0
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
