	CODE16
|Blend_WriteControl3|
	MOV      r2, #1
	LSL      r2, r2, #9
	PUSH     {r4, lr}
	SUB      sp, #0x10
	MOV      r1, #0
	LDR      r0, [pc, #0x9c]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #3
	LSL      r2, r2, #0xf
	MOV      r1, #0
	LSL      r0, r2, #0xa
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	MOV      r4, #0
	STRH     r4, [r1, #0x10]
	STRH     r4, [r1, #0x12]
	STRH     r4, [r1, #0x14]
	STRH     r4, [r1, #0x16]
	STRH     r4, [r1, #0x18]
	STRH     r4, [r1, #0x1a]
	STRH     r4, [r1, #0x1c]
	LDR      r0, [pc, #0x6c]
	STRH     r4, [r1, #0x1e]
	STRH     r4, [r0, #0x10]
	LDR      r0, [pc, #0x6c]
	LDR      r2, [pc, #0x6c]
	STRH     r0, [r1, #0xc]
	LSR      r0, r1, #0x10
	STRH     r0, [r1]
	MOV      r0, #3
	MOV      r1, #0
	LSL      r0, r0, #0x19
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0x1e
	STR      r0, [sp, #8]
	MOV      r0, #0x14
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	MOV      r2, #1
	STR      r4, [sp]
	STR      r4, [sp, #4]
	LDR      r1, [pc, #0x50]
	BL       |inc_0x03d784_0x041118| + 0x28c
	ADD      sp, #0x10
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |Blend_WriteControl3|
	ADD      r0, r4, #0
	BL       |sub_08014dc2|
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0x34]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x28]
	LDR      r0, [pc, #0x14]
	BL       |inc_0x049120_0x055620| + 0x24
	POP      {r4, pc}
	LSL      r0, r0, #0
	STRH     r0, [r1, #2]
	LSR      r3, r5, #1
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r0, r0, #8
	LSL      r0, r0, #0x14
	LSL      r0, r0, #1
	LSL      r0, r0, #0x10
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0
	DCW      0xf000,0x0600
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	LDR      r0, [r1, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	LDRB     r1, [r3, #8]
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r3, lr}
	ADD      r2, r1, #0
	LDRB     r1, [r0, #8]
	CMP      r1, #0
	BNE      |sub_08015966|
	MOV      r0, #1
	POP      {r3, pc}
