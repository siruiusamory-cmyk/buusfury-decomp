	CODE16
|sub_08006290|
	PUSH     {r4, r5, r6, lr}
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #1
	LDR      r1, [r2, #0x1c]
	LDR      r2, [r2, #0xc]
	MOV      r6, #1
	ADD      r4, r0, #0
	ADD      r0, r6, #0
	CMP      r2, #2
	SUB      sp, #0x38
	BGT      |loc_080062AA|
	MOV      r0, #0
|loc_080062AA|
	STR      r0, [r1, #8]
	MOV      r1, #0xf0
	MOV      r2, #0xa0
	ADD      r5, sp, #4
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r3, r6, #0
	MOV      r2, #2
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_08006718|
	LDR      r1, [pc, #0x2cc]
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	ADD      r0, sp, #4
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x38
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x2b8]
	SUB      sp, #0x24
	LDR      r5, [r0, #0x5c]
	LDR      r7, [r0, #0x68]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #0x84
	STR      r2, [sp]
	MOV      r0, #0
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r2, #0
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |loc_08013E64|
	MOV      r1, #0xff
	ADD      r1, #0x1d
	STR      r0, [r1, r4]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	LDR      r6, [pc, #0x28c]
	MOV      r1, #0
	LDR      r2, [r6, #4]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
	STR      r5, [sp]
	BL       |Object_Construct1|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	ADD      r1, r5, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x03d784_0x041118| + 0x2864
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	ADD      r5, r0, #0
	MOV      r1, #1
	ADD      r5, #0x1e
	MOV      r2, #0x84
	STR      r2, [sp]
	ADD      r3, r5, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r0, #0
	BL       |loc_08013E64|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	LDR      r2, [r6, #4]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	ADD      r2, r5, #0
	ADD      r2, #0x10
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x90
	MOV      r0, #0
	STR      r7, [sp]
	BL       |Object_Construct1|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	MOV      r0, #0x6d
	STR      r0, [sp, #4]
	MOV      r2, #0xdd
	STR      r2, [sp, #0xc]
	ADD      r0, r4, #0
	ADD      r0, #0xff
	MOV      r2, #0
	MOV      r1, #0x21
	MOV      r6, #0
	ADD      r3, r6, #0
	ADD      r0, #0x15
	CMP      r4, #0
	STR      r1, [sp, #8]
	STR      r2, [sp]
	BEQ      |loc_080063A2|
	ADD      r3, r0, #0
|loc_080063A2|
	ADD      r5, r3, #0
	ADD      r1, r4, #0
	MOV      r2, #0
	MOV      r0, #0
	BL       |Object_Construct2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	MOV      r2, #0xdd
	STR      r2, [sp, #0xc]
	MOV      r1, #0x33
	STR      r1, [sp, #8]
	MOV      r2, #1
	MOV      r0, #0x6d
	ADD      r3, r5, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	MOV      r0, #0
	STR      r2, [sp]
	BL       |Object_Construct2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	MOV      r2, #0xdd
	STR      r2, [sp, #0xc]
	MOV      r1, #0x45
	STR      r1, [sp, #8]
	MOV      r2, #2
	MOV      r0, #0x6d
	ADD      r3, r5, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	MOV      r0, #0
	STR      r2, [sp]
	BL       |Object_Construct2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	MOV      r2, #0
	MVN      r1, r2
	MOV      r0, #0x28
	STR      r0, [sp, #0x14]
	MOV      r0, #0
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x10
	MVN      r0, r0
	STR      r1, [sp, #0x18]
	MOV      r1, #0x10
	STR      r2, [sp, #0x10]
	ADD      r2, r0, #0
	STR      r1, [sp, #0xc]
	MOV      r1, #1
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r2, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #8]
	MOV      r3, #3
	MOV      r0, #0
	BL       |loc_080060A8|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	MOV      r2, #0
	MVN      r1, r2
	MOV      r0, #0x3a
	STR      r0, [sp, #0x14]
	MOV      r0, #0
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x10
	MVN      r0, r0
	STR      r1, [sp, #0x18]
	MOV      r1, #0x11
	STR      r2, [sp, #0x10]
	ADD      r2, r0, #0
	STR      r1, [sp, #0xc]
	MOV      r1, #2
	STR      r1, [sp]
	STR      r2, [sp, #4]
	ADD      r3, r6, #0
	ADD      r1, r4, #0
	MOV      r2, #1
	STR      r0, [sp, #8]
	MOV      r0, #0
	BL       |loc_080060A8|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	MOV      r2, #0
	MVN      r1, r2
	MOV      r0, #0x4c
	STR      r0, [sp, #0x14]
	MOV      r0, #0
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x10
	MVN      r0, r0
	STR      r1, [sp, #0x18]
	MOV      r1, #0x12
	STR      r2, [sp, #0x10]
	ADD      r2, r0, #0
	STR      r1, [sp, #0xc]
	MOV      r1, #3
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r2, #2
	ADD      r1, r4, #0
	STR      r0, [sp, #8]
	MOV      r3, #1
	MOV      r0, #0
	BL       |loc_080060A8|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	MOV      r2, #1
|unk_0800649E|
	INCBIN	baserom.gba_0x649e_0x64a0.extracted
	MOV      r0, #0x70
	STR      r0, [sp, #0x14]
	MOV      r0, #0
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x78
	MVN      r0, r0
	STR      r1, [sp, #0x18]
	MOV      r1, #0x14
	STR      r2, [sp, #0x10]
	ADD      r2, r0, #0
	STR      r1, [sp, #0xc]
	MOV      r1, #0
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r2, #3
	ADD      r1, r4, #0
	STR      r0, [sp, #8]
	MOV      r3, #2
	MOV      r0, #0
	BL       |loc_080060A8|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0xe16
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r0, #0xff
	ADD      r0, #0x19
	LDR      r1, [pc, #0xb0]
	LDR      r0, [r0]
	LDR      r1, [r1]
	CMP      r0, r1
	BEQ      |loc_08006500|
	LDR      r0, [pc, #0xa0]
	LDR      r0, [r0, #8]
	BL       |loc_08006B5E|
|loc_08006500|
	ADD      r0, r4, #0
	BEQ      |loc_08006510|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08006510|
	POP      {r4, pc}
	LDR      r1, [pc, #0x88]
	PUSH     {r4, lr}
	LDR      r1, [r1]
	LDR      r0, [pc, #0x88]
	MOV      r3, #0
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x88]
	CMP      r2, #0
	BEQ      |loc_0800655A|
	CMP      r2, #1
	BNE      |sub_0800658E|
	ADD      r4, r3, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #0xff
	ADD      r0, #0x1d
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08006552|
	LDR      r1, [pc, #0x6c]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r4, [r1, #0xc]
	STR      r4, [r1, #8]
	STR      r4, [r1, #0x10]
	LDR      r1, [pc, #0x60]
	STR      r1, [r0]
|loc_08006552|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r4, pc}
|loc_0800655A|
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r1, #0
	MOV      r0, #0
	BL       |inc_0x331c0_0x341c0| + 0x3fc
	BL       |inc_0x03d784_0x041118| + 0x11c
	BL       |Blend_WriteControl1|
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0x38]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x30]
	LDR      r0, [pc, #0x30]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r0, #0
	POP      {r4, pc}
