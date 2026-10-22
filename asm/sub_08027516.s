	CODE16
|sub_08027516|
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x20]
	SUB      sp, #0x18
	ASR      r1, r1, #8
	STR      r1, [sp, #0x10]
	LDR      r1, [r0, #0x24]
	LDR      r4, [pc, #0x178]
	ASR      r1, r1, #8
	STR      r1, [sp, #0x14]
	ADD      r1, r0, #0
	SUB      r4, #8
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0802755E|
	MOV      r2, #0x38
	LSL      r0, r1, #3
	STR      r0, [sp]
	STR      r2, [sp, #8]
	STR      r1, [sp, #4]
	MOV      r3, #4
	MOV      r0, #0
	ADD      r1, sp, #0x10
	LDR      r2, [pc, #0x14c]
	BL       |loc_0802A81C|
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0802755E|
	ADD      sp, #0x18
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x48]
	ADD      r7, r1, #0
	ADD      r0, #1
	SUB      sp, #0x34
	STR      r0, [r4, #0x48]
	LSL      r1, r0, #0x1e
	BNE      |loc_0802758C|
|loc_08027574|
	LSL      r0, r0, #0x1c
	LSR      r0, r0, #0x1e
	BEQ      |sub_080275D6|
	CMP      r0, #1
	BEQ      |loc_080275DE|
	CMP      r0, #2
	BEQ      |loc_080275E6|
	CMP      r0, #3
	BNE      |loc_0802758C|
	LDR      r0, [r4, #0x18]
	SUB      r0, #0x30
	STR      r0, [r4, #0x18]
|loc_0802758C|
	LDR      r1, [r4, #0x20]
	LDR      r2, [r4, #0x40]
	ADD      r1, r1, r2
	STR      r1, [r4, #0x20]
	LDR      r0, [r4, #0x44]
	LDR      r1, [r4, #0x24]
	ADD      r0, r1, r0
	STR      r0, [r4, #0x24]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r6, [pc, #0xf8]
	SUB      r6, #8
	LDR      r0, [r6, #4]
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r2, [r4, #0x30]
	CMP      r1, r2
	BGE      |loc_080275CA|
	LDR      r1, [r4, #0x28]
	LDR      r2, [r0, #8]
	CMP      r1, r2
	BGE      |loc_080275CA|
	LDR      r1, [r0, #4]
	LDR      r2, [r4, #0x34]
	CMP      r1, r2
	BGE      |loc_080275CA|
	LDR      r1, [r4, #0x2c]
	LDR      r0, [r0, #0xc]
	CMP      r1, r0
	BLT      |loc_080275EE|
|loc_080275CA|
	ADD      r1, r4, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
