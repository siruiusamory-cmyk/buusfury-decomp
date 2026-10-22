	CODE16
|sub_0803ACCC|
	LDR      r0, [r3, #0x58]
	CMP      r0, #0x10
	BGE      |loc_0803ACF8|
|loc_0803ACD2|
	MOV      r3, #3
	LSL      r3, r3, #9
	ADD      r3, sp
	LDR      r0, [r3, #0x58]
	MOV      r2, #0x20
	LSL      r0, r0, #6
	ADD      r0, r0, r5
	ADD      r0, #0x30
	MOV      r1, #0
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r3, #3
	LSL      r3, r3, #9
	ADD      r3, sp
	LDR      r0, [r3, #0x58]
	ADD      r0, #1
	STR      r0, [r3, #0x58]
	CMP      r0, #0x10
	BLT      |loc_0803ACD2|
|loc_0803ACF8|
	MOV      r7, #1
	LSL      r7, r7, #0xa
	MOV      r4, #0
	MOV      r0, #0x1f
|loc_0803AD00|
	MOV      r1, #0x10
	LSL      r2, r4, #6
	ADD      r2, r2, r5
|loc_0803AD06|
	SUB      r3, r0, r1
	LSL      r3, r3, #1
	ADD      r3, r2, r3
	LDRH     r3, [r3, #0x30]
	ORR      r3, r7
	ADD      r6, r3, #0
	LSL      r3, r1, #1
	ADD      r3, r2, r3
	ADD      r1, #1
	CMP      r1, #0x20
	STRH     r6, [r3, #0x30]
	BLT      |loc_0803AD06|
	ADD      r4, #1
	CMP      r4, #0x10
	BLT      |loc_0803AD00|
	MOV      r2, #0x10
|loc_0803AD26|
	MOV      r1, #0x1f
	SUB      r1, r1, r2
	LSL      r1, r1, #6
	ADD      r4, r1, r5
	LSL      r1, r2, #6
	MOV      r0, #0
	ADD      r6, r1, r5
|loc_0803AD34|
	LSL      r1, r0, #1
	ADD      r3, r4, r1
	LDRH     r3, [r3, #0x30]
	MOV      r7, #1
	LSL      r7, r7, #0xb
	ORR      r7, r3
	ADD      r1, r6, r1
	ADD      r0, #1
	CMP      r0, #0x20
	STRH     r7, [r1, #0x30]
	BLT      |loc_0803AD34|
	ADD      r2, #1
	CMP      r2, #0x20
	BLT      |loc_0803AD26|
	MOV      r3, #3
	LSL      r3, r3, #9
	ADD      r3, sp
	LDR      r0, [r3, #0x68]
	LDR      r2, [r5, #0x10]
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r0, [r0, #4]
	SUB      r1, r1, r2
	LDR      r2, [r5, #0x14]
	SUB      r0, r0, r2
	STR      r0, [r3, #0x50]
	STR      r1, [r3, #0x4c]
	ADD      r0, r1, #0
	LDR      r1, [r3, #0x50]
	ADD      r3, #0x54
	STMIA    r3!, {r0, r1}
	SUB      r3, #0x5c
	ASR      r1, r0, #3
	LDR      r0, [r3, #0x58]
	ASR      r0, r0, #3
	STR      r0, [r3, #0x50]
	STR      r1, [r3, #0x4c]
	LDR      r2, [r5, #0x28]
	CMP      r2, r1
	BNE      |loc_0803AD8A|
	LDR      r2, [r5, #0x2c]
	CMP      r2, r0
	BEQ      |loc_0803AD9C|
|loc_0803AD8A|
	MOV      r3, #3
	LSL      r3, r3, #9
	STR      r0, [r5, #0x2c]
	STR      r1, [r5, #0x28]
	ADD      r3, sp
	LDR      r1, [r3, #0x68]
	ADD      r0, r5, #0
	BL       |loc_0803A8AC|
|loc_0803AD9C|
	LDRB     r0, [r5, #4]
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	MOV      r3, #3
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	LSL      r3, r3, #9
	ADD      r3, sp
	ADD      r0, #0x10
	ADD      r3, #0x54
	LDMIA    r3!, {r1, r2}
	STRH     r1, [r0]
	STRH     r2, [r0, #2]
	ADD      sp, #0x1fc
	ADD      sp, #0x1fc
	ADD      sp, #0x1fc
	ADD      sp, #0x78
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4}
	LDR      r3, [r1]
	LDR      r1, [r1, #4]
	SUB      sp, #0x10
	STR      r1, [r0, #0x14]
	STR      r3, [r0, #0x10]
	MOV      r3, #0
	ADD      r1, sp, #8
	MOV      r2, #0
	STMIA    r1!, {r2, r3}
	LDRB     r1, [r0, #0xb]
	STR      r1, [sp, #8]
	LDRB     r1, [r0, #0xb]
	STR      r1, [sp, #0xc]
	LDR      r2, [r0, #0x10]
	LDR      r3, [sp, #8]
	ADD      r1, r0, #0
	SUB      r2, r2, r3
	LDR      r3, [r0, #0x14]
	LDR      r4, [sp, #0xc]
	STR      r2, [sp]
	SUB      r3, r3, r4
	STR      r3, [sp, #4]
	STR      r2, [r0, #0x18]
	STR      r3, [r0, #0x1c]
	LDR      r2, [r0, #0x10]
	LDR      r3, [sp, #8]
	LDR      r0, [r0, #0x14]
	ADD      r2, r2, r3
	LDR      r3, [sp, #0xc]
	ADD      r1, #0x20
	ADD      r0, r0, r3
	STR      r0, [sp, #4]
	ADD      r0, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STMIA    r1!, {r0, r2}
	ADD      sp, #0x10
	POP      {r4}
	BX       lr
	PUSH     {r4, r5, r6, lr}
	LSL      r2, r1, #1
	MOV      r3, #3
	SUB      r4, r3, r2
	MOV      r3, #0
	ADD      r2, r1, #0
	CMP      r1, #0
	BLE      |loc_0803AE46|
|loc_0803AE20|
	LSL      r6, r2, #2
	ADD      r6, r6, r0
	LSL      r5, r3, #2
	SUB      r6, #0x40
	STR      r2, [r0, r5]
	STR      r3, [r6, #0x3c]
	CMP      r4, #0
	BGE      |loc_0803AE36|
	ADD      r4, r5, r4
	ADD      r4, #6
	B        |loc_0803AE40|
|loc_0803AE36|
	SUB      r5, r3, r2
	LSL      r5, r5, #2
	ADD      r4, r5, r4
	ADD      r4, #0xa
	SUB      r2, #1
|loc_0803AE40|
	ADD      r3, #1
	CMP      r3, r2
	BLT      |loc_0803AE20|
|loc_0803AE46|
	MOV      r2, #0x80
	SUB      r2, r2, r1
	BEQ      |loc_0803AE58|
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LSL      r2, r2, #2
	MOV      r1, #0
	BL       |inc_0x049120_0x055620| + 0xc
|loc_0803AE58|
	POP      {r4, r5, r6, pc}
	LSL      r0, r0, #0
	LDR      r0, [pc, #0]
	BX       lr
|sub_0803AE60|
|unk_0803AE60|
	INCBIN	baserom.gba_0x3ae60_0x3ae62.extracted
