	CODE16
|sub_080203DE|
	ADD      r0, #0xff
	ADD      r0, #1
	CMP      r2, #0
	BEQ      |loc_080203EE|
	CMP      r2, #1
	BEQ      |loc_080203EE|
	CMP      r2, #2
	BNE      |loc_08020400|
|loc_080203EE|
	LDR      r1, [r0, #0x2c]
	ADD      r1, #1
	STR      r1, [r0, #0x2c]
	CMP      r1, #0x14
	BLE      |loc_080203FE|
	LDR      r1, [pc, #0x134]
	MOV      r0, #1
	STR      r0, [r1]
|loc_080203FE|
	BX       lr
|loc_08020400|
	MOV      r1, #0
	STR      r1, [r0, #0x2c]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	MOV      r0, #0xff
	LDR      r1, [pc, #0x130]
	ADD      r0, #0x61
	LDR      r3, [r1, r0]
	ADD      r0, #4
	LDR      r5, [r1, r0]
	LDR      r6, [pc, #0x12c]
	SUB      sp, #0x10
	LDR      r2, [r6, #0xc]
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r3, [sp]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x3c
	STR      r0, [sp, #4]
	MOV      r3, #0x14
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r6, #0xc]
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x3c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x22
	MOV      r0, #0
	STR      r5, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0xe0]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #7
	LSL      r2, r2, #0xa
	MOV      r1, #0
	LDR      r0, [pc, #0xd8]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #7
	STR      r0, [sp]
	MOV      r0, #8
	STR      r0, [sp, #4]
	MOV      r0, #0x17
	STR      r0, [sp, #8]
	MOV      r0, #0xf
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	LDR      r2, [pc, #0xc4]
	LDR      r1, [pc, #0xbc]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0xc0]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #8]
	LDRH     r1, [r0]
	LSR      r2, r0, #0x12
	ORR      r1, r2
	STRH     r1, [r0]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	MOV      r3, #1
	LSL      r3, r3, #0x1a
	LDRH     r1, [r3]
	LSR      r2, r3, #0x12
	BIC      r1, r2
	STRH     r1, [r3]
	CMP      r0, #0
	BEQ      |loc_080204CE|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080204CE|
	POP      {r3, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0x38
	MOV      r1, #0x80
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x4f3e
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x58]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #1
	LDR      r0, [r4, #0x14]
	CMP      r0, #0
	BNE      |loc_0802051E|
	LDR      r0, [pc, #0x44]
	LDR      r1, [r0]
	LDR      r0, [pc, #0x2c]
	LDR      r0, [r0, #0x10]
	BL       |inc_0x0158_0x143f2| + 0x47c2
|loc_0802051E|
	LDR      r0, [r4, #0x14]
	ADD      r0, #1
	STR      r0, [r4, #0x14]
	CMP      r0, #0x3c
	BLE      |sub_0802052C|
	MOV      r0, #1
	POP      {r4, pc}
