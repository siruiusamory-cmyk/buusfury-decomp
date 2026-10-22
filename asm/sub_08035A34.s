	CODE16
|sub_08035A34|
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x20]
	SUB      sp, #0x18
	ASR      r1, r1, #8
	STR      r1, [sp, #0x10]
	LDR      r1, [r0, #0x24]
	LDR      r4, [pc, #0x144]
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
	BLT      |loc_08035A7C|
	MOV      r2, #0x38
	LSL      r0, r1, #3
	STR      r0, [sp]
	STR      r2, [sp, #8]
	STR      r1, [sp, #4]
	MOV      r3, #4
	MOV      r0, #0
	ADD      r1, sp, #0x10
	LDR      r2, [pc, #0x11c]
	BL       |inc_0x1c3f2_0x2ab4c| + 0xe42a
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08035A7C|
	ADD      sp, #0x18
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r0, #0x40
	ADD      r7, r1, #0
	LDR      r1, [r4, #0x20]
	LDMIA    r0!, {r2}
	SUB      sp, #0x34
	ADD      r1, r1, r2
	STR      r1, [r4, #0x20]
	LDR      r1, [r4, #0x24]
	LDR      r0, [r0]
	ADD      r0, r1, r0
	STR      r0, [r4, #0x24]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r6, [pc, #0xe4]
	SUB      r6, #8
	LDR      r0, [r6, #4]
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r2, [r4, #0x30]
	CMP      r1, r2
	BGE      |loc_08035AC8|
	LDR      r1, [r4, #0x28]
	LDR      r2, [r0, #8]
	CMP      r1, r2
	BGE      |loc_08035AC8|
	LDR      r1, [r0, #4]
	LDR      r2, [r4, #0x34]
	CMP      r1, r2
	BGE      |loc_08035AC8|
	LDR      r1, [r4, #0x2c]
	LDR      r0, [r0, #0xc]
	CMP      r1, r0
	BLT      |sub_08035AD4|
|loc_08035AC8|
	ADD      r1, r4, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
