	CODE16
|Gfx_BuildVitalBars|
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x1fc
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	LDR      r0, [r1]
	LDR      r2, [pc, #0x2c0]
	SUB      sp, #0x1fc
	SUB      sp, #0x114
	STR      r2, [r0]
	LDR      r6, [r4, #0x28]
	LSL      r3, r6, #0x18
	LSR      r3, r3, #0x18
	ORR      r2, r3
	STR      r2, [r0]
	LDRH     r2, [r4, #0xc]
	LDR      r3, [r0, #4]
	LSR      r6, r3, #0xa
	LSL      r2, r2, #0x16
	LSR      r2, r2, #0x16
	LSL      r6, r6, #0xa
	ORR      r6, r2
	ADD      r3, r6, #0
	MOV      r2, #3
	LSL      r2, r2, #0xa
	MOV      r6, #1
	LSL      r6, r6, #0xa
	BIC      r3, r2
	ADD      r7, r3, r6
	STR      r7, [r0, #4]
	LDR      r7, [pc, #0x294]
	ADD      r0, #8
	STR      r7, [r0]
	LDR      r3, [r4, #0x28]
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	ORR      r7, r3
	STR      r7, [r0]
	LDRH     r7, [r4, #0xc]
	LDR      r3, [r0, #4]
	ADD      r7, #0x10
	MOV      ip, r7
	LSR      r7, r3, #0xa
	MOV      r3, ip
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	LSL      r7, r7, #0xa
	ORR      r7, r3
	BIC      r7, r2
	ADD      r7, r7, r6
	STR      r7, [r0, #4]
	LDR      r7, [pc, #0x26c]
	ADD      r0, #8
	STR      r7, [r0]
	LDR      r3, [r4, #0x28]
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	ORR      r7, r3
	STR      r7, [r0]
	LDRH     r7, [r4, #0xc]
	LDR      r3, [r0, #4]
	ADD      r7, #0x18
	MOV      ip, r7
	LSR      r7, r3, #0xa
	MOV      r3, ip
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	LSL      r7, r7, #0xa
	ORR      r7, r3
	BIC      r7, r2
	ADD      r2, r7, r6
	STR      r2, [r0, #4]
	ADD      r0, #8
	ADD      r6, r5, #0
	ADD      r6, #0x16
	MOV      r3, #0
	STR      r0, [r1]
	LDRSH    r0, [r6, r3]
	CMP      r0, #0
	BEQ      |loc_0800BA6E|
	LDRSH    r0, [r6, r3]
	LSL      r3, r0, #2
	ADD      r0, r3, r0
	ADD      r1, r6, #2
	MOV      r3, #0
	LDRSH    r1, [r1, r3]
	CMP      r0, r1
	BGT      |loc_0800BA6E|
	LDR      r0, [pc, #0x228]
	LDR      r0, [r0, #4]
	LDR      r1, [r4, #0x10]
	SUB      r1, r0, r1
	CMP      r1, #0x3c
	BLE      |loc_0800BA6E|
	STR      r0, [r4, #0x10]
	LDR      r0, [pc, #0x1f0]
	LDR      r1, [pc, #0x204]
	LDR      r3, [pc, #0x204]
	LDR      r0, [r0, #4]
	MOV      r7, #0
	MOV      r2, #0x20
	ADD      r1, #0xc
	ADD      r0, r0, r3
	ADD      r3, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_0800BA6E|
	MOV      r3, #2
	LDRSH    r1, [r6, r3]
	MOV      r3, #0
	LDRSH    r0, [r6, r3]
	MOV      r6, #0x29
	MUL      r0, r6
	SWI      6
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	STRB     r0, [r3]
	ADD      r0, r5, #0
	ADD      r0, #0x1a
	MOV      r3, #2
	LDRSH    r1, [r0, r3]
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	MUL      r0, r6
	SWI      6
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	ADD      r6, r5, #0
	ADD      r6, #0x1c
	STRB     r0, [r3, #1]
	MOV      r3, #0
	LDRSH    r1, [r6, r3]
	ADD      r0, r6, #2
	LDRH     r0, [r0]
	MOV      r3, #0x29
	MUL      r0, r3
	SWI      6
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	STRB     r0, [r3, #2]
	MOV      r3, #0
	LDRSH    r1, [r6, r3]
	ADD      r0, r6, #4
	LDRH     r0, [r0]
	MOV      r3, #0x29
	MUL      r0, r3
	SWI      6
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	STRB     r0, [r3, #3]
	MOV      r1, #0x48
	ADD      r0, r5, #0
	BL       |Stats_GetXpProgress|
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	STRB     r0, [r3, #4]
	LDR      r0, [r5, #4]
	ASR      r0, r0, #0xf
	STRB     r0, [r3, #5]
	LDRB     r1, [r5, #0x15]
	ADD      r0, r5, #0
	BL       |loc_080135A2|
	ADD      r6, r0, #0
	LDR      r1, [r0, #0x10]
	ADD      r0, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |sub_0800BAFC|
	LDR      r0, [r6, #4]
	B        |sub_0800BAFE|
