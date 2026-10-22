	CODE16
|sub_0800F740|
	PUSH     {r4, r5, lr}
	ADD      r5, r1, #0
	MOV      r1, #0x29
	LSL      r1, r1, #4
	ADD      r1, r0, r1
	LDRB     r1, [r1, #1]
	SUB      sp, #0x14
	CMP      r1, #0
	BNE      |loc_0800F76A|
	LDR      r1, [pc, #0x1b0]
	LDR      r4, [r1, #8]
	ADD      r1, r0, #0
	ADD      r0, sp, #4
	BL       |Object_WriteBounds1|
	ADD      r4, #0x80
	LDR      r1, [r4, #0x30]
	ADD      r2, r5, #0
	ADD      r0, sp, #4
	BL       |loc_08009930|
|loc_0800F76A|
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x19c]
	SUB      sp, #0x10
	STR      r0, [r4]
	MOV      r0, #0x29
	LSL      r0, r0, #4
	ADD      r0, r4, r0
	LDRB     r0, [r0, #1]
	ADD      r6, r1, #0
	CMP      r0, #0
	BNE      |loc_0800F79E|
	LDR      r0, [pc, #0x17c]
	ADD      r1, r4, #0
	LDR      r5, [r0, #8]
	MOV      r0, sp
	BL       |Object_WriteBounds1|
	ADD      r5, #0x80
	LDR      r1, [r5, #0x30]
	MOV      r2, #1
	MOV      r0, sp
	BL       |loc_08009930|
|loc_0800F79E|
	LDR      r3, [pc, #0x174]
	MOV      r0, #0
	LDR      r1, [r3]
	CMP      r1, #0
	BLE      |loc_0800F7B8|
|loc_0800F7A8|
	LSL      r2, r0, #2
	ADD      r2, r2, r3
	LDR      r2, [r2, #4]
	CMP      r2, r4
	BEQ      |loc_0800F7BC|
	ADD      r0, #1
	CMP      r1, r0
	BGT      |loc_0800F7A8|
|loc_0800F7B8|
	MOV      r0, #0
	MVN      r0, r0
|loc_0800F7BC|
	SUB      r1, #1
	STR      r1, [r3]
	SUB      r1, r1, r0
	BEQ      |loc_0800F7D4|
	LSL      r0, r0, #2
	ADD      r0, r0, r3
	LSL      r2, r1, #2
	ADD      r1, r0, #0
	ADD      r1, #8
	ADD      r0, #4
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0800F7D4|
	MOV      r0, #0x47
	LSL      r0, r0, #3
	MOV      r1, #0
	ADD      r0, r4, r0
	BL       |loc_0800A9FE|
	MOV      r0, #0x8b
	LSL      r0, r0, #2
	ADD      r0, r4, r0
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_0800F7F6|
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_0800F7F6|
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |sub_0800E85E|
	CMP      r6, #0
	BEQ      |loc_0800F808|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0800F808|
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
