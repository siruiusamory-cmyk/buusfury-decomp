	CODE16
|sub_080071F8|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	ADD      r0, r1, #0
	ADD      r5, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	SUB      sp, #0x1c
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #2]
	LDRB     r1, [r6, #0x11]
	AND      r0, r1
	BEQ      |loc_080072C8|
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r4, [r6, #0x14]
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #0x10]
	ADD      r0, r1, #0
	STR      r1, [sp, #0xc]
	LDR      r1, [sp, #0x10]
	STR      r0, [sp, #0x14]
	MOV      r3, #0x14
	STR      r1, [sp, #0x18]
	LDRSH    r0, [r4, r3]
	MOV      r3, #8
	LDRSH    r1, [r4, r3]
	MOV      r3, #0x16
	SUB      r0, r0, r1
	LDR      r1, [sp, #0x14]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x14]
	LDRSH    r0, [r4, r3]
	MOV      r3, #0xa
	LDRSH    r1, [r4, r3]
	ADD      r3, sp, #0
	SUB      r0, r0, r1
	LDR      r1, [sp, #0x18]
	ADD      r0, r0, r1
	LDR      r1, [sp, #0x14]
	STR      r0, [sp, #0x18]
	STRH     r1, [r3, #0x10]
	STRH     r0, [r3, #0x12]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #2
	BL       |inc_0x046118_0x049114| + 0x98c
	STR      r0, [sp, #0xc]
	MOV      r0, #0x11
	LSL      r0, r0, #5
	ADD      r0, r5, r0
	LDRH     r7, [r0, #0x10]
	LDRB     r0, [r6, #0x10]
	ADD      r1, r5, #0
	STRB     r0, [r5, #0x10]
	MOV      r0, #0
	BL       |loc_08006D98|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDRB     r1, [r4, #0x13]
	MOV      r2, #1
	STR      r2, [sp, #4]
	LDR      r0, [pc, #0x74]
	STR      r1, [sp]
	LDRB     r2, [r4, #0x12]
	LDRB     r1, [r4, #0x11]
	SUB      r0, #4
	LDR      r0, [r0]
	ADD      r3, sp, #0x10
	BL       |loc_08008D44|
	ADD      r5, r0, #0
	LDRB     r0, [r4, #0x10]
	ADD      r1, r5, #0
	STRB     r0, [r5, #0x10]
	MOV      r0, #0
	BL       |loc_08006DD6|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r0, [sp, #0xc]
	CMP      r0, #0
	BEQ      |loc_080072C8|
	MOV      r0, #0x11
	LSL      r0, r0, #5
	ADD      r0, r5, r0
	STRH     r7, [r0, #0x10]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #2
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080072C8|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080072DE|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
