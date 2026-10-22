	CODE16
|loc_080167A0|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	SUB      sp, #0x1fc
	SUB      sp, #0x1fc
	ADD      r4, r1, #0
	MOV      r1, #1
	SUB      sp, #0x28
	STRB     r1, [r4, #2]
	LDR      r1, [pc, #0x2e4]
	ADD      r3, sp, #0x3fc
	STR      r1, [r4, #0x20]
	LDR      r1, [pc, #0x2e0]
	ADD      r5, r0, #0
	LDR      r1, [r1, #8]
	ADD      r5, #0xff
	STR      r1, [r4, #0xc]
	LDR      r1, [r3, #0x2c]
	ADD      r5, #1
	LDR      r1, [r1]
	LDR      r6, [pc, #0x2d4]
	CMP      r1, #0
	BNE      |sub_08016800|
	MOV      r0, #1
	STRB     r0, [r4]
	MOV      r0, #0x78
	STR      r0, [r4, #4]
	MOV      r0, #0x58
	STR      r0, [r4, #8]
	LDR      r1, [r5, #0x1c]
	MOV      r0, #0x4b
	CMP      r1, #0
	BEQ      |loc_080167E0|
	MOV      r0, #0x4c
|loc_080167E0|
	LSL      r0, r0, #2
	LDR      r1, [r6, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	LDR      r0, [r5, #0x28]
	MOV      r1, #0
	STR      r1, [r0, #0x10]
	STR      r1, [r0, #8]
	LDR      r0, [r5, #0x2c]
	STR      r1, [r0, #0x10]
	STR      r1, [r0, #8]
	ADD      sp, #0x1fc
	ADD      sp, #0x1fc
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
