	CODE16
|loc_0800938C|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	CMP      r1, #0
	BEQ      |loc_080093AE|
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	LDR      r0, [pc, #0x29c]
	BL       |inc_0x049120_0x055620| + 0xc
|loc_080093AE|
	ADD      r6, r5, #0
	ADD      r6, #0x80
	LDR      r4, [r6, #0xc]
	LDR      r7, [pc, #0x294]
	ADD      r1, r4, #0
	LDR      r0, [r7, #4]
	BL       |sub_08009B80|
	ADD      r1, r4, #0
	LDR      r0, [r7]
	BL       |loc_0800924C|
	ADD      r1, r4, #0
	LDR      r0, [r7, #4]
	BL       |loc_08009BD4|
	ADD      r1, r5, #0
	LDR      r0, [r7]
	BL       |loc_0800929C|
	LDR      r0, [r4, #0x3c]
	LDR      r1, [pc, #0x270]
	LSL      r0, r0, #3
	ADD      r1, #0x14
	ADD      r0, r0, r1
	LDRH     r1, [r0]
	LDR      r2, [r6, #0x34]
	ADD      r2, r1, r2
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	STRH     r2, [r1, #8]
	LDRH     r2, [r0, #2]
	LDR      r3, [r6, #0x38]
	ADD      r2, r2, r3
	STRH     r2, [r1, #0xa]
	LDRH     r2, [r0, #4]
	LDR      r3, [r6, #0x3c]
	ADD      r2, r2, r3
	STRH     r2, [r1, #0xc]
	LDRH     r0, [r0, #6]
	MOV      r2, #0xc0
	LDR      r2, [r2, r5]
	LDR      r3, [pc, #0x24c]
	ADD      r0, r0, r2
	STRH     r0, [r1, #0xe]
	ADD      r0, r5, #0
	ADD      r0, #0xa0
	LDRH     r2, [r0, #4]
	STRH     r2, [r3, #0x10]
	LDRB     r3, [r0, #1]
	LDR      r2, [pc, #0x240]
	STRB     r3, [r2, #2]
	LDRB     r3, [r0]
	STRB     r3, [r2, #3]
	LDRH     r0, [r0, #2]
	STRH     r0, [r1]
	POP      {r3, r4, r5, r6, r7, pc}
