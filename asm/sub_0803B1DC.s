|sub_0803B1DC|
	EXPORT |sub_0803B1DC|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x10]
	LDR      r0, [r0, #0xc]
	ASR      r1, r1, #8
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	BL       |loc_0803A7FC|
	MOV      r0, #0
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	MOV      r6, #0
	ADD      r4, r0, #0
	CMP      r1, #0
	BNE      |loc_0803B23C|
	LDR      r0, [r2, #0x30]
	CMP      r0, r4
	BNE      |loc_0803B204|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|loc_0803B204|
	LDR      r0, [r2, #0x1c]
	LDRB     r0, [r0]
	CMP      r0, #1
	BNE      |sub_0803B238|
	ADD      r1, r2, #4
	ADD      r0, r4, #0
	BL       |sub_0803AF58|
	CMP      r0, #0
	BEQ      |sub_0803B238|
	LDR      r0, [pc, #0xbc]
	LDRB     r0, [r0]
	CMP      r0, #0
	BNE      |sub_0803B238|
	LDR      r5, [r4, #0x10]
	CMP      r5, #0
	BLE      |loc_0803B234|
	LDR      r0, [pc, #0xb4]
	BL       |inc_0x049120_0x055620| + 0xb944
	SUB      r0, r5, r0
	STR      r0, [r4, #0x10]
	BPL      |loc_0803B234|
	STR      r6, [r4, #0x10]
|loc_0803B234|
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
