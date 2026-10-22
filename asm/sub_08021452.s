	CODE16
|sub_08021452|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	MOV      r0, #1
	STR      r0, [r4, #0x44]
	LDR      r0, [r4, #0x5c]
	ADD      r5, r1, #0
	LDR      r1, [r0, #4]
	ADD      r6, r2, #0
	ADD      r1, #0x18
	STR      r1, [r4, #0x18]
	LDRB     r2, [r1, #2]
	LDRB     r0, [r1, #3]
	LDR      r3, [pc, #0x11c]
	MUL      r2, r0
	LDRH     r0, [r4, #0xc]
	LDR      r1, [r1, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	MOV      r0, #0x37
	STRB     r0, [r4, #8]
	CMP      r5, #1
	BNE      |loc_08021490|
	LDR      r1, [r4, #0x24]
	LSL      r0, r5, #0xb
	SUB      r0, r1, r0
	STR      r0, [r4, #0x24]
|loc_08021490|
	LSL      r0, r5, #3
	LDR      r1, [pc, #0xf8]
	LDR      r3, [pc, #0xf8]
	LDR      r2, [r1, r0]
	ADD      r0, r0, r1
	MUL      r2, r6
	MUL      r2, r3
	ASR      r2, r2, #8
	STR      r2, [r4, #0x4c]
	LDR      r0, [r0, #4]
	MOV      r1, #1
	MUL      r0, r6
	MUL      r0, r3
	ASR      r0, r0, #8
	LSL      r1, r1, #9
	SUB      r0, r0, r1
	STR      r0, [r4, #0x50]
	LDR      r0, [pc, #0xb8]
	LDR      r5, [pc, #0xb8]
	LDR      r2, [pc, #0xbc]
	LDR      r0, [r0]
	SUB      r5, #0x24
	ADD      r1, r5, #0
	ADD      r1, #0x24
	ADD      r0, r0, r2
	ADD      r4, r0, #0
	BL       |inc_0x03d784_0x041118| + 0xb7e
	ADD      r1, r5, #0
	ADD      r1, #0xff
	ADD      r1, #0x99
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	POP      {r4, r5, r6, pc}
	PUSH     {r0, r1, r2, r3, r4, r5, r6, lr}
	ADD      r4, r0, #0
	MOV      r0, #1
	LDR      r5, [sp, #0x20]
	STR      r0, [r4, #0x44]
	LDR      r0, [r4, #0x5c]
	ADD      r6, r1, #0
	LDR      r1, [r0, #4]
	LDR      r3, [pc, #0x9c]
	ADD      r1, #0x18
	STR      r1, [r4, #0x18]
	LDRB     r2, [r1, #2]
	LDRB     r0, [r1, #3]
	MUL      r2, r0
	LDRH     r0, [r4, #0xc]
	LDR      r1, [r1, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	MOV      r0, #0x37
	STRB     r0, [r4, #8]
	CMP      r6, #1
	BNE      |loc_08021518|
	LDR      r1, [r4, #0x24]
	LSL      r0, r6, #0xb
	SUB      r0, r1, r0
	STR      r0, [r4, #0x24]
|loc_08021518|
	LDR      r1, [sp, #8]
	LDR      r3, [pc, #0x74]
	STR      r1, [r4, #0x4c]
	LDR      r1, [sp, #0xc]
	LDR      r2, [pc, #0x50]
	STR      r1, [r4, #0x50]
	LDR      r0, [r4, #0x4c]
	MUL      r1, r5
	MUL      r0, r5
	MUL      r0, r3
	ASR      r0, r0, #0x10
	STR      r0, [r4, #0x4c]
	ADD      r0, r1, #0
	MUL      r0, r3
	MOV      r1, #1
	LSL      r1, r1, #9
	ASR      r0, r0, #0x10
	SUB      r0, r0, r1
	STR      r0, [r4, #0x50]
	LDR      r0, [pc, #0x2c]
	LDR      r5, [pc, #0x2c]
	LDR      r0, [r0]
	SUB      r5, #0x24
	ADD      r1, r5, #0
	ADD      r1, #0x24
	ADD      r0, r0, r2
	ADD      r4, r0, #0
	BL       |inc_0x03d784_0x041118| + 0xb7e
	ADD      r1, r5, #0
	ADD      r1, #0xff
	ADD      r1, #0x99
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
|sub_08021566|
	DCW      0x0000
	DCW      0xa33c,0x0804,0x5090,0x0872,0x92cc,0x0831,0x05c4,0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xe454
|sub_08021582|
	LSR      r4, r0, #0x20
	STRH     r0, [r0, #6]
	LSR      r3, r5, #1
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	MOV      r6, #0x8c
	LSR      r7, r0, #0x20
	LSL      r4, r6, #0x17
	LSL      r0, r0, #0
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_080215B0|
	MOV      r0, #0x50
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080215B0|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
