	CODE16
|sub_08017DA2|
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x10]
	ADD      r5, r1, #0
	SUB      sp, #0xc
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r4, #0
	ADD      r1, #8
	STR      r1, [sp]
	ADD      r3, r4, #0
	ADD      r3, #0x14
	ADD      r1, r0, #0
	STR      r5, [sp, #4]
	LDR      r2, [r4, #0xc]
	MOV      r0, #0
	BL       |loc_08017C1C|
	ADD      sp, #0xc
	POP      {r4, r5, pc}
	PUSH     {r4, lr}
	LDR      r1, [pc, #0x84]
	SUB      sp, #0x10
	LDR      r4, [r1]
	ADD      r1, r0, #0
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0xfca2
	ADD      r4, #0x80
	LDR      r1, [r4, #0x28]
	MOV      r2, #1
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0x97d8
	MOV      r2, #1
	MOV      r0, sp
	LDR      r1, [r4, #0x30]
	BL       |inc_0x0158_0x143f2| + 0x97d8
	ADD      sp, #0x10
	POP      {r4, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0x24
	ADD      r4, sp, #0x14
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [pc, #0x5c]
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_08017E30|
	ADD      r0, sp, #4
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [sp, #0x14]
	LDR      r1, [sp, #0xc]
	CMP      r0, r1
	BGE      |loc_08017E30|
	LDR      r0, [sp, #4]
	LDR      r1, [sp, #0x1c]
	CMP      r0, r1
	BGE      |loc_08017E30|
	LDR      r0, [sp, #0x18]
	LDR      r1, [sp, #0x10]
	CMP      r0, r1
	BGE      |loc_08017E30|
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x20]
	CMP      r0, r1
	BLT      |loc_08017E4A|
|loc_08017E30|
	LDR      r0, [pc, #0x20]
	MOV      r2, #0
	LDR      r5, [r0]
	ADD      r5, #0x80
	LDR      r1, [r5, #0x28]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x97d8
	MOV      r2, #0
	ADD      r0, r4, #0
	LDR      r1, [r5, #0x30]
	BL       |inc_0x0158_0x143f2| + 0x97d8
|loc_08017E4A|
	ADD      sp, #0x24
	POP      {r4, r5, pc}
	LSL      r0, r0, #0
	LDMIA    r1!, {r2, r3, r5}
	LSR      r4, r0, #0x20
	STMIA    r2!, {r3, r4, r5}
	LSR      r7, r5, #1
|loc_08017E58|
	SUB      r4, r5, r6
	LSL      r0, r0, #0xc
	LDR      r5, [sp, #0x60]
	LSR      r4, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x10
	BNE      |sub_08017E80|
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08017E80|
	ADD      r0, r4, #0
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
