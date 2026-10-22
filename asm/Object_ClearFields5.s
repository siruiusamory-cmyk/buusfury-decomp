	CODE16
|Object_ClearFields5|
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0, #0x38]
	LDR      r2, [r0, #0x40]
	ADD      r2, r1, r2
	STR      r2, [r0, #0x38]
	LSR      r1, r2, #0x10
	BEQ      |loc_0802A8FC|
	ASR      r4, r2, #0x10
	LSL      r3, r4, #1
	ADD      r3, r3, r4
	LDR      r1, [r0, #0x34]
	LSL      r3, r3, #2
	ADD      r1, r1, r3
	STR      r1, [r0, #0x34]
	LDR      r3, [r0, #0x3c]
	SUB      r3, r3, r4
	STR      r3, [r0, #0x3c]
	CMP      r3, #0
	BGT      |loc_0802A8DC|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x128]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	POP      {r4, r5, r6, pc}
|loc_0802A8DC|
	MOV      r3, #0
	LDRSB    r5, [r1, r3]
	LDR      r4, [r0, #0x10]
	MOV      r3, #1
	SUB      r4, r4, r5
	STR      r4, [r0, #0x20]
	LDRSB    r6, [r1, r3]
	LDR      r5, [r0, #0x14]
	SUB      r5, r5, r6
	STR      r5, [r0, #0x24]
	LDRB     r3, [r1, #2]
	LDRB     r1, [r1, #3]
	ADD      r3, r4, r3
	ADD      r1, r5, r1
	STR      r1, [r0, #0x2c]
	STR      r3, [r0, #0x28]
|loc_0802A8FC|
	LSL      r1, r2, #0x10
	LSR      r1, r1, #0x10
	STR      r1, [r0, #0x38]
	POP      {r4, r5, r6, pc}
	LDR      r1, [pc, #0xf4]
	PUSH     {r4, r5}
	LDR      r1, [r1, #4]
	LDR      r3, [r0, #0x20]
	ADD      r1, #0x18
	LDR      r4, [r1]
	SUB      sp, #8
	SUB      r3, r3, r4
	LDR      r4, [r0, #0x24]
	LDR      r5, [r1, #4]
	ADD      r2, r0, #0
	SUB      r4, r4, r5
	STR      r4, [sp, #4]
	ADD      r2, #0x18
	STR      r3, [sp]
	STMIA    r2!, {r3, r4}
	LDR      r2, [r0, #0x20]
	LDR      r3, [r1, #8]
	CMP      r2, r3
	BGE      |sub_0802A94C|
	LDR      r2, [r1]
	LDR      r3, [r0, #0x28]
	CMP      r2, r3
	BGE      |sub_0802A94C|
	LDR      r2, [r0, #0x24]
	LDR      r3, [r1, #0xc]
	CMP      r2, r3
	BGE      |sub_0802A94C|
	LDR      r1, [r1, #4]
	LDR      r0, [r0, #0x2c]
	CMP      r1, r0
	BGE      |sub_0802A94C|
	MOV      r0, #1
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
