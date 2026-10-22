	CODE16
|loc_080051B0|
	PUSH     {r4, r5, r6}
	LDR      r4, [r0, #0x28]
	LDR      r5, [r0, #0x24]
	SUB      r3, r3, r2
	MUL      r4, r2
	ADD      r2, r5, r4
	ADD      r1, r2, r1
	MOV      r5, #0x2f
	STRB     r5, [r1]
	LDR      r2, [r0, #0x28]
	MOV      r4, #0x31
	ADD      r1, r2, r1
	SUB      r1, #1
	SUB      r3, #2
	CMP      r3, #0
	BEQ      |loc_080051E0|
	MOV      r6, #0x30
|loc_080051D2|
	STRB     r5, [r1]
	STRB     r6, [r1, #1]
	STRB     r4, [r1, #2]
	LDR      r2, [r0, #0x28]
	ADD      r1, r2, r1
	SUB      r3, #1
	BNE      |loc_080051D2|
|loc_080051E0|
	STRB     r4, [r1, #1]
	POP      {r4, r5, r6}
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r0, [pc, #0x218]
	LDR      r1, [sp, #0x24]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r2, [pc, #0x214]
	LDR      r1, [pc, #0x214]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x2250
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |loc_080066EC|
	LDR      r1, [pc, #0x208]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
