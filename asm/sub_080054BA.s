	CODE16
|sub_080054BA|
	PUSH     {r0, r4, r5, r6, r7, lr}
	SUB      sp, #0x18
	LDR      r0, [sp, #0x18]
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r0, [sp, #0x14]
	LDR      r1, [r0, #0x1c]
	LDR      r0, [r0, #0x28]
	CMP      r1, r0
	BEQ      |loc_08005574|
	LDR      r1, [sp, #0x14]
	LDR      r4, [pc, #0x21c]
	STR      r0, [r1, #0x1c]
	LDR      r0, [r4, #0x1c]
	BL       |loc_08011B04|
	LDR      r1, [sp, #0x18]
	MOV      r6, #0
	ADD      r1, #0xff
	ADD      r1, #0x2d
	STR      r1, [sp, #0x10]
|loc_080054E4|
	LDR      r0, [sp, #0x14]
	LDR      r1, [sp, #0x10]
	LDR      r0, [r0, #0x1c]
	MOV      r4, #0
	ADD      r0, r0, r6
	LSL      r0, r0, #7
	ADD      r0, r0, r1
	ADD      r0, #0xc
	STR      r0, [sp, #0xc]
	LDR      r0, [r0]
	CMP      r0, #0
	BLE      |loc_08005562|
	MOV      r2, #0x34
	LDR      r1, [sp, #0x18]
	LSL      r0, r6, #5
	ADD      r1, r0, r1
	MUL      r2, r6
	ADD      r2, #0x44
	STR      r2, [sp, #4]
	STR      r1, [sp, #8]
|loc_0800550C|
	LSL      r1, r4, #1
	ADD      r1, r1, r4
	LDR      r0, [sp, #0xc]
	LSL      r1, r1, #2
	ADD      r7, r1, r0
	ADD      r7, #4
	LDR      r1, [r7]
	MOV      r0, #0
	LDR      r2, [pc, #0x1d4]
	BL       |loc_0800EB60|
	LDR      r1, [sp, #8]
	LSL      r2, r4, #2
	ADD      r1, r1, r2
	MOV      r2, #5
	LSL      r2, r2, #7
	ADD      r1, r1, r2
	STR      r0, [r1, #0x38]
	ADD      r5, r0, #0
	LDR      r0, [r7, #4]
	CMP      r0, #0
	BNE      |loc_08005544|
	LDR      r1, [pc, #0x1bc]
	ADD      r0, r5, #0
	BL       |sub_0800EECC|
	MOV      r0, #1
	STRB     r0, [r5, #0x10]
|loc_08005544|
	LSL      r1, r4, #4
	ADD      r1, #0x12
	LDR      r2, [sp, #4]
	STR      r1, [r5, #0x6c]
	LDR      r0, [pc, #0x1a0]
	STR      r2, [r5, #0x70]
	LDR      r0, [r0, #0x1c]
	ADD      r1, r5, #0
	BL       |List_Append|
	LDR      r0, [sp, #0xc]
	ADD      r4, #1
	LDR      r0, [r0]
	CMP      r0, r4
	BGT      |loc_0800550C|
|loc_08005562|
	ADD      r6, #1
	CMP      r6, #2
	BLT      |loc_080054E4|
	LDR      r0, [sp, #0x18]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x2c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_08005574|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
