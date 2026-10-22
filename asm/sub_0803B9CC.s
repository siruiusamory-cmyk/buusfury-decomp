	CODE16
|sub_0803B9CC|
	LDR      r2, [sp, #0x3c]
	CMP      r7, #0
	STR      r2, [r0]
	LDR      r0, [sp, #0x40]
	STR      r0, [r1]
	BNE      |loc_0803B9DA|
	MOV      r7, #1
|loc_0803B9DA|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_0803B9FA|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0803B9FA|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [sp, #0x34]
	LDR      r1, [sp, #0x38]
	LSL      r0, r0, #8
	STR      r0, [sp, #0x2c]
	LDR      r0, [sp, #0x44]
	LSL      r1, r1, #8
	STR      r1, [sp, #0x30]
	LDR      r1, [r0, #4]
	LDR      r0, [sp, #0x2c]
	LDR      r2, [sp, #0x30]
	MUL      r0, r1
	MUL      r2, r1
	ASR      r1, r2, #8
	ASR      r0, r0, #8
	STR      r1, [sp, #8]
	STR      r1, [sp, #0x10]
	LSL      r1, r0, #8
	STR      r0, [sp, #4]
	STR      r0, [sp, #0xc]
	LSL      r7, r7, #8
	ADD      r0, r7, #0
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [sp]
	LDR      r0, [sp, #0x10]
	LSL      r1, r0, #8
	ADD      r0, r7, #0
	BL       |inc_0x046118_0x049114| + 0xd40
	LDR      r1, [sp]
	STR      r0, [sp, #8]
	ADD      r0, r1, #0
	STR      r1, [sp, #4]
	LDR      r1, [sp, #8]
	STR      r0, [sp, #0x14]
	STR      r1, [sp, #0x18]
	LDR      r0, [r5]
	LDR      r1, [sp, #0x14]
	ADD      r0, r0, r1
	LDR      r1, [r6]
	LDR      r2, [sp, #0x18]
	STR      r0, [sp, #4]
	ADD      r1, r1, r2
	STR      r1, [sp, #8]
	STR      r1, [sp, #0x28]
	STR      r1, [sp, #0x20]
	STR      r0, [sp, #0x24]
	STR      r0, [sp, #0x1c]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x54]
	ADD      r2, r2, r1
	ADD      r1, sp, #0x24
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |sub_0803BA84|
	LDR      r0, [sp, #0x24]
	STR      r0, [r5]
	LDR      r0, [sp, #0x28]
	STR      r0, [r6]
	B        |loc_0803BAEE|
