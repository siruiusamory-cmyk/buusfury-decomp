	CODE16
|loc_08011E94|
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [pc, #0x84]
	ADD      r5, r0, r1
	LDR      r4, [r5]
	SUB      r4, #1
	BMI      |loc_08011EC2|
	ADD      r6, r0, #4
|loc_08011EA2|
	LDR      r1, [r6]
	LSL      r0, r4, #2
	ADD      r2, r1, #1
	ADD      r0, r0, r5
	LDR      r0, [r0, #4]
	LSL      r1, r1, #2
	ADD      r1, r1, r6
	STR      r2, [r6]
	STR      r0, [r1, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x20]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	SUB      r4, #1
	BPL      |loc_08011EA2|
|loc_08011EC2|
	MOV      r0, #0
	STR      r0, [r5]
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r1, #0
	LDR      r1, [r0, #4]
	ADD      r7, r0, #4
	MOV      r6, #0
	ADD      r5, r0, #0
	CMP      r1, #0
	BLE      |loc_08011EE8|
|loc_08011ED8|
	LSL      r0, r6, #2
	ADD      r0, r0, r7
	LDR      r0, [r0, #4]
	CMP      r0, r4
	BEQ      |loc_08011EEC|
	ADD      r6, #1
	CMP      r1, r6
	BGT      |loc_08011ED8|
|loc_08011EE8|
	MOV      r6, #0
	MVN      r6, r6
|loc_08011EEC|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r1, r6, #0
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x6d34
	LDR      r0, [pc, #0x18]
	ADD      r0, r5, r0
	LDR      r1, [r0]
	ADD      r2, r1, #1
	STR      r2, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r4, [r0, #4]
	POP      {r3, r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	CMP      r0, #0x24
	LSR      r7, r0, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LSL      r4, r1, #0x10
	LSL      r0, r0, #0
	CMP      r0, #0
	BEQ      |loc_08011F28|
	CMP      r0, #7
	BNE      |loc_08011F2C|
|loc_08011F28|
	MOV      r0, #0
	BX       lr
|loc_08011F2C|
	CMP      r0, #8
	BGE      |loc_08011F52|
	LDR      r1, [pc, #0x258]
	MOV      r3, #0x68
	LDR      r1, [r1]
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1, #0x14]
	LDR      r2, [pc, #0x248]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	ADD      r0, r1, r0
	LDRB     r0, [r0, #0xf]
|loc_08011F52|
	LDR      r1, [pc, #0x240]
	LSL      r0, r0, #2
	LDR      r0, [r1, r0]
	BX       lr
