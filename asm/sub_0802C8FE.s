	CODE16
|sub_0802C8FE|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0x70]
	LSR      r5, r6, #1
	LDR      r1, [pc, #0x1f0]
	LSR      r5, r6, #1
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	LSL      r3, r0, #4
	LDR      r1, [pc, #0x194]
	ADD      r0, r3, r0
	STRB     r0, [r1, #0xc]
	STRB     r0, [r1, #0xd]
	BX       lr
	LDR      r0, [pc, #0x18c]
	LDR      r2, [pc, #0x18c]
	LDRH     r1, [r0]
	MOV      r0, #0x40
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	ORR      r0, r1
	STRH     r0, [r2]
	BX       lr
	LDR      r0, [pc, #0x168]
	LDR      r2, [pc, #0x164]
	LDRH     r1, [r0]
	MOV      r0, #0x40
	BIC      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	BIC      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	BIC      r1, r0
	STRH     r1, [r2]
	ADD      r2, #2
	LDRH     r1, [r2]
	BIC      r1, r0
	STRH     r1, [r2]
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [r0, #4]
	ADD      r1, #1
	STR      r1, [r0, #4]
	LDR      r0, [r0, #8]
	CMP      r1, r0
	BLT      |Mosaic_WriteSize1|
	MOV      r0, #1
	POP      {r3, pc}
