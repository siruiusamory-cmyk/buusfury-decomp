	CODE16
|sub_08021A4E|
	LDR      r0, [r4, #4]
	STR      r0, [r7, #0x18]
	LDR      r0, [pc, #0x164]
	LDR      r0, [r0, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x41a4
	LDR      r1, [pc, #0x184]
	LDR      r0, [r7, #0x14]
	BL       |inc_0x0158_0x143f2| + 0x10a60
	LDR      r1, [pc, #0x17c]
	LDR      r0, [r7, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x10a60
	LDR      r0, [r7, #0x14]
	BL       |inc_0x0158_0x143f2| + 0x104dc
	LDR      r0, [r7, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x104dc
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08021A8C|
	LDR      r1, [pc, #0x160]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #4]
	MOV      r1, #4
	STR      r1, [r0, #8]
|loc_08021A8C|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r7, [pc, #0x120]
	LDRB     r0, [r7]
	LDRB     r1, [r7, #1]
	ADD      r7, r0, r1
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08021AAC|
	ADD      r1, r7, #0
	ADD      r1, #0x6a
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x13c]
	STR      r1, [r0]
|loc_08021AAC|
	BL       |inc_0x03d784_0x041118| + 0x11c
	ADD      r2, r4, #4
	LDR      r7, [pc, #0x104]
	LDMIA    r2!, {r1, r2}
	LDR      r0, [r7, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x45ca
	MOV      r3, #0x64
	MOV      r2, #0
	MOV      r0, #0
	LDR      r1, [r4, #8]
	BL       |inc_0x153f2_0x1a3f2| + 0x41b6
	ADD      r1, r0, #0
	LDR      r0, [r7, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0xe0]
	LDRB     r0, [r1]
	LDRB     r1, [r1, #1]
	ADD      r7, r0, r1
	LDR      r1, [r4, #4]
	MOV      r0, #0x34
	STR      r1, [sp, #0xe0]
	LDR      r1, [r4, #8]
	STR      r1, [sp, #0xe4]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08021AF8|
	LDR      r1, [pc, #0x100]
	STR      r1, [r0]
	STR      r7, [r0, #0x10]
	LDR      r1, [sp, #0xe0]
	STR      r1, [r0, #8]
	LDR      r1, [sp, #0xe4]
	STR      r1, [r0, #0xc]
|loc_08021AF8|
	BL       |inc_0x03d784_0x041118| + 0x11c
	ADD      r7, r0, #0
	LDR      r0, [pc, #0xb8]
	LDR      r0, [r0, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x460c
	LDR      r0, [pc, #0xb0]
	MOV      r2, #0
	MOV      r1, #0x13
	LDR      r0, [r0, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	LDR      r0, [pc, #0xa4]
	MOV      r2, #0
	MOV      r1, #0xf
	LDR      r0, [r0, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x11ab4
	CMP      r7, #1
	BEQ      |sub_08021B4A|
	CMP      r7, #2
	BEQ      |loc_08021B54|
	CMP      r7, #3
	BEQ      |loc_08021B5C|
	CMP      r7, #0xff
	BNE      |loc_08021B5C|
	LDR      r7, [pc, #0x88]
	LDR      r0, [r7, #0x30]
	BL       |inc_0x03d784_0x041118| + 0x2a16
	BL       |inc_0x03d784_0x041118| + 0x29ca
	LDR      r1, [pc, #0xb4]
	LDR      r0, [r7, #4]
	ADD      r0, r0, r1
	BL       |inc_0x03d784_0x041118| + 0xb68
	MOV      r0, #2
	ADD      sp, #0xec
	POP      {r4, r5, r6, r7, pc}
