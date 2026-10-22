	CODE16
|sub_08012A24|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r5, [pc, #0x2e4]
	ADD      r6, r4, #0
	LDR      r0, [r5, #0xc]
	ADD      r6, #0xff
	ADD      r6, #0xa1
	LDR      r0, [r0, #0xc]
	ADD      r7, r6, #4
	CMP      r0, #0
	SUB      sp, #0x5c
	BEQ      |sub_08012B20|
	STR      r4, [sp, #0x48]
	LDRB     r0, [r4, #0x10]
	ADD      r3, sp, #0x20
	ADD      r2, sp, #0x20
	STRB     r0, [r3, #0x1c]
	LDR      r0, [pc, #0x2cc]
	STR      r4, [sp, #0x58]
	STR      r0, [sp, #0x44]
	MOV      r0, #1
	LSL      r0, r0, #0xa
	STR      r0, [sp, #0x40]
	MOV      r0, #1
	STRB     r0, [r3, #8]
	LDR      r0, [r6]
	LDR      r1, [r7]
	ASR      r0, r0, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #0x1c]
	STR      r1, [sp, #0x24]
	STR      r0, [sp, #0x18]
	STR      r0, [sp, #0x20]
	LDRB     r0, [r4, #0x10]
	LDR      r1, [pc, #0x2a4]
	ADD      r1, #0x54
	LSL      r0, r0, #4
	ADD      r1, r0, r1
	ADD      r0, sp, #0x2c
	BL       |inc_0x049120_0x055620| + 0x9eb4
	ADD      r2, sp, #0x28
	MOV      r1, #0
	LDR      r0, [r5, #4]
	BL       |loc_08011C0C|
	CMP      r0, #0
	BEQ      |sub_08012AB4|
	LDR      r5, [r5]
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r0, #0x30
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0x284]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LDR      r0, [pc, #0x280]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r5, r0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [sp, #0x4c]
	CMP      r0, #0
	BEQ      |sub_08012AF4|
	MOV      r1, #0x4b
	MOV      r0, #0xf
	BL       |loc_0800797C|
	B        |sub_08012AF4|
