	CODE16
|sub_08027E42|
	LSR      r4, r0, #0x20
	DCW      0xea50,0x0874
|loc_08027E48|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRH     r0, [r0, #0xc]
	SUB      sp, #0x14
	LDR      r1, [pc, #0x2b8]
	LSL      r0, r0, #5
	ADD      r1, r0, r1
	MOV      r7, #0
	MOV      r6, #0x40
	ADD      r0, r4, #0
	ADD      r0, #0x34
	ADD      r5, r0, #0
	STR      r6, [sp, #0xc]
	STR      r6, [sp, #0x10]
	STR      r7, [sp, #4]
	STR      r7, [sp, #8]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x298]
	STR      r6, [sp, #4]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSL      r1, r6, #6
	ADD      r1, r0, r1
	MOV      r0, #0x80
	STR      r0, [sp, #0xc]
	ADD      r0, r5, #0
	STR      r7, [sp, #8]
	STR      r6, [sp, #0x10]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x27c]
	STR      r7, [sp, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSL      r1, r6, #7
	ADD      r1, r0, r1
	MOV      r0, #0x80
	STR      r0, [sp, #4]
	MOV      r0, #0xa0
	STR      r0, [sp, #0xc]
	ADD      r0, r5, #0
	STR      r6, [sp, #0x10]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	SUB      r0, #1
	STR      r0, [r4, #0x14]
	BNE      |loc_08027ED2|
	ADD      r0, r4, #0
	ADD      r0, #0x29
	MOV      r2, #5
	ADD      r5, r0, #0
	LDR      r1, [pc, #0x248]
	BL       |inc_0x046118_0x049114| + 0xb3c
	MOV      r6, #2
	CMP      r0, #0
	BNE      |loc_08027ED4|
	STR      r6, [r4, #0x10]
|loc_08027ED2|
	POP      {r4, r5, r6, pc}
|loc_08027ED4|
	ADD      r1, r4, #0
	ADD      r1, #0x24
	MOV      r2, #5
	ADD      r0, r5, #0
	BL       |inc_0x046118_0x049114| + 0xb3c
	CMP      r0, #0
	BNE      |loc_08027EE8|
	STR      r6, [r4, #0x10]
	POP      {r4, r5, r6, pc}
|loc_08027EE8|
	MOV      r0, #1
	STR      r0, [r4, #0x10]
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x18]
	SUB      sp, #0x14
	ADD      r0, #1
	STR      r0, [r4, #0x18]
	CMP      r0, #0x20
	BLT      |loc_08027F02|
	LDR      r1, [pc, #0x214]
	STR      r1, [r4, #0x30]
|loc_08027F02|
	LSL      r1, r0, #0x1d
	BNE      |loc_08027F68|
	LSL      r0, r0, #0x1c
	BPL      |sub_08027F6C|
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x1fc]
	MOV      r7, #0
	LSL      r0, r0, #5
	ADD      r1, r0, r1
	MOV      r6, #0x40
	ADD      r0, r4, #0
	ADD      r0, #0x68
	ADD      r5, r0, #0
	STR      r6, [sp, #0xc]
	STR      r6, [sp, #0x10]
	STR      r7, [sp, #4]
	STR      r7, [sp, #8]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x1dc]
	STR      r6, [sp, #4]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSL      r1, r6, #6
	ADD      r1, r0, r1
	MOV      r0, #0x80
	STR      r0, [sp, #0xc]
	ADD      r0, r5, #0
	STR      r7, [sp, #8]
	STR      r6, [sp, #0x10]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x1c0]
	STR      r7, [sp, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSL      r1, r6, #7
	ADD      r1, r0, r1
	MOV      r0, #0x80
	STR      r0, [sp, #4]
	MOV      r0, #0xa0
	STR      r0, [sp, #0xc]
	ADD      r0, r5, #0
	STR      r6, [sp, #0x10]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
|loc_08027F68|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
