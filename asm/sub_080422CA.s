	CODE16
|sub_080422CA|
	MOV      r1, #0
	STRB     r1, [r2, #3]
|loc_080422CE|
	BL       |inc_0x042118_0x049114| + 0x2d98
	POP      {r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x38c]
	ADD      r4, r0, #0
	LDR      r0, [r6]
	LDR      r7, [pc, #0x388]
	LDRB     r0, [r0, #4]
	CMP      r0, #0
	BEQ      |loc_0804230E|
	MOV      r5, #0
|loc_080422E6|
	LSL      r0, r5, #2
	LDR      r0, [r7, r0]
	LDRH     r1, [r0]
	LSL      r1, r1, #0x10
	BPL      |loc_08042304|
	LDRB     r0, [r0, #0x1a]
	ADD      r1, r0, #0
	AND      r1, r4
	BEQ      |loc_08042304|
	BIC      r0, r4
	ADD      r2, r0, #0
	ADD      r1, r5, #0
	MOV      r0, #0x20
	BL       |inc_0x042118_0x049114| + 0x28f4
|loc_08042304|
	ADD      r5, #1
	LSL      r5, r5, #0x18
	LSR      r5, r5, #0x18
	CMP      r5, #4
	BCC      |loc_080422E6|
|loc_0804230E|
	LDR      r0, [r6]
	LDRB     r0, [r0, #5]
	CMP      r0, #0
	BEQ      |loc_0804233A|
	MOV      r5, #0
|loc_08042318|
	LSL      r0, r5, #2
	LDR      r0, [r7, r0]
	LDRH     r1, [r0, #0x34]
	LSL      r1, r1, #0x10
	BPL      |loc_08042330|
	ADD      r0, #0x40
	LDRB     r0, [r0, #0xe]
	AND      r0, r4
	BEQ      |loc_08042330|
	ADD      r0, r5, #0
	BL       |inc_0x042118_0x049114| + 0x29dc
|loc_08042330|
	ADD      r5, #1
	LSL      r5, r5, #0x18
	LSR      r5, r5, #0x18
	CMP      r5, #4
	BCC      |loc_08042318|
|loc_0804233A|
	LDR      r1, [r6]
	LDRB     r0, [r1, #6]
	CMP      r0, #0
	BEQ      |loc_08042370|
	BIC      r0, r4
	STRB     r0, [r1, #6]
	LDR      r3, [pc, #0x314]
	MOV      r0, #0
	LDR      r5, [pc, #0x320]
	ADD      r3, #0x23
|loc_0804234E|
	LSL      r1, r0, #2
	LDR      r1, [r5, r1]
	LDRH     r2, [r1]
	CMP      r2, r3
	BNE      |loc_08042366|
	LDRB     r2, [r1, #3]
	AND      r2, r4
	BEQ      |loc_08042366|
	ADD      r1, #3
	LDRB     r2, [r1]
	BIC      r2, r4
	STRB     r2, [r1]
|loc_08042366|
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	CMP      r0, #4
	BCC      |loc_0804234E|
|loc_08042370|
	POP      {r3, r4, r5, r6, r7, pc}
