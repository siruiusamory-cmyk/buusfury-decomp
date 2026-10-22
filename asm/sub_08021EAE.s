	CODE16
|sub_08021EAE|
	LSL      r0, r0, #0
	STR      r2, [sp, #0x350]
	LSR      r4, r0, #0x20
	ADD      r6, pc, #0x2D0
	LSR      r2, r6, #1
	CMP      r3, #0xfc
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x204]
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x10]
	MOV      r1, #0xff
	ADD      r1, #0x89
	LDR      r1, [r1, r0]
	LDR      r2, [r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r1, #0xff
	LDR      r0, [r4, #0x14]
	ADD      r1, #0x89
	LDR      r1, [r1, r0]
	LDR      r2, [r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6ee8
	POP      {r3, r4, r5, pc}
	MOV      r1, #0xff
	ADD      r1, #0x8d
	PUSH     {r3, lr}
	LDRH     r1, [r1, r0]
	BL       |inc_0x03d784_0x041118| + 0x2ab8
	POP      {r3, pc}
	MOV      r0, #0
	CMP      r1, #0
	BEQ      |loc_08021F08|
|loc_08021EFE|
	LSL      r2, r1, #0x1f
	BPL      |loc_08021F04|
	ADD      r0, #1
|loc_08021F04|
	LSR      r1, r1, #1
	BNE      |loc_08021EFE|
|loc_08021F08|
	BX       lr
|loc_08021F0A|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [pc, #0x1b8]
	LDR      r2, [r1]
	STR      r2, [sp]
	LDR      r6, [r1]
	MOV      r5, #0
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #0x81
	LDR      r7, [pc, #0x1a4]
	LDR      r0, [r7, #8]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x20]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_08021F40|
	LDR      r0, [r7, #8]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	B        |loc_08021F58|
|loc_08021F40|
	LDR      r1, [pc, #0x184]
	LDR      r0, [r1]
	CMP      r6, r0
	BEQ      |loc_08021F58|
	LDR      r6, [r1]
	LDR      r0, [r7, #8]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_08021F58|
	LDR      r1, [r4, #0x1c]
	LDR      r3, [pc, #0x16c]
	LDR      r0, [sp]
	LDR      r2, [r3]
	CMP      r0, r2
	BEQ      |loc_08021F82|
	LDR      r0, [r3]
	ADD      r5, #1
	CMP      r5, #0x3c
	STR      r0, [sp]
	BNE      |loc_08021F82|
	LDR      r0, [pc, #0x15c]
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |sub_08021F7E|
	MOV      r0, #0
	STRH     r0, [r4, #0xc]
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
