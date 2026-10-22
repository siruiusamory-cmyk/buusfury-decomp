	CODE16
|loc_08006718|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r2, #0
	LDR      r2, [r1, #0x2c]
	SUB      sp, #0x14
	STR      r2, [sp]
	ADD      r7, r3, #0
	LDR      r3, [r1, #0x28]
	ADD      r4, r1, #0
	MOV      r1, #0
	MOV      r2, #0
	ADD      r6, r0, #0
	ADD      r0, r4, #0
	BL       |loc_08004F1C|
	MOV      r0, #8
	STR      r0, [sp, #4]
	MOV      r0, #0x18
	STR      r0, [sp, #8]
	MOV      r0, #0xe8
	STR      r0, [sp, #0xc]
	MOV      r0, #0x98
	STR      r0, [sp, #0x10]
	ADD      r0, r4, #0
	ADD      r1, sp, #4
	BL       |loc_08004F50|
	MOV      r1, #1
	STRB     r1, [r4]
	MOV      r0, #0x78
	STR      r0, [r4, #4]
	MOV      r0, #0x10
	STR      r0, [r4, #8]
	LDR      r0, [pc, #0x118]
	LDR      r0, [r0]
	STR      r0, [r4, #0xc]
	MOV      r0, #5
	STRB     r0, [r4, #3]
	STRB     r1, [r4, #2]
	LDR      r0, [pc, #0x110]
	LDR      r1, [pc, #0x114]
	STR      r0, [r4, #0x20]
	LSL      r0, r5, #2
	LDR      r1, [r1, r0]
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	CMP      r7, #0
	BEQ      |loc_0800679C|
	LDR      r0, [r6, #4]
	MOV      r5, #0
	CMP      r0, #0
	BLE      |loc_0800679C|
	ADD      r7, r6, #4
|loc_08006782|
	LSL      r0, r5, #2
	ADD      r0, r0, r7
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r6, #4]
	ADD      r5, #1
	CMP      r0, r5
	BGT      |loc_08006782|
|loc_0800679C|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #4]
	ADD      r7, r1, #0
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_080067D2|
	ADD      r6, r5, #4
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r7, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |sub_080067CA|
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
