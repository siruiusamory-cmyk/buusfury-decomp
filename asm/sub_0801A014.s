	CODE16
|sub_0801A014|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0, #0x15]
	ADD      r5, r1, #0
	LSL      r0, r0, #1
	ADD      r0, r0, r4
	ADD      r0, #0x2e
	LDRB     r0, [r0]
	LDR      r1, [pc, #0x2e8]
	LSL      r0, r0, #2
	ADD      r1, #0x3c
	LDR      r1, [r1, r0]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x13440
	LDRB     r0, [r4, #0x15]
	LSL      r0, r0, #1
	ADD      r0, r0, r4
	ADD      r0, #0x2e
	LDRB     r4, [r0]
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801A050|
	LDR      r1, [pc, #0x2cc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	MOV      r1, #0
	STR      r1, [r0, #0xc]
|loc_0801A050|
	ADD      r4, r0, #0
	MOV      r1, #0x13
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0x2a8]
	PUSH     {r3, lr}
	LDR      r1, [r1, #0x14]
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BNE      |sub_0801A074|
	MOV      r0, #0
	POP      {r3, pc}
