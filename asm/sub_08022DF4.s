	CODE16
|sub_08022DF4|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x290]
	ADD      r5, r0, #0
	LDR      r1, [r6, #0x10]
	MOV      r0, #0x20
	LDRB     r1, [r1]
	SUB      sp, #0xc
	CMP      r1, #1
	BEQ      |loc_08022E0C|
	LDR      r0, [pc, #0x290]
	ADD      r0, r5, r0
	LDR      r0, [r0]
|loc_08022E0C|
	STR      r0, [sp]
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #0x41
	STR      r0, [sp, #8]
	LDRB     r0, [r0]
	ADD      r4, r5, #0
	ADD      r4, #0xff
	ADD      r4, #1
	CMP      r0, #0
	BEQ      |sub_08022E8C|
	CMP      r0, #1
	BEQ      |loc_08022EF2|
	CMP      r0, #2
	BEQ      |loc_08022EF4|
	CMP      r0, #3
	BNE      |loc_08022EAC|
	LDR      r0, [r4, #0x3c]
	CMP      r0, #0
	BEQ      |loc_08022E3C|
	ADD      r1, r0, #0
	LDR      r0, [r6, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08022E3C|
	LDR      r0, [r4, #0x38]
	STR      r0, [r4, #0x3c]
	LDR      r0, [r4, #0x34]
	STR      r0, [r4, #0x38]
	LDR      r0, [r4, #0x30]
	STR      r0, [r4, #0x34]
	LDR      r1, [r4, #0x2c]
	STR      r1, [r4, #0x30]
	MOV      r1, #0
	STR      r1, [r4, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #0x38]
	CMP      r0, #0
	BEQ      |loc_08022E6E|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08022E6E|
	LDR      r0, [r4, #0x1c]
	CMP      r0, #2
	BMI      |loc_08022E86|
	SUB      r1, r0, #2
	ADD      r0, r5, #0
	BL       |loc_08022DAA|
	ADD      r1, r0, #0
	STR      r0, [r4, #0x2c]
	LDR      r0, [r6, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08022E86|
	MOV      r0, #0
	MOV      r6, #0x6a
	B        |sub_0802304E|
