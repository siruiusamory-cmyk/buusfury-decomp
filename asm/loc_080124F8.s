	CODE16
|loc_080124F8|
	PUSH     {r4, r5, r6, lr}
	LDR      r5, [pc, #0xdc]
	ADD      r4, r0, #0
	ADD      r5, #0xc
	MOV      r6, #0
	LDR      r0, [r4, #0x28]
	CMP      r0, #0
	BEQ      |loc_08012530|
	LDR      r0, [r4, #0x28]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0801252C|
	LDR      r0, [r4, #0x28]
	CMP      r0, #0
	BEQ      |loc_0801252A|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0801252A|
	STR      r6, [r4, #0x28]
|loc_0801252C|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|loc_08012530|
	LDRH     r1, [r4, #8]
	LDR      r0, [r4]
	LSL      r1, r1, #2
	LDR      r1, [r0, r1]
	LSR      r0, r1, #0x10
	BNE      |sub_08012552|
	LSL      r0, r1, #0x10
	LSR      r0, r0, #0x10
	LDR      r1, [pc, #0x90]
	STRH     r0, [r4, #8]
	LDR      r1, [r1]
	CMP      r1, #0
	BNE      |loc_0801254E|
	LDR      r1, [r4, #4]
	STRH     r0, [r1]
|loc_0801254E|
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
