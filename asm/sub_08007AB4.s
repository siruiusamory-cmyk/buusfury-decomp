	CODE16
|sub_08007AB4|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LSL      r0, r1, #0x17
	LSR      r2, r0, #0x1f
	MOV      r0, #1
	EOR      r0, r2
	SUB      sp, #0xc
	STR      r0, [sp]
	MOV      r0, #0x1e
	ASR      r7, r1, #3
	AND      r7, r0
	LDR      r0, [sp, #0xc]
	LDR      r1, [pc, #0xa8]
	LDRB     r0, [r0, #4]
	MOV      r4, #0
	LSL      r0, r0, #0xb
	ADD      r6, r0, r1
	MOV      r0, #0x20
	SUB      r0, r0, r7
	LSL      r1, r2, #0xb
	LDR      r2, [sp, #0xc]
	LSL      r0, r0, #1
	ADD      r1, r1, r2
	STR      r1, [sp, #8]
	LSL      r5, r7, #1
	STR      r0, [sp, #4]
|loc_08007AE6|
	LDR      r1, [sp, #8]
	LSL      r0, r4, #6
	ADD      r1, r1, r0
	ADD      r1, r1, r5
	ADD      r1, #8
	ADD      r0, r0, r6
	ADD      r0, r0, r5
	LDR      r2, [sp, #4]
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r4, #1
	CMP      r4, #0x20
	BLT      |loc_08007AE6|
	CMP      r7, #0
	BEQ      |loc_08007B22|
	LDR      r0, [sp]
	LDR      r2, [sp, #0xc]
	MOV      r4, #0
	LSL      r0, r0, #0xb
	ADD      r7, r0, r2
|loc_08007B0E|
	LSL      r0, r4, #6
	ADD      r1, r7, r0
	ADD      r1, #8
	ADD      r0, r0, r6
	ADD      r2, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r4, #1
	CMP      r4, #0x20
	BLT      |loc_08007B0E|
|loc_08007B22|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {lr}
	LDR      r1, [r1, #0xc]
	SUB      sp, #0xc
	LSL      r1, r1, #3
	ASR      r1, r1, #0xa
	STR      r1, [sp, #4]
	MOV      r1, #0
	STR      r1, [sp, #8]
	LDRB     r1, [r0, #4]
	MOV      r2, #1
	LSL      r2, r2, #0x1a
	LSL      r1, r1, #2
	ADD      r1, r1, r2
	ADD      r1, #0x10
	LDR      r2, [sp, #4]
	MOV      r3, #0
	STRH     r2, [r1]
	STRH     r3, [r1, #2]
	LDR      r1, [sp, #4]
	BL       |sub_08007AB4|
	ADD      sp, #0xc
	POP      {pc}
	PUSH     {r3, lr}
	LDR      r2, [r0]
	LDR      r3, [r2, #4]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
|sub_08007B62|
|unk_08007B62|
; cited by 0x08007A6C (a pc-relative load targets 0x08007B6C)
	INCBIN	baserom.gba_0x7b62_0x7b76.extracted
|sub_08007B76|
	DCW      0x0600
