	CODE16
|Object_Construct2|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r7, sp, #0x2c
	LDMIA    r7!, {r4, r6, r7}
	LDR      r5, [sp, #0x28]
	CMP      r0, #0
	BNE      |loc_08006898|
	MOV      r0, #0x20
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080068B4|
|loc_08006898|
	LDR      r1, [sp, #8]
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x208]
	STR      r1, [r0]
	LDR      r1, [sp, #0xc]
	STR      r1, [r0, #8]
	LDR      r1, [sp, #0x10]
	ADD      r0, #0xc
	STMIA    r0!, {r1, r4, r6}
	SUB      r0, #0x18
	SUB      r1, r7, r4
	SUB      r1, #2
	STR      r5, [r0, #0x1c]
	STR      r1, [r0, #0x18]
|loc_080068B4|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0xc]
	ADD      r6, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0xc
	LDR      r2, [r1]
	ADD      r2, r2, r1
	LDR      r1, [r4, #0x1c]
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [r4, #0x18]
	MUL      r0, r1
	ADD      r5, r0, #0
	LDR      r0, [r4, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	LDR      r1, [r4, #0x1c]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0xd40
	ADD      r7, r0, #0
	LDR      r0, [r4, #0x14]
	LDR      r1, [r6, #0x28]
	MUL      r0, r1
	LDR      r1, [r6, #0x24]
	ADD      r0, r0, r1
	LDR      r1, [r4, #0x10]
	LDR      r2, [r4, #0x18]
	ADD      r5, r0, r1
	CMP      r7, #0
	BNE      |sub_08006938|
	MOV      r1, #1
	ADD      r0, r5, r1
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r6, #0x28]
	ADD      r5, r0, r5
|loc_0800690A|
	MOV      r0, #0x73
	STRB     r0, [r5]
	MOV      r1, #0x70
	ADD      r0, r5, #1
	LDR      r2, [r4, #0x18]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x18]
	MOV      r1, #1
	ADD      r0, r0, r5
	STRB     r1, [r0, #1]
	LDR      r0, [r6, #0x28]
	ADD      r7, r7, r1
	ADD      r5, r0, r5
	CMP      r7, #3
	BLT      |loc_0800690A|
	MOV      r1, #0x73
	ADD      r0, r5, #1
	LDR      r2, [r4, #0x18]
	BL       |inc_0x046118_0x049114| + 0xd28
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
