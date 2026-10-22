	CODE16
|Blend_WriteControlAndAlpha4|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	MOV      r0, #3
	MOV      r2, #0x40
	MOV      r1, #0
	LSL      r0, r0, #0x19
	SUB      sp, #0x14
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0x1e
	STR      r0, [sp, #0xc]
	MOV      r0, #0x14
	MOV      r4, #0
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	STR      r4, [sp, #4]
	STR      r4, [sp, #8]
	MOV      r2, #1
	LDR      r1, [pc, #0xe8]
	BL       |inc_0x03d784_0x041118| + 0x28c
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0xe0]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0xf
	STR      r0, [sp, #4]
	MOV      r0, #0xb
	STR      r0, [sp, #8]
	MOV      r0, #0x1c
	STR      r0, [sp, #0xc]
	MOV      r0, #0x12
	STR      r0, [sp, #0x10]
	MOV      r2, #0x13
	LSL      r2, r2, #5
	ADD      r0, sp, #4
	LDR      r1, [pc, #0xc4]
	BL       |inc_0x03d784_0x041118| + 0x28c
	MOV      r1, #0
	MOV      r0, #0
	BL       |loc_080271D0|
	MOV      r1, #0xb
	LSL      r1, r1, #8
	ADD      r6, r5, r1
	LDR      r7, [pc, #0x94]
	STR      r0, [r6]
	ADD      r1, r0, #0
	LDR      r0, [r7, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r1, #1
	MOV      r0, #0
	BL       |loc_080271D0|
	MOV      r1, #0x2b
	LSL      r1, r1, #6
	ADD      r1, r5, r1
	STR      r0, [r1, #0x3c]
	ADD      r1, r0, #0
	LDR      r0, [r7, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r1, #2
	MOV      r0, #0
	BL       |loc_080271D0|
	ADD      r1, r0, #0
	STR      r0, [r6, #4]
	LDR      r0, [r7, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r1, #3
	MOV      r0, #0
	BL       |loc_080271D0|
	ADD      r1, r0, #0
	STR      r0, [r6, #8]
	LDR      r0, [r7, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r0, r5, #0
	BL       |loc_08025056|
	LDR      r1, [pc, #0x68]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #0xc]
	ADD      r1, #0xff
	ADD      r1, #1
	STRH     r1, [r0, #0xe]
	STRH     r4, [r0, #0x18]
	STRH     r4, [r0, #0x1a]
	STRH     r4, [r0, #0x1c]
	STRH     r4, [r0, #0x1e]
	MOV      r1, #0x52
	STRB     r4, [r1, r0]
	LDR      r1, [pc, #0x50]
	LDR      r2, [pc, #0x38]
	STRB     r4, [r1]
	LDR      r1, [pc, #0x50]
	STRH     r1, [r2, #0x10]
	MOV      r1, #0x71
	LSL      r1, r1, #6
	STRH     r1, [r0]
	LSR      r2, r0, #0x11
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0x44]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x38]
	LDR      r0, [pc, #0x3c]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_080256B8|
	DCW      0xd380
	DCW      0x0874,0x19cc,0x0873,0xbce8,0x0806,0x3e41,0x0000,0x0040
	DCW      0x0400,0x05c4,0x0000,0x947c,0x0831,0xf800
|sub_080256D6|
	LSL      r0, r0, #0x18
	DCW      0xf000,0x0600
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	LSL      r3, r2, #1
	LSL      r0, r0, #0x10
	SUB      r7, #0x5f
	LSL      r0, r0, #0
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	LSL      r0, r0, #8
	LSL      r0, r0, #0x14
|loc_080256F0|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BNE      |loc_08025704|
	LDR      r0, [pc, #0x3dc]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08025704|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_08025704|
	ADD      r0, r4, #0
	BL       |loc_08024A7C|
	LDR      r0, [pc, #0x3cc]
	MOV      r1, #0
	STR      r0, [r4]
	MOV      r0, #1
	LSL      r0, r0, #0xf
	ADD      r0, r4, r0
	STR      r1, [r0, #0x3c]
	LDR      r0, [pc, #0x3c0]
	ADD      r0, r4, r0
	STR      r1, [r0]
	STR      r1, [r0, #4]
	ADD      r1, #0xf0
	STR      r1, [r0, #8]
	LDR      r1, [r0, #4]
	ADD      r1, #0xa0
	STR      r1, [r0, #0xc]
	LDR      r0, [pc, #0x3b4]
	LDR      r0, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0x49b0
	LDR      r1, [pc, #0x3b0]
	ADD      r1, r4, r1
	STR      r0, [r1]
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_0802573C|
	LDR      r2, [pc, #0x3a8]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0802574A|
	BL       |GBARam_Free|
|loc_0802574A|
	POP      {r3, pc}
|loc_0802574C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	MOV      r1, #0
	SUB      sp, #0xec
	BL       |loc_08024A9C|
	ADD      r0, r4, #0
	ADD      r0, #0xc
	MOV      r2, #1
	LSL      r2, r2, #0xf
	MOV      r1, #0
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0x384]
	MOV      r3, #0
	ADD      r7, r4, r0
	STR      r3, [r7]
	STR      r3, [r7, #4]
	STR      r3, [r7, #8]
	SUB      r0, #0x10
	ADD      r0, r4, r0
	STR      r3, [r7, #0xc]
	STR      r3, [r0]
	STR      r3, [r0, #4]
	STR      r3, [r0, #8]
	STR      r3, [r0, #0xc]
	LDR      r0, [pc, #0x360]
	MOV      r1, #0
	ADD      r0, r4, r0
	STR      r0, [sp, #0xe8]
	STR      r1, [sp, #0xe0]
	LDR      r0, [r0]
	MOV      lr, r7
	CMP      r0, #0
	BEQ      |loc_08025876|
	LDR      r0, [r0, #0x14]
	MOV      ip, r1
	CMP      r0, #0
	BLE      |loc_08025878|
	LDR      r0, [sp, #0xe8]
	MOV      r1, ip
	LDR      r0, [r0]
	LSL      r1, r1, #2
	ADD      r0, r0, r1
	LDR      r5, [r0, #0x18]
	LDR      r3, [pc, #0x338]
	LDRH     r0, [r5, #2]
	LDR      r1, [r3, #8]
	LSR      r2, r0, #3
	ADD      r1, r2, r1
	LSL      r2, r0, #0x1d
	ADD      r1, #0x80
	LDRB     r1, [r1, #0xd]
	LSR      r2, r2, #0x1d
	MOV      r0, #1
	LSL      r0, r2
	AND      r1, r0
	BEQ      |sub_080257DA|
	LDR      r2, [r5, #0xc]
	LDR      r3, [r5, #4]
	LDR      r1, [r5, #8]
	SUB      r2, r2, r3
	LDR      r3, [r5, #0x10]
	ADD      r0, r5, #0
	SUB      r1, r3, r1
	MUL      r2, r1
	LSL      r1, r2, #1
	ADD      r6, r1, r5
	ADD      r0, #0x14
	ADD      r6, #0x24
	B        |sub_080257EC|
