	CODE16
|sub_08006AAA|
	LSR      r4, r0, #0x20
	LSL      r4, r3, #5
	LSR      r7, r0, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r4, [sp, #0x1f0]
	LSR      r1, r6, #0x20
	PUSH     {r3, lr}
	STRB     r1, [r0, #1]
	LDR      r0, [pc, #0xd4]
	LDR      r2, [pc, #0xd8]
	LDR      r0, [r0, #4]
	ADD      r0, r0, r2
	BL       |inc_0x03d784_0x041118| + 0xca6
	POP      {r3, pc}
	PUSH     {r3, lr}
	STRB     r1, [r0, #2]
	LDR      r0, [pc, #0xc4]
	LDR      r0, [r0, #4]
	ADD      r0, #0xc
	BL       |inc_0x03d784_0x041118| + 0x1a08
	POP      {r3, pc}
	PUSH     {r3, lr}
	MOV      r1, #4
	BL       |inc_0x03d784_0x041118| + 0x24ca
	LDR      r1, [pc, #0xb8]
	ADD      r0, r0, r1
	POP      {r3, pc}
	PUSH     {r4, r5, lr}
	LDR      r5, [pc, #0xa8]
	ADD      r4, r0, #0
	SUB      sp, #0x14
	MOV      r3, #8
	MOV      r2, #0
	ADD      r1, sp, #4
	LDR      r0, [r5]
	BL       |inc_0x03d784_0x041118| + 0x24b6
	MOV      r1, #4
	MOV      r0, sp
	ADD      r0, r0, r1
	BL       |inc_0x03d784_0x041118| + 0x24ca
	LDR      r1, [pc, #0x94]
	ADD      r0, r0, r1
	LDR      r1, [sp, #8]
	CMP      r0, r1
	BNE      |loc_08006B36|
	ADD      r3, sp, #0
	LDRB     r0, [r3, #4]
	CMP      r0, #8
	BGT      |loc_08006B36|
	LDRB     r0, [r3, #6]
	CMP      r0, #8
	BGT      |loc_08006B36|
	LDRB     r0, [r3, #5]
	CMP      r0, #8
	BGT      |loc_08006B36|
	LDRB     r0, [r3, #4]
	STRB     r0, [r4]
	LDRB     r0, [r3, #5]
	STRB     r0, [r4, #1]
	LDRB     r0, [r3, #6]
	STRB     r0, [r4, #2]
	LDRB     r0, [r3, #7]
	STRB     r0, [r4, #3]
	B        |loc_08006B44|
|loc_08006B36|
	MOV      r0, #4
	STRB     r0, [r4]
	STRB     r0, [r4, #2]
	MOV      r0, #6
	STRB     r0, [r4, #1]
	MOV      r0, #0
	STRB     r0, [r4, #3]
|loc_08006B44|
	LDRB     r1, [r4, #2]
	LDR      r0, [r5, #4]
	ADD      r0, #0xc
	BL       |inc_0x03d784_0x041118| + 0x1a08
	LDRB     r1, [r4, #1]
	LDR      r0, [r5, #4]
	LDR      r2, [pc, #0x44]
	ADD      r0, r0, r2
	BL       |inc_0x03d784_0x041118| + 0xca6
	ADD      sp, #0x14
	POP      {r4, r5, pc}
