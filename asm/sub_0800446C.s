	CODE16
|sub_0800446C|
	PUSH     {r4, r5, r6, lr}
	LDR      r4, [r2]
	MOV      r3, #0
	CMP      r4, #0
	BLE      |loc_080044AA|
|loc_08004476|
	LSL      r5, r3, #2
	ADD      r5, r5, r2
	LDR      r5, [r5, #4]
	LSL      r6, r5, #4
	LSR      r6, r6, #4
	CMP      r6, r1
	BNE      |loc_080044A4|
	LSR      r5, r5, #0x1c
	BNE      |loc_080044A4|
	SUB      r4, #1
	STR      r4, [r2]
	SUB      r0, r4, r3
	BEQ      |loc_080044A2|
	LSL      r4, r0, #2
	LSL      r0, r3, #2
	ADD      r0, r0, r2
	ADD      r1, r0, #0
	ADD      r1, #8
	ADD      r0, #4
	ADD      r2, r4, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080044A2|
	POP      {r4, r5, r6, pc}
|loc_080044A4|
	ADD      r3, #1
	CMP      r4, r3
	BGT      |loc_08004476|
|loc_080044AA|
	MOV      r5, #0
	CMP      r4, #0
	BLE      |loc_080044A2|
|loc_080044B0|
	LSL      r3, r5, #2
	ADD      r3, r3, r2
	ADD      r3, #4
	LDR      r6, [r3]
	LSL      r6, r6, #4
	LSR      r6, r6, #4
	CMP      r6, r1
	BNE      |loc_0800450E|
	LDR      r4, [r3]
	MOV      r3, #0x2c
	LSL      r1, r4, #4
	LSR      r1, r1, #4
	MUL      r1, r3
	LDR      r3, [pc, #0x70]
	LSR      r4, r4, #0x1c
	ADD      r1, r1, r3
	MOV      r3, #0x68
	SUB      r4, #1
	LDRB     r1, [r1, #0x14]
	MUL      r3, r4
	ADD      r0, r3, r0
	LDR      r3, [pc, #0x64]
	LSL      r1, r1, #2
	ADD      r0, r0, r1
	ADD      r0, r0, r3
	LDR      r3, [pc, #0x44]
	ADD      r3, #0x14
	LDR      r1, [r3, r1]
|loc_080044E8|
	STR      r1, [r0]
	LDR      r3, [r0]
	CMP      r3, r1
	BNE      |loc_080044E8|
	LDR      r1, [r2]
	ADD      r0, r2, #0
	SUB      r1, #1
	STR      r1, [r2]
	SUB      r1, r1, r5
	BEQ      |loc_080044A2|
	LSL      r2, r1, #2
	LSL      r1, r5, #2
	ADD      r0, r1, r0
	ADD      r1, r0, #0
	ADD      r1, #8
	ADD      r0, #4
	BL       |inc_0x049120_0x055620| + 0x18
	POP      {r4, r5, r6, pc}
|loc_0800450E|
	ADD      r5, #1
	CMP      r4, r5
	BGT      |loc_080044B0|
	POP      {r4, r5, r6, pc}
	LSL      r0, r0, #0
	LDMIA    r5!, {r3, r4, r6}
	LSR      r7, r6, #1
	LDRH     r0, [r4, #0x24]
	LSL      r0, r0, #0
	LDMIA    r5!, {r3, r7}
	LSR      r7, r6, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STRB     r4, [r4, r6]
	LSR      r5, r0, #0x20
	LDMIA    r4!, {r2, r3, r4, r6, r7}
	LSR      r7, r6, #1
	LSR      r0, r5, #2
	LSL      r0, r0, #0
	BGE      |loc_080045D0|
	LSR      r7, r5, #1
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	LSL      r4, r6, #0x14
	LSL      r0, r0, #0
