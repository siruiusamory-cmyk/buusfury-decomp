	CODE16
|loc_08013678|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x28c]
	SUB      sp, #0x10
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0, #0xc]
	LDR      r1, [pc, #0x280]
	LDR      r6, [sp, #0x14]
	LSL      r0, r0, #5
	ADD      r5, r0, r1
	ADD      r7, r2, #0
	CMP      r6, r7
	BGE      |loc_08013742|
|loc_0801369A|
	MOV      r0, #0xff
	ADD      r0, #1
	BL       |inc_0x03d784_0x041118| + 0x2348
	STR      r0, [sp, #0xc]
	MOV      r0, #0xff
	ADD      r0, #1
	BL       |inc_0x03d784_0x041118| + 0x2348
	STR      r0, [sp, #8]
	MOV      r0, #0xff
	ADD      r0, #1
	BL       |inc_0x03d784_0x041118| + 0x2348
	STR      r0, [sp, #4]
	MOV      r0, #0xff
	ADD      r0, #1
	BL       |inc_0x03d784_0x041118| + 0x2348
	MOV      r3, #0x18
	LDRSH    r1, [r4, r3]
	LDR      r2, [r5]
	LDR      r3, [sp, #0xc]
	MUL      r2, r3
	LDR      r3, [r5, #4]
	LSR      r2, r2, #8
	ADD      r2, r2, r3
	LSR      r2, r2, #0x10
	ADD      r1, r2, r1
	LDR      r2, [r5, #8]
	LDR      r3, [sp, #8]
	MUL      r2, r3
	LDR      r3, [r5, #0xc]
	LSR      r2, r2, #8
	ADD      r2, r2, r3
	MUL      r2, r1
	LSR      r2, r2, #0x10
	ADD      r1, r2, r1
	LSL      r1, r1, #0x10
	ASR      r1, r1, #0x10
|loc_080136EA|
	STRH     r1, [r4, #0x16]
	MOV      r3, #0x16
	LDRSH    r2, [r4, r3]
	CMP      r2, r1
	BNE      |loc_080136EA|
|loc_080136F4|
	STRH     r1, [r4, #0x18]
	MOV      r3, #0x18
	LDRSH    r2, [r4, r3]
	CMP      r2, r1
	BNE      |loc_080136F4|
	MOV      r3, #0x1c
	LDRSH    r1, [r4, r3]
	LDR      r2, [r5, #0x10]
	LDR      r3, [sp, #4]
	MUL      r2, r3
	LDR      r3, [r5, #0x14]
	ADD      r2, r2, r3
	LSR      r2, r2, #0x10
	ADD      r1, r2, r1
	LDR      r2, [r5, #0x18]
	MUL      r2, r0
	LSR      r0, r2, #8
	LDR      r2, [r5, #0x1c]
	ADD      r0, r0, r2
	MUL      r0, r1
	LSR      r0, r0, #0x10
	ADD      r0, r0, r1
	LSL      r0, r0, #0x10
	ASR      r0, r0, #0x10
	ADD      r2, r0, #0
|loc_08013726|
	STRH     r0, [r4, #0x1a]
	MOV      r3, #0x1a
	LDRSH    r1, [r4, r3]
	CMP      r1, r0
	BNE      |loc_08013726|
	ADD      r0, r2, #0
|loc_08013732|
	STRH     r0, [r4, #0x1c]
	MOV      r3, #0x1c
	LDRSH    r1, [r4, r3]
	CMP      r1, r0
	BNE      |loc_08013732|
	ADD      r6, #1
	CMP      r6, r7
	BLT      |loc_0801369A|
|loc_08013742|
	LDR      r6, [sp, #0x14]
	LDRH     r1, [r4, #0x2c]
	SUB      r0, r7, r6
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	ADD      r0, r1, r0
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
|loc_08013752|
	STRH     r0, [r4, #0x2c]
	LDRH     r1, [r4, #0x2c]
	CMP      r1, r0
	BNE      |loc_08013752|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
