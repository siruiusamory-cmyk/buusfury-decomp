	CODE16
|loc_08021174|
	EXPORT |loc_08021174|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r2, #0
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08021188|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080211A6|
|loc_08021188|
	LDR      r1, [pc, #0xd4]
	MOV      r3, #0
	STMIA    r0!, {r1, r3}
	LDR      r2, [pc, #0xd4]
	SUB      r0, #8
	LDR      r1, [pc, #0xd4]
	STR      r2, [r0, #8]
	STR      r1, [r0]
	ADD      r1, #0x2c
	STR      r1, [r0, #8]
	LDMIA    r4!, {r2, r4}
	ADD      r0, #0xc
	STMIA    r0!, {r2, r4, r5}
	SUB      r0, #0x18
	STR      r3, [r0, #0x2c]
|loc_080211A6|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, lr}
	LDR      r5, [pc, #0xc0]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	SUB      sp, #0x14
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r0, [r0, #4]
	STR      r1, [sp, #0xc]
	STR      r0, [sp, #0x10]
	LDR      r2, [sp, #0x10]
	LSL      r1, r1, #0xa
	STR      r1, [r4, #0x20]
	LSL      r2, r2, #0xa
	STR      r2, [r4, #0x24]
	LDR      r2, [r4, #0x14]
	ADD      r1, r4, #0
	STR      r2, [sp]
	ADD      r2, r4, #0
	ADD      r2, #0x28
	ADD      r1, #0xc
	ADD      r0, sp, #0xc
	ADD      r3, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x3edc
	LDR      r0, [sp, #4]
	MOV      r1, #0
	LSL      r0, r0, #2
	STR      r0, [r4, #0x18]
	LDR      r0, [sp, #8]
	LSL      r0, r0, #2
	STR      r0, [r4, #0x1c]
	CMP      r4, #0
	BEQ      |loc_080211F0|
	ADD      r1, r4, #0
	ADD      r1, #8
|loc_080211F0|
	LDR      r0, [r5, #4]
	BL       |loc_08021094|
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r0, #0x18
	LDMIA    r0!, {r2}
	LDR      r1, [r4, #0x20]
	ADD      r5, r4, #0
	ADD      r1, r1, r2
	STR      r1, [r4, #0x20]
	LDR      r1, [r4, #0x24]
	LDR      r0, [r0]
	ADD      r5, #0x20
	ADD      r0, r1, r0
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x28]
	ADD      r6, r5, #4
	SUB      r0, #1
	STR      r0, [r4, #0x28]
	CMP      r0, #0
	LDR      r7, [pc, #0x4c]
	BNE      |loc_08021238|
	MOV      r0, #1
	STR      r0, [r4, #0x2c]
	LDR      r0, [r7, #4]
	BL       |loc_080210B6|
	LDR      r0, [r4, #0xc]
	LDR      r1, [r4, #0x10]
	LSL      r0, r0, #0xa
	STR      r0, [r5]
	LSL      r1, r1, #0xa
	STR      r1, [r6]
|loc_08021238|
	LDR      r0, [r7]
	ADD      r0, #0x80
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |sub_08021254|
	LDR      r0, [r7]
	LDR      r1, [r5]
	STMIA    r0!, {r1}
	LDR      r1, [r6]
	STR      r1, [r0]
	LDR      r0, [r7]
	BL       |sub_0802ed98|
	POP      {r3, r4, r5, r6, r7, pc}
