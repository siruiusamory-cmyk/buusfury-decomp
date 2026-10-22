	CODE16
|sub_0803A086|
	LSR      r4, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r3, #0x38
	STRB     r3, [r1, #8]
	STRB     r2, [r1, #0x11]
	STR      r2, [r0, #4]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x34
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	LDR      r1, [r5, #4]
	CMP      r1, #0
	BNE      |loc_0803A116|
	SUB      r0, #0x10
	CMP      r0, #0x28
	BCS      |loc_0803A116|
	MOV      r6, sp
	ADD      r1, r4, #0
	ADD      r0, sp, #4
	BL       |inc_0x0158_0x143f2| + 0xfd20
	STR      r4, [sp, #0x20]
	LDRB     r0, [r4, #0x10]
	ADD      r3, sp, #0
	MOV      r7, #0
	STRB     r0, [r3, #0x14]
	LDR      r0, [pc, #0x2a0]
	STR      r0, [sp, #0x1c]
	MOV      r0, #1
	LSL      r0, r0, #0xa
	STR      r0, [sp, #0x18]
	STRB     r7, [r3]
	LDR      r0, [pc, #0x298]
	STR      r4, [sp, #0x30]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r3, r2, r1
	ADD      r2, r6, #0
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	CMP      r0, #0
	BEQ      |loc_0803A116|
	LDR      r0, [pc, #0x284]
	LDR      r6, [r0]
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r0, #0x30
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0x278]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LDR      r0, [pc, #0x278]
	ADD      r3, r7, #0
	MOV      r2, #0x40
	ADD      r0, r6, r0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	STR      r0, [r5, #4]
|loc_0803A116|
	LDRH     r0, [r4, #0x12]
	LSL      r0, r0, #0x15
	LSR      r0, r0, #0x18
	STRB     r0, [r4, #0x11]
	LDR      r1, [r4, #0x50]
	LDR      r1, [r1]
	CMP      r1, r0
	BNE      |loc_0803A134|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0803A134|
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r3, #0x38
	STRB     r3, [r1, #8]
	STRB     r2, [r1, #0x11]
	STR      r2, [r0, #4]
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	CMP      r0, #0
	BEQ      |loc_0803A166|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [pc, #0x218]
	LDR      r1, [r4, #4]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_0803A166|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
	POP      {r4, pc}
