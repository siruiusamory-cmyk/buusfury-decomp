	CODE16
|loc_08018950|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r6, r0, #0
	ADD      r4, r1, #0
	CMP      r1, #0
	SUB      sp, #0x24
	BEQ      |loc_080189C8|
|loc_0801895E|
	MOV      r0, #0xff
	ADD      r0, #0xf1
	LDR      r5, [r0, r4]
	ADD      r0, sp, #0x14
	ADD      r1, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x74]
	ADD      r3, r2, r1
	ADD      r2, r7, #0
	LDR      r1, [r6, #0xc]
	BL       |inc_0x046118_0x049114| + 0x98e
	ADD      r1, r4, #0
	LDR      r4, [pc, #0x80]
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_080189C4|
	LDR      r0, [sp, #0x14]
	LDR      r1, [sp, #0x1c]
	LDR      r2, [sp, #0x20]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x18]
	STR      r1, [sp, #4]
	ADD      r0, r0, r2
	STR      r0, [sp, #8]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	ADD      r3, sp, #0xc
	ADD      r1, r3, #0
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x10]
	MOV      r2, #0x38
	MOV      r0, #0
	BL       |loc_0801952C|
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_080189C4|
	ADD      r4, r5, #0
	BNE      |loc_0801895E|
|loc_080189C8|
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	LDRB     r4, [r1, #0x10]
	SUB      sp, #0x20
	MOV      r3, #1
	EOR      r4, r3
	ADD      r3, sp, #0
	STRB     r4, [r3, #4]
	LDR      r0, [r0, #4]
	ADD      r2, sp, #4
	BL       |loc_08018950|
	MOV      r0, #0
	ADD      sp, #0x20
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080189FC|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_080189FC|
	POP      {r4, pc}
	LSL      r0, r0, #0
	BGE      |loc_08018A34|
	LSR      r7, r5, #1
	LDR      r4, [sp, #0x20]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x10
	SUB      sp, #0xc
	STR      r0, [r4, #0x10]
	MOV      r0, #5
	LSL      r0, r0, #7
	ADD      r0, r1, r0
	LDR      r0, [r0, #0x14]
	ADD      r5, r1, #0
	CMP      r0, #0
	BEQ      |loc_08018A26|
	LDR      r0, [r4, #0xc]
	LSL      r0, r0, #2
	STR      r0, [r4, #0xc]
