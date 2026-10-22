	CODE16
|loc_08018A26|
	MOV      r1, #0x29
	LSL      r1, r1, #4
	ADD      r0, r5, r1
	LDRB     r6, [r0]
	MOV      r0, #1
	EOR      r6, r0
	ASR      r1, r6, #1
|loc_08018A34|
	EOR      r0, r1
	STR      r0, [sp, #4]
	MOV      r0, #0x40
	STR      r1, [sp, #8]
	BL       |inc_0x03d784_0x041118| + 0x2348
	LDR      r1, [r4, #0xc]
	ADD      r0, #0x60
	MUL      r0, r1
	LSR      r7, r0, #7
	LDR      r0, [sp, #4]
	LDR      r2, [pc, #0x194]
	LSL      r1, r6, #2
	LDR      r1, [r2, r1]
	ADD      r4, #4
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	MUL      r1, r7
	STR      r1, [r0]
	MOV      r0, #1
	LSL      r0, r0, #0xf
	BL       |inc_0x03d784_0x041118| + 0x2348
	MOV      r1, #1
	LSL      r1, r1, #0xe
	SUB      r0, r0, r1
	LDR      r1, [sp, #8]
	MUL      r0, r7
	LSL      r1, r1, #2
	ADD      r1, r1, r4
	ASR      r0, r0, #0xc
	STR      r0, [r1]
	MOV      r0, #0xff
	ADD      r0, #0xc9
	STRB     r6, [r5, #0x10]
	LDR      r0, [r0, r5]
	CMP      r0, #0
	BNE      |loc_08018A8E|
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08018A8E|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r0, r1, #0
	ADD      r0, #0xff
	ADD      r0, #0xc1
	SUB      sp, #0x64
	STR      r0, [sp, #0x60]
	ADD      r4, r1, #0
	LDR      r1, [r1]
	LDR      r0, [r0, #8]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	CMP      r0, #0
	BEQ      |sub_08018AD6|
	ADD      r0, r4, #0
	MOV      r1, #7
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_08018AC8|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #7
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08018AC8|
	LDR      r0, [r5, #0x10]
	SUB      r0, #1
	STR      r0, [r5, #0x10]
	BNE      |loc_08018AE6|
	MOV      r0, #1
	ADD      sp, #0x64
	POP      {r4, r5, r6, r7, pc}
