	CODE16
|sub_08027F74|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x18]
	ADD      r0, #1
	STR      r0, [r4, #0x18]
	CMP      r0, #0x10
	BLT      |loc_08027FB6|
	MOV      r1, #0x8c
	LDR      r2, [pc, #0x190]
	LDR      r1, [r1, r4]
	LDR      r0, [r4, #0x58]
	LDR      r2, [r2, #4]
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0x50
	STR      r0, [r4, #0x38]
	MOV      r0, #0x1c
	STR      r0, [r4, #0x3c]
	MOV      r0, #0x4b
	LDR      r1, [pc, #0x180]
	LSL      r0, r0, #3
	LDR      r1, [r1, r0]
	ADD      r0, r4, #0
	ADD      r0, #0x34
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r0, r4, #0
	BL       |loc_08027E48|
	LDR      r0, [pc, #0x170]
	STR      r0, [r4, #0x30]
	MOV      r0, #0
	STR      r0, [r4, #0x18]
|loc_08027FB6|
	POP      {r4, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x150]
	MOV      r2, #0xf3
	SUB      r0, #0xc
	LDR      r1, [r0]
	SUB      sp, #0x110
	LDRH     r1, [r1, #4]
	AND      r1, r2
	BEQ      |loc_08028030|
	LDR      r1, [r4, #0x18]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, #0x14
	STR      r1, [sp]
	MOV      r1, #0x2c
	STR      r1, [sp, #4]
	LDR      r1, [sp]
	ADD      r1, #0x10
	STR      r1, [sp, #8]
	MOV      r1, #0x3c
	STR      r1, [sp, #0xc]
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x2b9e
	CMP      r0, #2
	BLT      |loc_08027FF2|
	SUB      r0, #2
|loc_08027FF2|
	LDR      r1, [r4, #0x18]
	MOV      r6, #0
	ADD      r2, r1, #1
	ADD      r1, r1, r4
	ADD      r1, #0x20
	STR      r2, [r4, #0x18]
	STRB     r0, [r1, #9]
	LDR      r1, [pc, #0x10c]
	LSL      r0, r0, #2
	ADD      r1, #8
	LDR      r0, [r1, r0]
	ADD      r5, sp, #0x10
	LDR      r1, [r0, #4]
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	ADD      r0, #0x34
	MOV      r2, sp
	BL       |inc_0x03d784_0x041118| + 0x219e
	ADD      r0, r4, #0
	BL       |loc_08027E48|
	LDR      r0, [r4, #0x18]
	CMP      r0, #5
	BNE      |loc_08028030|
	LDR      r0, [pc, #0xf8]
	STR      r0, [r4, #0x30]
	STR      r6, [r4, #0x18]
|loc_08028030|
	ADD      sp, #0x110
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x1c]
	SUB      sp, #0x114
	SUB      r0, #1
	STR      r0, [r4, #0x1c]
	BNE      |loc_0802807E|
	ADD      r5, r4, #0
	LDR      r0, [r4, #0x18]
	ADD      r5, #0x34
	MOV      r6, #0
	CMP      r0, #0xa
	BLT      |sub_08028082|
	MOV      r1, #0x8c
	LDR      r2, [pc, #0xc4]
	LDR      r1, [r1, r4]
	LDR      r0, [r4, #0x58]
	LDR      r2, [r2, #4]
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0x50
	STR      r0, [r4, #0x38]
	MOV      r0, #0x1c
	STR      r0, [r4, #0x3c]
	MOV      r0, #0x95
	LDR      r1, [pc, #0xb4]
	LSL      r0, r0, #2
	LDR      r1, [r1, r0]
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r0, r4, #0
	BL       |loc_08027E48|
	LDR      r0, [pc, #0xac]
	STR      r0, [r4, #0x30]
	STR      r6, [r4, #0x18]
|loc_0802807E|
	ADD      sp, #0x114
	POP      {r4, r5, r6, r7, pc}
