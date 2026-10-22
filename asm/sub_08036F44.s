	CODE16
|sub_08036F44|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08036F60|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08036F60|
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	POP      {r5, r6, r7, pc}
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0, #0x3c]
	ADD      r4, r0, #0
	LDRB     r0, [r1, #3]
	LDRB     r2, [r1, #2]
	LDR      r5, [pc, #0x2b8]
	MUL      r2, r0
	LDRH     r0, [r4, #0xc]
	LDR      r1, [r1, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r5
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r1, [r4, #0x3c]
	MOV      r3, #1
	LDRB     r2, [r1, #0xe]
	LDRB     r0, [r1, #0xf]
	LSL      r3, r3, #9
	MUL      r2, r0
	LDRH     r0, [r4, #0xc]
	LDR      r1, [r1, #0x14]
	LSL      r0, r0, #5
	ADD      r0, r0, r5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
	POP      {r3, r4, r5, pc}
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x1c
	BNE      |sub_08036FC0|
	MOV      r0, #0x48
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08036FC0|
	ADD      r0, r4, #0
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
