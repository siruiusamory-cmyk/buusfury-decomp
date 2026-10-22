	CODE16
|loc_0800C298|
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r4, r0, #0
	MOV      r2, #0x10
	MOV      r1, #0x20
	MOV      r0, sp
	MOV      r5, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r0, [r4, #0x14]
	ADD      r3, sp, #0
	LDRB     r0, [r0, #5]
	LDR      r1, [pc, #0x178]
	STRB     r0, [r3, #3]
	MOV      r0, #1
	STRB     r0, [r3, #2]
	STR      r1, [sp, #0x20]
	LDR      r1, [pc, #0x174]
	LDR      r1, [r1, #8]
	STR      r1, [sp, #0xc]
	MOV      r1, #0x10
	STR      r1, [sp, #4]
	MOV      r1, #0xc
	STR      r1, [sp, #8]
	STRB     r0, [r3]
	LDR      r0, [sp, #0x24]
	LDR      r2, [sp, #0x30]
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x14]
	LDRB     r1, [r0, #5]
	CMP      r1, #2
	BEQ      |loc_0800C2E6|
	LDRB     r2, [r0, #6]
	ADD      r0, r5, #0
	ADR      r1, |loc_0800C434|
	BL       |inc_0x03d784_0x041118| + 0x512
|loc_0800C2E6|
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x150]
	LSL      r0, r0, #5
	ADD      r1, r0, r1
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x2234
	MOV      r1, #0
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
