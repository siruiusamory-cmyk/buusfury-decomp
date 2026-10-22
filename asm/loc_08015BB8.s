	CODE16
|loc_08015BB8|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #0x14
	ADD      r5, r0, #0
	LDR      r0, [sp, #0x38]
	LDR      r2, [pc, #0x2bc]
	LSL      r0, r0, #2
	ADD      r6, r0, r2
	LDR      r0, [r1]
	LDR      r2, [r1, #8]
	SUB      r2, r2, r0
	STR      r2, [sp, #8]
	LDR      r2, [r1, #0xc]
	LDR      r1, [r1, #4]
	SUB      r2, r2, r1
	STR      r2, [sp, #4]
	LDR      r2, [r5, #0x28]
	MUL      r1, r2
	LDR      r2, [r5, #0x24]
	ADD      r1, r1, r2
	ADD      r4, r1, r0
	LDRB     r0, [r6]
	STRB     r0, [r4, #1]
	LDRB     r1, [r6, #1]
	LDR      r2, [sp, #8]
	SUB      r2, #3
	ADD      r0, r4, #2
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r5, #0x28]
	MOV      r7, #0
	ADD      r4, r0, r4
	LDRB     r0, [r6]
	LDR      r1, [sp, #4]
	SUB      r1, #2
	STR      r1, [sp, #0x10]
	CMP      r1, #0
	BLE      |loc_08015C2C|
	LDR      r2, [sp, #8]
	SUB      r2, #2
	STR      r2, [sp, #0xc]
|loc_08015C08|
	STRB     r0, [r4]
	LDRB     r1, [r6, #2]
	LDR      r2, [sp, #0xc]
	ADD      r0, r4, #1
	BL       |inc_0x046118_0x049114| + 0xd28
	LDRB     r0, [r6, #3]
	LDR      r1, [sp, #8]
	ADD      r7, #1
	ADD      r1, r4, r1
	SUB      r1, #0x10
	STRB     r0, [r1, #0xf]
	LDR      r0, [r5, #0x28]
	ADD      r4, r0, r4
	LDRB     r0, [r6, #1]
	LDR      r1, [sp, #0x10]
	CMP      r7, r1
	BLT      |loc_08015C08|
|loc_08015C2C|
	LDRB     r1, [r6, #3]
	LDR      r2, [sp, #8]
	SUB      r2, #2
	ADD      r0, r4, #1
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [pc, #0x244]
	SUB      r0, #8
	LDR      r0, [r0, #4]
	STR      r0, [r5, #0xc]
	LDR      r0, [pc, #0x240]
	STR      r0, [r5, #0x20]
	MOV      r0, #2
	STRB     r0, [r5, #3]
	MOV      r0, #0
	STRB     r0, [r5]
	LDR      r1, [sp, #0x1c]
	ADD      r0, r5, #0
	LDR      r2, [r1]
	LDR      r1, [r1, #4]
	STR      r1, [r5, #8]
	STR      r2, [r5, #4]
	LDR      r1, [sp, #0x20]
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
