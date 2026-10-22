	CODE16
|sub_08037C1A|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_08037C36|
	MOV      r0, #0x48
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08037C36|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08037C36|
	MOV      r1, #1
	LSL      r1, r1, #0xa
	ADD      r2, r6, #0
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x4712
	LDR      r0, [pc, #0xfc]
	STR      r0, [r4]
	LDR      r1, [r5]
	LDR      r2, [r5, #4]
	MOV      r0, #0
	STR      r0, [r4, #0x40]
	LSL      r1, r1, #8
	STR      r1, [r4, #0x20]
	LSL      r2, r2, #8
	STR      r2, [r4, #0x24]
	LDRB     r1, [r6, #0x10]
	MOV      r0, #0x3c
	CMP      r1, #3
	BEQ      |loc_08037C60|
	MOV      r0, #0
|loc_08037C60|
	LDR      r1, [pc, #0xe0]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x44]
	STR      r0, [r4, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0xd0]
	ADD      r4, r0, #0
	LDR      r0, [r6, #0xc]
	LDR      r2, [r6, #8]
	SUB      sp, #0x4c
	STR      r2, [sp, #0x44]
	STR      r0, [sp, #0x48]
	LDR      r0, [r6, #0x14]
	LDR      r2, [r6, #0x10]
	STR      r0, [sp, #0x40]
	STR      r2, [sp, #0x3c]
	LDRB     r0, [r1, #0x10]
	CMP      r0, #3
	LDRB     r0, [r1, #0x11]
	BNE      |loc_08037C9C|
	ADD      r1, sp, #0x3c
	ADD      r0, r0, r1
	SUB      r0, #0x10
	LDRB     r5, [r0, #0xe]
	B        |loc_08037CA4|
|loc_08037C9C|
	ADD      r1, sp, #0x44
	ADD      r0, r0, r1
	SUB      r0, #0x10
	LDRB     r5, [r0, #0xe]
|loc_08037CA4|
	LSL      r0, r5, #1
	ADD      r0, r0, r5
	LDR      r1, [pc, #0x98]
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	STR      r0, [r4, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r0, [r6, #0x1c]
	LDR      r1, [r6, #0x18]
	STR      r0, [sp, #0x38]
	STR      r1, [sp, #0x34]
	LDR      r0, [r4, #0x1c]
	ADD      r3, sp, #0
	STR      r0, [sp, #0x20]
	ADD      r0, sp, #0x34
	ADD      r0, r0, r5
	SUB      r0, #0x10
	LDRB     r0, [r0, #6]
	MOV      r7, sp
	ADD      r5, r7, #4
	STRB     r0, [r3, #0x14]
	LDR      r0, [pc, #0x78]
	STR      r0, [sp, #0x1c]
	MOV      r0, #5
	LSL      r0, r0, #0xb
	STR      r0, [sp, #0x18]
	ADD      r0, r4, #0
	ADD      r0, #0x28
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r5!, {r0, r1, r2, r3}
	LDRB     r0, [r4, #0x11]
	ADD      r3, sp, #0
	ADD      r2, r7, #0
	STRB     r0, [r3]
	STR      r4, [sp, #0x30]
	LDR      r0, [r6, #4]
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x11b18
	CMP      r0, #0
	BEQ      |loc_08037D1A|
	MOV      r0, #2
	LDR      r4, [r6]
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r0, #0x30
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0x44]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LDR      r0, [pc, #0x44]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r4, r0
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08037D1A|
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x40]
	CMP      r1, #0x50
	BGE      |loc_08037D3C|
	ADD      r2, r1, #1
	ASR      r1, r1, #4
	LSL      r3, r1, #1
	STR      r2, [r0, #0x40]
	LDR      r2, [r0, #0x44]
	ADD      r1, r3, r1
	LSL      r1, r1, #2
	ADD      r1, r1, r2
	STR      r1, [r0, #0x18]
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
|loc_08037D3C|
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r2, r3, r5, r7}
	LSR      r4, r0, #0x20
	LDMIA    r3!, {r3, r4, r6, r7}
	LSR      r6, r6, #1
|unk_08037D48|
	INCBIN	baserom.gba_0x37d48_0x37d4a.extracted
	LSR      r6, r6, #1
	STRH     r0, [r0, #8]
	LSR      r3, r5, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x18
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x18
	BCS      |sub_08037D82|
	LSL      r0, r0, #0x1d
	LSR      r0, r0, #0x1f
	STRB     r0, [r4, #0x11]
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
