	CODE16
|sub_08026C3C|
	MOV      r2, #3
	MOV      r0, #0x10
	STRB     r0, [r1, #0x12]
	LDRB     r0, [r1, #0x11]
	CMP      r0, r2
	BEQ      |loc_08026C60|
	STRB     r2, [r1, #0x11]
	LDRH     r0, [r1, #0xc]
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0x48]
	LDR      r1, [r1, #4]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	LSL      r2, r2, #7
	ADD      r1, r1, r2
	MOV      r2, #0x80
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08026C60|
	POP      {r3, pc}
	LDR      r2, [r1]
	ADD      r3, r2, #0
	ADD      r3, #8
	STR      r3, [r1]
	LDR      r1, [r0, #0x14]
	LDR      r1, [r1]
	STR      r1, [r2]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r2, #4]
	LSR      r1, r1, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r1, r1, #0xa
	ORR      r0, r1
	MOV      r1, #3
	LSL      r1, r1, #0xa
	BIC      r0, r1
	STR      r0, [r2, #4]
	MOV      r0, #0
	BX       lr
|sub_08026C8A|
	DCW      0x0000
	DCW      0x9680,0x0804,0xcb00
|sub_08026C92|
	LSR      r4, r6, #1
	STMIA    r0!, {r3, r6}
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r6, r3, #0
	ADD      r4, r2, #0
	CMP      r0, #0
	LDR      r5, [sp, #0x18]
	BNE      |loc_08026CB4|
	MOV      r0, #0x20
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08026CD8|
|loc_08026CB4|
	LDR      r1, [pc, #0x114]
	STR      r1, [r0]
	STR      r4, [r0, #0x1c]
	STR      r7, [r0, #0x10]
	STRH     r6, [r0, #0xc]
	LDRH     r1, [r4, #0x14]
	ADD      r1, r1, r5
	STRH     r1, [r0, #0x14]
	LDRB     r2, [r4, #0x16]
	MOV      r1, #1
	CMP      r2, #0
	BNE      |loc_08026CCE|
	MOV      r1, #0
|loc_08026CCE|
	STR      r1, [r0, #0x18]
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	LDR      r1, [r4, #0xc]
	STR      r1, [r0, #4]
|loc_08026CD8|
	POP      {r3, r4, r5, r6, r7, pc}
	LDR      r1, [r0, #0x18]
	CMP      r1, #0
	BNE      |loc_08026CE4|
	MOV      r0, #0
	BX       lr
|loc_08026CE4|
	LDR      r1, [r0, #0x1c]
	LDR      r0, [r0, #0x10]
	LDR      r2, [pc, #0xe4]
	ADD      r0, r0, r2
	LDR      r2, [r1]
	LDR      r3, [r0, #8]
	CMP      r2, r3
	BGE      |sub_08026D10|
	LDR      r2, [r0]
	LDR      r3, [r1, #8]
	CMP      r2, r3
	BGE      |sub_08026D10|
	LDR      r2, [r1, #4]
	LDR      r3, [r0, #0xc]
	CMP      r2, r3
	BGE      |sub_08026D10|
	LDR      r0, [r0, #4]
	LDR      r1, [r1, #0xc]
	CMP      r0, r1
	BGE      |sub_08026D10|
	MOV      r0, #1
	BX       lr
