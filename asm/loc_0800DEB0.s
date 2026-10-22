	CODE16
|loc_0800DEB0|
	LDRH     r2, [r1, #0x12]
	ADD      r2, #1
	LSL      r2, r2, #0x10
	LSR      r2, r2, #0x10
	STRH     r2, [r1, #0x12]
	LDRB     r0, [r0, #4]
	LSR      r2, r0
	LDR      r0, [r1, #0x50]
	LDR      r0, [r0]
	CMP      r0, r2
	BGT      |loc_0800DECC|
	MOV      r0, #0
	STRH     r0, [r1, #0x12]
	MOV      r2, #0
|loc_0800DECC|
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [pc, #0x18c]
	BL       |loc_0800ED18|
	POP      {r3, pc}
	MOV      r0, #0
	STRH     r0, [r1, #0x12]
	STRB     r0, [r1, #0x11]
	MOV      r0, #0x24
	STRB     r0, [r1, #8]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	MOV      r4, #0
	STRH     r4, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r4, [r1, #0x11]
	LDR      r0, [pc, #0x170]
	LDR      r1, [pc, #0x174]
	LDR      r5, [r0]
	MOV      r0, #0x4b
	LSL      r0, r0, #3
	ADD      r6, r0, r1
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0x2348
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r1, r6, r0
	LDR      r0, [pc, #0x160]
	ADD      r3, r4, #0
	MOV      r2, #0x40
	ADD      r0, r5, r0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, lr}
	ADD      r4, r1, #0
	LDRB     r0, [r1, #0x10]
	LDR      r1, [pc, #0x144]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r1, #8
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	ADD      r5, #0xa1
	LDR      r1, [r5, #4]
	LDR      r2, [r5]
	SUB      sp, #0x14
	STR      r1, [sp, #0x10]
	ADD      r1, r2, #0
	STR      r2, [sp, #0xc]
	LDR      r2, [r0]
	SUB      r1, r1, r2
	STR      r1, [sp, #0xc]
	LDR      r1, [sp, #0x10]
	LDR      r0, [r0, #4]
	SUB      r0, r1, r0
	STR      r0, [sp, #0x10]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x10]
	ASR      r0, r0, #8
	ASR      r1, r1, #8
	STR      r0, [sp, #4]
	LDR      r0, [pc, #0x104]
	STR      r1, [sp, #8]
	LDR      r0, [r0, #4]
	ADD      r1, sp, #4
	SUB      r2, r5, #4
	BL       |loc_080097C2|
	CMP      r0, #0
	BEQ      |loc_0800DF7A|
	LDR      r0, [sp, #0xc]
	STR      r0, [r5]
	LDR      r1, [sp, #0x10]
	STR      r1, [r5, #4]
|loc_0800DF7A|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x40]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	LDR      r0, [r1, #0x50]
	LDR      r2, [r0]
	LDRH     r0, [r1, #0x12]
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	LSR      r0, r0, #5
	CMP      r0, r2
	BLT      |sub_0800DFA8|
	MOV      r0, #0x40
	STRH     r0, [r1, #0x12]
	MOV      r0, #2
	STRB     r0, [r1, #0x11]
	BX       lr
