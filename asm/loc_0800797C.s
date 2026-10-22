	CODE16
|loc_0800797C|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08007990|
	LDR      r1, [pc, #0x90]
	STR      r1, [r0]
|loc_08007990|
	STR      r6, [r0, #8]
	STRB     r5, [r0, #4]
	ADD      r4, r0, #0
	MOV      r0, #0x64
	SUB      r0, r0, r5
	ASR      r1, r0, #0x1f
	LSR      r1, r1, #0x1c
	ADD      r0, r1, r0
	ASR      r1, r0, #4
	ADD      r1, #1
	STRB     r1, [r4, #5]
	MOV      r1, #1
	LDR      r5, [pc, #0x78]
	STRB     r1, [r4, #6]
	LDR      r0, [r5, #4]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4ce4
	ADD      r1, r4, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4ca2
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #8]
	SUB      sp, #8
	SUB      r0, #1
	STR      r0, [r4, #8]
	LDR      r5, [pc, #0x58]
	BNE      |sub_080079E2|
	STR      r0, [sp]
	STR      r0, [sp, #4]
	LDR      r0, [r5]
	MOV      r1, sp
	BL       |sub_080097A6|
	LDR      r0, [r5, #4]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4d00
	ADD      sp, #8
	POP      {r4, r5, r6, pc}
