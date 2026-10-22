	CODE16
|loc_080046F4|
	PUSH     {r3, lr}
	LDRB     r1, [r0, #1]
	LSL      r2, r1, #0x1e
	LSR      r2, r2, #0x1f
	BNE      |loc_08004720|
	MOV      r2, #2
	ORR      r1, r2
	STRB     r1, [r0, #1]
	MOV      r0, #0
	BL       |loc_0800B854|
	ADD      r1, r0, #0
	MOV      r0, #0xf
	MVN      r0, r0
	STR      r0, [r1, #0x28]
	MOV      r0, #1
	STR      r0, [r1, #0x14]
	LDR      r0, [pc, #0xf8]
	SUB      r0, #0x14
	LDR      r0, [r0, #0x10]
	BL       |List_Append|
|loc_08004720|
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	LDRB     r1, [r0, #1]
	ADD      r6, r2, #0
	MOV      r2, #2
	ORR      r1, r2
	STRB     r1, [r0, #1]
	MOV      r0, #0x38
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800473E|
	ADD      r1, r4, #0
	B        |loc_0800474E|
|loc_0800473E|
	ADD      r0, r4, #0
	BL       |loc_0800B854|
	LDR      r0, [pc, #0xec]
	ADD      r1, r4, #0
	STR      r0, [r4]
	ADD      r4, #0x30
	STMIA    r4!, {r5, r6}
|loc_0800474E|
	MOV      r0, #0xf
	MVN      r0, r0
	STR      r0, [r1, #0x28]
	MOV      r0, #1
	STR      r0, [r1, #0x14]
	LDR      r0, [pc, #0xb4]
	SUB      r0, #0x14
	LDR      r0, [r0, #0x10]
	BL       |List_Append|
	POP      {r4, r5, r6, pc}
