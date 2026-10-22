	CODE16
|loc_080381DC|
	PUSH     {r4, r5, r6, r7}
	MOV      ip, r3
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r5, [sp, #0x10]
	LDR      r4, [r0, #0x54]
	LSL      r1, r1, #2
	ADD      r1, r4, r1
	MOV      r3, #0
	LDRSB    r6, [r1, r3]
	LDR      r4, [r0, #0x24]
	ADD      r3, r4, r6
	LDR      r4, [r5]
	LDR      r6, [r0, #0x28]
	ADD      r4, r3, r4
	MOV      r3, #1
	LDRSB    r7, [r1, r3]
	LDR      r5, [r5, #4]
	ADD      r3, r6, r7
	ADD      r3, r3, r5
	LDR      r7, [pc, #0x1c4]
	LDRB     r5, [r1, #2]
	LDRB     r6, [r1, #3]
	ADD      r7, #0x48
	LDR      r7, [r7, #8]
	ADD      r5, r4, r5
	ADD      r6, r3, r6
	CMP      r4, r7
	BGE      |loc_08038286|
	LDR      r7, [pc, #0x1b4]
	ADD      r7, #0x48
	LDR      r7, [r7]
	CMP      r7, r5
	BGE      |loc_08038286|
	LDR      r5, [pc, #0x1a8]
	ADD      r5, #0x48
	LDR      r7, [r5, #0xc]
	CMP      r3, r7
	BGE      |loc_08038286|
	LDR      r5, [r5, #4]
	CMP      r5, r6
	BGE      |loc_08038286|
	LDR      r5, [r2]
	LDR      r1, [r1, #4]
	LDR      r6, [pc, #0x198]
	STR      r1, [r5]
	LDR      r1, [r2]
	LSL      r4, r4, #0x17
	LDR      r5, [r1]
	LSR      r4, r4, #7
	AND      r5, r6
	ORR      r4, r5
	STR      r4, [r1]
	LSR      r4, r4, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r4, r4, #8
	LDR      r1, [r2]
	ORR      r3, r4
	STR      r3, [r1]
	LDRH     r1, [r0, #0xc]
	ADD      r3, r1, #0
	LDR      r1, [r2]
	ADD      r3, ip
	ADD      r1, #4
	LDR      r4, [r1]
	LSL      r3, r3, #0x16
	LSR      r4, r4, #0xa
	LSL      r4, r4, #0xa
	LSR      r3, r3, #0x16
	ORR      r3, r4
	STR      r3, [r1]
	LDRB     r0, [r0, #8]
	MOV      r4, #3
	LSL      r4, r4, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r3, r4
	LDR      r1, [r2]
	ORR      r0, r3
	STR      r0, [r1, #4]
	LDR      r0, [r2]
	ADD      r0, #8
	STR      r0, [r2]
|loc_08038286|
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_0803828A|
|unk_0803828A|
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r0, [r1]
		SUB sp, #0x1c
		STR r0, [sp, #0x10]
		ADD r6, r1, #0
		LDR r1, [r4, #0x2c]
		LDR r0, [r4, #0x3c]
		LDR r2, [r4, #0x30]
		MUL r1, r0
		MUL r2, r0
		ADD r0, r1, #0
		STR r0, [sp, #0x14]
		STR r2, [sp, #0xc]
		STR r2, [sp, #0x18]
		STR r1, [sp, #8]
		LDRB r0, [r4, #0x10]
		ADD r5, sp, #0x14
		ADD r7, sp, #0x10
		CMP r0, #2
		BEQ      |inc_0x351c0_0x3d4d0| + 0x3104
		STR r5, [sp]
		ADD r2, r7, #0
		MOV r1, #1
		ADD r0, r4, #0
		LDR r3, [r4, #0x48]
	INCBIN  baserom.gba_0x382be_0x382c0.extracted
|sub_080382C0|
|unk_080382C0|
	INCBIN	baserom.gba_0x382c0_0x382c4.extracted
	STR      r5, [sp]
	ADD      r2, r7, #0
	MOV      r1, #2
	ADD      r0, r4, #0
	LDR      r3, [r4, #0x4c]
	BL       |loc_080381DC|
	LDRB     r0, [r4, #8]
	ADD      r2, r7, #0
	MOV      r1, #3
	ADD      r0, #0xf6
	STRB     r0, [r4, #8]
	STR      r5, [sp]
	LDR      r3, [r4, #0x50]
	ADD      r0, r4, #0
	BL       |loc_080381DC|
	LDRB     r0, [r4, #8]
	ADD      r0, #0xa
	STRB     r0, [r4, #8]
	LDR      r0, [r4, #0x3c]
	MOV      r5, #0
	SUB      r0, #1
	CMP      r0, #0
	BLE      |loc_08038320|
|loc_080382F6|
	LDR      r0, [r4, #0x2c]
	LDR      r1, [r4, #0x30]
	MUL      r0, r5
	MUL      r1, r5
	STR      r0, [sp]
	ADD      r2, sp, #8
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	STR      r0, [sp, #8]
	MOV      r1, #0
	ADD      r2, r7, #0
	ADD      r0, r4, #0
	LDR      r3, [r4, #0x44]
	BL       |loc_080381DC|
	LDR      r0, [r4, #0x3c]
	ADD      r5, #8
	SUB      r0, #1
	CMP      r0, r5
	BGT      |loc_080382F6|
|loc_08038320|
	LDR      r0, [sp, #0x10]
	STR      r0, [r6]
	ADD      sp, #0x1c
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0xc
	CMP      r1, #0
	BEQ      |sub_0803834C|
	CMP      r1, #0xb
	BEQ      |loc_080383B6|
	CMP      r1, #0xc
	BNE      |loc_080383BA|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0
	ADD      sp, #0xc
	POP      {r4, r5, pc}
