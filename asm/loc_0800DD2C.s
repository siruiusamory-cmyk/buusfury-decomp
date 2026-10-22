	CODE16
|loc_0800DD2C|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_0800DD44|
	MOV      r0, #0x44
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800DD44|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800DD44|
	LDR      r0, [r5, #4]
	MOV      r3, #0x34
	LDR      r1, [pc, #0xd0]
	MUL      r0, r3
	ADD      r1, r0, r1
	ADD      r2, r5, #0
	ADD      r2, #8
	ADD      r1, #0xc
	ADD      r0, r4, #0
	BL       |loc_0800D960|
	LDR      r0, [pc, #0xc4]
	ADD      r1, r4, #0
	STR      r0, [r4]
	STR      r5, [r4, #0x30]
	MOV      r0, #0x38
	STRB     r0, [r4, #8]
	ADD      r0, r4, #0
	ADD      r0, #0x34
	ADD      r5, r0, #0
	BL       |sub_0800DB64|
	LDR      r0, [pc, #0xb0]
	MOV      r2, #0
	LDR      r0, [r0, #4]
	ADD      r6, r0, #0
	ADD      r6, #0x80
	LDR      r1, [r6, #0x28]
	ADD      r0, r5, #0
	BL       |loc_08009930|
	MOV      r2, #0
	ADD      r0, r5, #0
	LDR      r1, [r6, #0x30]
	BL       |loc_08009930|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	CMP      r1, #3
	SUB      sp, #0xc
	BNE      |loc_0800DE12|
	LDR      r0, [r4, #0x34]
	LDR      r1, [r2, #8]
	ADD      r6, r2, #0
	CMP      r0, r1
	BGE      |sub_0800DE0E|
	LDR      r0, [r6]
	LDR      r1, [r4, #0x3c]
	CMP      r0, r1
	BGE      |sub_0800DE0E|
	LDR      r0, [r4, #0x38]
	LDR      r1, [r6, #0xc]
	CMP      r0, r1
	BGE      |sub_0800DE0E|
	LDR      r0, [r6, #4]
	LDR      r1, [r4, #0x40]
	CMP      r0, r1
	BGE      |sub_0800DE0E|
	LDR      r7, [r4, #0x30]
	MOV      r3, #0x34
	LDR      r0, [r7, #4]
	LDR      r1, [pc, #0x58]
	MUL      r0, r3
	ADD      r0, r0, r1
	STR      r0, [sp, #4]
	LDR      r0, [pc, #0x58]
	ADD      r5, r4, r3
	LDR      r0, [r0, #4]
	MOV      r2, #1
	ADD      r0, #0x80
	STR      r0, [sp, #8]
	LDR      r1, [r0, #0x28]
	ADD      r0, r5, #0
	BL       |loc_08009930|
	LDR      r0, [sp, #8]
	MOV      r2, #1
	LDR      r1, [r0, #0x30]
	ADD      r0, r5, #0
	BL       |loc_08009930|
	LDR      r0, [pc, #0x38]
	ADD      r1, r4, #0
	LDR      r0, [r0]
	BL       |loc_08011944|
	LDR      r2, [r6, #0x10]
	LDR      r1, [r7, #4]
	LDR      r0, [sp, #4]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x1d72
	ADD      r0, r7, #0
	ADD      r0, #0x10
	LDR      r1, [r7, #0x10]
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #1
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
