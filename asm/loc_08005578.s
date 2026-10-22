	CODE16
|loc_08005578|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	ADD      r4, r1, #0
	ADD      r1, r6, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r1, [sp]
	LDR      r1, [r1, #0xc]
	MOV      r0, #2
	ADD      r7, r2, #0
	ADD      r5, r3, #0
	CMP      r1, r2
	BNE      |loc_08005598|
	MOV      r0, #0xff
	ADD      r0, #0x25
	LDRB     r0, [r0, r6]
|loc_08005598|
	STRB     r0, [r4, #3]
	LDR      r0, [pc, #0x154]
	MOV      r1, #0x10
	LDR      r0, [r0, #0xc]
	ADD      r2, r7, #1
	STR      r0, [r4, #0xc]
	MOV      r0, #0
	STRB     r0, [r4]
	ADD      r0, r5, #0
	ADD      r0, #8
	STR      r0, [r4, #8]
	LDR      r0, [pc, #0x14c]
	STR      r1, [r4, #4]
	LDR      r1, [r0, #0x38]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x512
	LDR      r0, [pc, #0x134]
	MOV      r1, #0x64
	LDR      r0, [r0, #8]
	STR      r0, [r4, #0xc]
	ADD      r0, r5, #0
	ADD      r0, #0xe
	STR      r0, [r4, #8]
	ADD      r0, r6, #0
	ADD      r0, #0xff
	STR      r1, [r4, #4]
	LSL      r1, r7, #7
	ADD      r0, #0x2d
	LDR      r2, [r0, r1]
	CMP      r2, #0
	BEQ      |sub_08005620|
	ADD      r6, r1, r0
	LDRH     r0, [r6, #4]
	LDR      r1, [pc, #0x11c]
	LSL      r0, r0, #2
	LDR      r2, [r1, r0]
	MOV      r1, #0x6c
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x540
	ADD      r0, r5, #0
	ADD      r0, #0x1b
	STR      r0, [r4, #8]
	MOV      r7, #0x64
	STR      r7, [r4, #4]
	LDRH     r0, [r6, #6]
	LDR      r1, [pc, #0x104]
	LSL      r0, r0, #2
	LDR      r2, [r1, r0]
	MOV      r1, #0x6c
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x540
	ADD      r1, r5, #0
	ADD      r1, #0x28
	LDR      r0, [r6, #8]
	STR      r1, [r4, #8]
	STR      r7, [r4, #4]
	BL       |inc_0x049120_0x055620| + 0xa01c
	ADD      r2, r1, #0
	ADD      r3, r0, #0
	ADD      r0, r4, #0
	ADR      r1, |loc_08005700|
	BL       |inc_0x03d784_0x041118| + 0x512
	POP      {r3, r4, r5, r6, r7, pc}
