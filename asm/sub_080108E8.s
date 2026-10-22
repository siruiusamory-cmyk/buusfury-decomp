	CODE16
|sub_080108E8|
	LDR      r1, [pc, #0x268]
	ASR      r0, r0, #1
	LDRB     r1, [r1]
	ADD      r1, #1
	CMP      r0, r1
	BGE      |loc_080108F6|
	MOV      r5, #1
|loc_080108F6|
	CMP      r5, #0
	BEQ      |loc_08010970|
	LDR      r1, [r4]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	BL       |loc_080135D2|
	STR      r0, [sp, #0x6c]
	MOV      r0, #0
	MVN      r0, r0
	STR      r0, [sp, #0x70]
	ADD      r0, sp, #0x5c
	ADD      r1, r4, #0
	BL       |Object_WriteBounds1|
	LDR      r0, [sp, #0x5c]
	LDR      r1, [sp, #0x64]
	LDR      r3, [sp, #0x68]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x60]
	STR      r1, [sp, #0x54]
	ASR      r1, r1, #1
	ADD      r0, r0, r3
	STR      r0, [sp, #0x58]
	ASR      r0, r0, #1
	LDR      r2, [pc, #0x224]
	STR      r0, [sp, #0x58]
	STR      r1, [sp, #0x54]
	STR      r0, [r2, #4]
	STR      r1, [r2]
	MOV      r0, #0x40
	BL       |inc_0x03d784_0x041118| + 0x2348
	SUB      r0, #0x20
	ASR      r1, r0, #0x1f
	LSR      r1, r1, #0x1b
	ADD      r0, r1, r0
	ASR      r0, r0, #5
	LDR      r1, [pc, #0x210]
	LSL      r0, r0, #8
	STR      r0, [r1]
	ADD      r4, r1, #4
	MOV      r0, #0x40
	BL       |inc_0x03d784_0x041118| + 0x2348
	SUB      r0, #0x20
	ASR      r1, r0, #0x1f
	LSR      r1, r1, #0x1b
	ADD      r0, r1, r0
	ASR      r0, r0, #5
	LSL      r0, r0, #8
	STR      r0, [r4]
	MOV      r0, sp
	LDR      r1, [pc, #0x1f4]
	ADD      r2, sp, #0x6c
	BL       |loc_08004098|
|loc_08010970|
	ADD      sp, #0x7c
	POP      {r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	CMP      r1, #0
	BNE      |loc_0801099A|
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r0, [r0, #0x2c]
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800ED18|
	POP      {r4, pc}
|loc_0801099A|
	LSL      r0, r1, #2
	LDR      r1, [pc, #0x1a4]
	SUB      r1, #0x64
	LDR      r1, [r1, r0]
	ADD      r0, r4, #0
	BL       |loc_0800ED18|
	POP      {r4, pc}
