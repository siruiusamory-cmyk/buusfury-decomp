	CODE16
|loc_08011874|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r0, r1, #0
	ADD      r1, r2, #0
	ADD      r2, r3, #0
	ADD      r4, #0xc
	STMIA    r4!, {r0, r1, r2}
	LDR      r3, [pc, #0x210]
	SUB      r4, #0x18
	STR      r3, [r4]
	BL       |inc_0x049120_0x055620| + 0x5370
	ADD      r0, r4, #0
	POP      {r4, pc}
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	LDR      r4, [r0, #0xc]
	ADD      r5, r0, #0
	LDRB     r0, [r4]
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	SUB      sp, #4
	STRB     r0, [r4]
	BNE      |loc_080118C2|
	LDRH     r0, [r4, #2]
	LDR      r1, [pc, #0x1e4]
	CMP      r0, r1
	BEQ      |loc_080118C2|
	MOV      r3, #2
	LDR      r0, [pc, #0x1d8]
	LDRSH    r1, [r4, r3]
	LDR      r0, [r0, #8]
	BL       |loc_0801142A|
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #2]
|loc_080118C2|
	LDR      r0, [sp, #8]
	ADD      r1, r6, #0
	ADD      r2, r7, #0
	ADD      r5, #0xc
	STMIA    r5!, {r0, r6, r7}
	BL       |inc_0x049120_0x055620| + 0x5370
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	CMP      r1, #0xa
	BEQ      |loc_080118EA|
	CMP      r1, #0xb
	BNE      |sub_08011916|
	ADD      r0, #0xc
	LDMIA    r0!, {r0, r1, r2}
	BL       |inc_0x049120_0x055620| + 0x5370
	MOV      r0, #0
	POP      {r4, pc}
|loc_080118EA|
	LDR      r4, [r0, #0xc]
	LDRB     r0, [r4]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r4]
	BNE      |loc_08011912|
	LDRH     r0, [r4, #2]
	LDR      r1, [pc, #0x194]
	CMP      r0, r1
	BEQ      |loc_08011912|
	MOV      r3, #2
	LDR      r0, [pc, #0x188]
	LDRSH    r1, [r4, r3]
	LDR      r0, [r0, #8]
	BL       |loc_0801142A|
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #2]
|loc_08011912|
	MOV      r0, #0
	POP      {r4, pc}
