	CODE16
|sub_0801E71E|
	LDR      r3, [r2, #0x30]
	MOV      r1, #2
	CMP      r3, #0
	BNE      |loc_0801E728|
	MOV      r1, #0x75
|loc_0801E728|
	STRB     r1, [r0, #3]
	LDR      r1, [pc, #0x20]
	SUB      r1, #0x14
	LDR      r1, [r1, #8]
	STR      r1, [r0, #0xc]
	LDR      r3, [r2, #0x20]
	LDR      r4, [r2, #0x24]
	STR      r3, [r0, #4]
	STR      r4, [r0, #8]
	LDR      r1, [r2, #0x1c]
	BL       |inc_0x03d784_0x041118| + 0x356
	POP      {r4, pc}
|sub_0801E742|
	DCW      0x0000
	DCW      0xe3d4,0x083b,0x6a2c,0x0805,0x080c,0x0872,0x0040,0x0600
	DCW      0xe358,0x0804,0x05c4,0x0000,0x9488,0x0831,0x920c,0x0804
	DCW      0xb5ac,0x0804,0x947c,0x0804,0x94d8,0x0804,0xf70d
|sub_0801E772|
	LSR      r3, r0, #0x20
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r0, [pc, #0x258]
	LDR      r1, [sp, #0x24]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r2, [pc, #0x254]
	LDR      r1, [pc, #0x254]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x2250
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x248]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r4, lr}
	SUB      sp, #0x20
	ADD      r4, r0, #0
	MOV      r0, #0x78
	STR      r0, [sp, #0x14]
	MOV      r2, #1
	STR      r2, [sp, #0x1c]
	MOV      r0, #0
	MOV      r1, #0
	STR      r1, [sp, #0x18]
	MVN      r0, r0
	MOV      r2, #0x78
	STR      r2, [sp, #0x10]
	MOV      r1, #0x5f
	STR      r1, [sp, #0xc]
	ADD      r2, r0, #0
	MOV      r1, #1
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r2, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #8]
	MOV      r3, #1
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7758
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0x86
	STR      r0, [sp, #0x14]
	MOV      r2, #1
	STR      r2, [sp, #0x1c]
	MOV      r0, #0
	MOV      r1, #1
	STR      r1, [sp, #0x18]
	MVN      r0, r0
	MOV      r2, #0x78
	STR      r2, [sp, #0x10]
	MOV      r1, #0x4f
	STR      r1, [sp, #0xc]
	ADD      r2, r0, #0
	MOV      r1, #0
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r2, #1
	ADD      r1, r4, #0
	STR      r0, [sp, #8]
	MOV      r3, #0
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7758
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0xe16
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	BL       |inc_0x03d784_0x041118| + 0x2a3e
	MOV      r1, #0
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x71dc
	BL       |inc_0x03d784_0x041118| + 0x29dc
	ADD      sp, #0x20
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x198]
	LDR      r0, [pc, #0x1a4]
	SUB      r3, #0x24
	LDR      r1, [r3, #4]
	MOV      r5, #0xff
	ADD      r0, r1, r0
	ADD      r5, #0x21
	MOV      r4, #1
	CMP      r2, #0
	LDR      r1, [pc, #0x198]
	LDR      r6, [pc, #0x18c]
	BEQ      |sub_0801E8DA|
	CMP      r2, #1
	BNE      |loc_0801E94C|
	MOV      r7, #0
	ADD      r3, r7, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r0, r5, #0
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801E89A|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STMIA    r0!, {r6, r7}
	STR      r7, [r1, #0xc]
	STR      r7, [r1, #8]
	SUB      r0, #8
	ADD      r2, r1, #0
	ADD      r2, #0x10
	STR      r7, [r1, #0x10]
	LDR      r3, [pc, #0x168]
	STRB     r7, [r2, #4]
	STR      r3, [r0]
	STR      r7, [r1, #0x18]
	STRB     r4, [r2, #0xc]
|loc_0801E89A|
	BL       |inc_0x03d784_0x041118| + 0x11c
	CMP      r0, #2
	BNE      |loc_0801E960|
	LDR      r3, [pc, #0x144]
	SUB      r3, #0x24
	LDR      r0, [r3, #0xc]
	BL       |inc_0x03d784_0x041118| + 0x2a16
	MOV      r0, #0xbf
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BEQ      |loc_0801E8D0|
	ADD      r3, r4, #0
	MOV      r2, #0xd
	MOV      r1, #0x5e
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x5308
	LDR      r0, [pc, #0x138]
	STR      r0, [r5]
	MOV      r0, #0xb
	LSL      r0, r0, #6
	ADD      r0, r5, r0
	STR      r7, [r0, #0x38]
|loc_0801E8D0|
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
