	CODE16
|sub_0800FFA2|
	PUSH     {r4, r5}
	LDRB     r3, [r1, #0x11]
	LDR      r2, [r1, #0x50]
	SUB      sp, #0x18
	LSL      r3, r3, #4
	ADD      r2, r2, r3
	LDRB     r3, [r1, #0x10]
	LSL      r3, r3, #2
	ADD      r2, r2, r3
	LDR      r3, [r2, #4]
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ADD      r2, #0xa1
	LDMIA    r2!, {r4}
	LDR      r2, [r2]
	ASR      r4, r4, #8
	ASR      r2, r2, #8
	STR      r2, [sp, #4]
	ADD      r2, r4, #0
	STR      r4, [sp]
	LDR      r4, [sp, #4]
	STR      r2, [sp, #8]
	LDR      r2, [pc, #0x3c]
	STR      r4, [sp, #0xc]
	LDR      r2, [r2]
	LDR      r4, [sp, #8]
	ADD      r2, #0x28
	LDR      r5, [r2]
	SUB      r4, r4, r5
	LDR      r5, [sp, #0xc]
	LDR      r2, [r2, #4]
	STR      r4, [sp]
	SUB      r2, r5, r2
	STR      r2, [sp, #4]
	ADD      r2, r4, #0
	LDR      r4, [sp, #4]
	STR      r2, [sp, #0x10]
	STR      r4, [sp, #0x14]
	LDR      r1, [r1, #0x58]
	LDRB     r1, [r1, #8]
	ADD      r1, r2, r1
	ADD      r2, r4, #0
	ADD      r4, r3, #0
	MOV      r3, #5
	LDRSB    r4, [r4, r3]
	SUB      r1, #8
	ADD      r2, r2, r4
	STMIA    r0!, {r1, r2}
	ADD      sp, #0x18
	POP      {r4, r5}
	BX       lr
|unk_08010008|
	INCBIN	baserom.gba_0x10008_0x1000a.extracted
	LSR      r4, r0, #0x20
	MOV      r7, #0x14
	LSR      r7, r0, #0x20
	LDR      r2, [pc, #0x2bc]
	SUB      sp, #8
	LDR      r1, [r2, #8]
	LDR      r3, [r2, #4]
	STR      r1, [sp, #4]
	STR      r3, [sp]
	LDR      r2, [r2]
	MOV      r1, #0xff
	ADD      r1, #0xad
	LDR      r1, [r1, r0]
	LDR      r2, [r2, #0xc]
	ASR      r1, r1, #0xa
	ASR      r2, r2, #0xa
	SUB      r1, r1, r2
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x1d
	MOV      r2, sp
	LDRB     r1, [r2, r1]
	STRB     r1, [r0, #0x10]
	ADD      sp, #8
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x290]
	ADD      r1, r4, #0
	LDR      r0, [r0]
	ADD      r1, #0xff
	ADD      r0, #0x80
	LDR      r2, [r0, #0x10]
	LDR      r3, [pc, #0x284]
	ADD      r1, #0xa1
	ADD      r0, r1, #4
	LDR      r7, [r3]
	ADD      r5, r0, #0
	SUB      r5, #0x24
	MOV      r6, #0
	ADD      r7, #0x18
	CMP      r2, #0
	SUB      sp, #0x24
	BEQ      |loc_08010144|
	LDR      r1, [r1]
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #0x18]
	ADD      r0, r1, #0
	STR      r1, [sp, #0x14]
	LDR      r1, [sp, #0x18]
	STR      r0, [sp, #0x1c]
	STR      r1, [sp, #0x20]
	LDR      r1, [r7]
	CMP      r0, r1
	BLT      |loc_08010092|
	LDR      r0, [sp, #0x1c]
	LDR      r1, [r7, #8]
	CMP      r0, r1
	BGE      |loc_08010092|
	LDR      r0, [sp, #0x20]
	LDR      r1, [r7, #4]
	CMP      r0, r1
	BLT      |loc_08010092|
	LDR      r0, [sp, #0x20]
	LDR      r1, [r7, #0xc]
	CMP      r0, r1
	BLT      |sub_08010098|
|loc_08010092|
	MOV      r0, #0
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
