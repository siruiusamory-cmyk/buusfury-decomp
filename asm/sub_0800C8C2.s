	CODE16
|sub_0800C8C2|
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x2c]
	LDR      r2, [r0]
	LDR      r3, [r2, #0x10]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x2c]
	LDR      r2, [r0]
	LDR      r3, [r2, #0x18]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x20]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r0, #0x14
	ADD      r1, r0, #0
	LDR      r2, [r0]
	LDR      r3, [r0, #8]
	LDR      r0, [r0, #4]
	ADD      r1, #8
	LDR      r1, [r1, #4]
	SUB      sp, #0x14
	ADD      r0, r0, r1
	ADD      r2, r2, r3
	ASR      r1, r2, #1
	STR      r0, [sp, #8]
	ASR      r0, r0, #1
	STR      r2, [sp, #4]
	LDR      r7, [pc, #0x1d4]
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	ADD      r5, sp, #0xc
	ADD      r2, r7, #0
	ADD      r1, r5, #0
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x10]
	MOV      r0, #0
	BL       |loc_0800C454|
	LDR      r6, [pc, #0x1bc]
	ADD      r1, r0, #0
	SUB      r6, #8
	LDR      r0, [r6]
	BL       |List_Append|
	ADD      r2, r7, #0
	ADD      r2, #8
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |loc_0800C454|
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |List_Append|
	ADD      r2, r7, #0
	ADD      r2, #0x10
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |loc_0800C454|
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |List_Append|
	ADD      r2, r7, #0
	ADD      r2, #0x18
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |loc_0800C454|
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |List_Append|
	LDRB     r0, [r4, #0xc]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r4, #0xc]
	BNE      |sub_0800CA04|
	LDR      r1, [r4, #0x2c]
	STR      r0, [r1, #0x1c]
	LDR      r0, [r6]
	BL       |loc_080116FC|
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0800C9D6|
	LSL      r7, r1, #2
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r0, r0, r7
	MOV      r2, #0x38
	LSR      r1, r7, #2
	STR      r1, [sp, #4]
	ADD      r1, r5, #0
	STR      r2, [sp, #8]
	STR      r0, [sp]
	MOV      r3, #4
	MOV      r0, #0
	LDR      r2, [pc, #0x140]
	BL       |inc_0x1c3f2_0x2ab4c| + 0xe42a
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |List_Append|
|loc_0800C9D6|
	MOV      r0, #0xc
	LDR      r5, [r6]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800C9EC|
	MOV      r1, #0x10
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x128]
	STR      r1, [r0]
	STR      r4, [r0, #8]
|loc_0800C9EC|
	ADD      r2, r0, #0
	MOV      r0, #0x61
	LSL      r0, r0, #4
	ADD      r0, r5, r0
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
