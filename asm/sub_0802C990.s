	CODE16
|sub_0802C990|
	PUSH     {r3, lr}
	MOV      r0, #0xff
	STRB     r0, [r1, #0xc]
	STRB     r0, [r1, #0xd]
	MOV      r0, #0x37
	MVN      r0, r0
	LDRH     r0, [r0, r1]
	MOV      r1, #0x40
	ORR      r0, r1
	LDR      r1, [pc, #0x104]
	STRH     r0, [r1]
	LDRH     r0, [r1, #2]
	ADD      r2, r1, #2
	MOV      r1, #0x40
	ORR      r0, r1
	STRH     r0, [r2]
	ADD      r2, #2
	LDRH     r0, [r2]
	ORR      r0, r1
	STRH     r0, [r2]
	ADD      r2, #2
	LDRH     r0, [r2]
	ORR      r0, r1
	STRH     r0, [r2]
	LSL      r2, r1, #3
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0xe4]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0xdc]
	LDR      r0, [pc, #0xe0]
	BL       |inc_0x049120_0x055620| + 0x24
	POP      {r3, pc}
	LDR      r2, [pc, #0xc8]
	PUSH     {r3, lr}
	MOV      r1, #0
	STRB     r1, [r2, #0xc]
	STRB     r1, [r2, #0xd]
	MOV      r1, #0x37
	MVN      r1, r1
	LDRH     r2, [r1, r2]
	MOV      r1, #0x40
	LDR      r3, [pc, #0xb8]
	BIC      r2, r1
	STRH     r2, [r3]
	ADD      r3, #2
	LDRH     r2, [r3]
	BIC      r2, r1
	STRH     r2, [r3]
	ADD      r3, #2
	LDRH     r2, [r3]
	BIC      r2, r1
	STRH     r2, [r3]
	ADD      r3, #2
	LDRH     r2, [r3]
	BIC      r2, r1
	STRH     r2, [r3]
	CMP      r0, #0
	BEQ      |loc_0802CA1A|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802CA1A|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0, #4]
	ADD      r1, #1
	STR      r1, [r0, #4]
	LDR      r0, [r0, #8]
	CMP      r1, r0
	BLT      |Mosaic_WriteSize2|
	MOV      r0, #1
	POP      {r3, pc}
