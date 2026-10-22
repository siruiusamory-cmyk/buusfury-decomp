	CODE16
|sub_08006BCE|
	LSR      r7, r0, #0x20
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x184]
	MOV      r2, #0
	MOV      r1, #0xd
	LDR      r0, [r4]
	BL       |loc_08011C0C|
	MOV      r1, #0xd
	LDR      r0, [r4, #4]
	BL       |inc_0x153f2_0x1a3f2| + 0x3fbc
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x16c]
	ADD      r5, r0, #0
	LDR      r0, [r4]
	BL       |loc_08011E94|
	MOV      r2, #0
	MOV      r1, #0xe
	LDR      r0, [r4]
	BL       |loc_08011C0C|
	MOV      r1, #0xe
	LDR      r0, [r4, #4]
	BL       |inc_0x153f2_0x1a3f2| + 0x3fbc
	ADD      r0, r5, #0
	BEQ      |loc_08006C16|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08006C16|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x13c]
	MOV      r2, #0
	MOV      r1, #0xc
	LDR      r0, [r5]
	BL       |loc_08011C0C|
	ADD      r4, r0, #0
	LDR      r0, [r5, #4]
	MOV      r1, #0xc
	BL       |inc_0x153f2_0x1a3f2| + 0x3fbc
	SUB      r1, r0, #1
	ORR      r4, r1
	BNE      |sub_08006C3A|
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
