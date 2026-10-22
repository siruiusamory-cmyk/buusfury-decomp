	CODE16
|sub_0802BFBC|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	LDR      r1, [pc, #0xa8]
	LSL      r0, r0, #2
	LDR      r4, [r1, r0]
	LDR      r6, [pc, #0x94]
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x03d784_0x041118| + 0x2864
	ADD      r0, #0x21
	LSR      r5, r0, #5
	LSL      r5, r5, #5
	LSL      r1, r5, #5
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x115da
	ADD      r3, r7, #0
	ADD      r2, r4, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |sub_0802BECC|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7}
	LDR      r2, [r1]
	LDR      r4, [r0, #0x10]
	MOV      r3, #0
	CMP      r4, #0
	BLE      |loc_0802C038|
	MOV      r6, #3
	LDR      r7, [pc, #0x74]
	LSL      r6, r6, #0xa
|loc_0802BFFE|
	STR      r7, [r2]
	LDR      r4, [r0, #0x14]
	ADD      r4, r4, r3
	LSL      r4, r4, #0x17
	LSR      r4, r4, #7
	ORR      r4, r7
	STR      r4, [r2]
	LDR      r5, [r0, #0x18]
	LSR      r4, r4, #8
	LSL      r5, r5, #0x18
	LSR      r5, r5, #0x18
	LSL      r4, r4, #8
	ORR      r4, r5
	STR      r4, [r2]
	LDRH     r4, [r0, #0xc]
	LDR      r5, [r2, #4]
	ADD      r4, r4, r3
	LSL      r4, r4, #0x16
	LSR      r5, r5, #0xa
	LSL      r5, r5, #0xa
	LSR      r4, r4, #0x16
	ORR      r4, r5
	BIC      r4, r6
	STR      r4, [r2, #4]
	LDR      r4, [r0, #0x10]
	ADD      r2, #8
	ADD      r3, #0x20
	CMP      r4, r3
	BGT      |loc_0802BFFE|
|loc_0802C038|
	STR      r2, [r1]
	POP      {r4, r5, r6, r7}
	MOV      r0, #0
	BX       lr
	PUSH     {r3, lr}
	CMP      r1, #0x27
	BNE      |sub_0802C054|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x10]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r0, #0
	POP      {r3, pc}
