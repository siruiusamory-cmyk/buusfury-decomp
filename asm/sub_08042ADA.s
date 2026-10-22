	CODE16
|sub_08042ADA|
	LDR      r3, [pc, #0xd4]
	MOV      r2, #0
	STRB     r2, [r3, #5]
	STRB     r2, [r3, #4]
	MOV      r0, #0xff
	STRB     r0, [r3, #6]
	STRB     r2, [r3, #7]
	STRB     r2, [r3, #0x10]
	STRB     r2, [r3, #0xc]
	MOV      r0, #0x24
	STRB     r2, [r0, r3]
	MOV      r0, #0x30
	STRB     r2, [r0, r3]
	MOV      r0, #0
|loc_08042AF6|
	LSL      r1, r0, #1
	ADD      r1, r1, r3
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRH     r2, [r1, #0x28]
	STRH     r2, [r1, #0x34]
	CMP      r0, #4
	BCC      |loc_08042AF6|
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |sub_08042ADA|
	LDR      r0, [pc, #0x9c]
	MOV      r2, #1
	STRB     r2, [r0, #4]
	MOV      r1, #2
	STRB     r1, [r0, #5]
	STR      r4, [r0, #0x3c]
	LDRB     r1, [r4, #0x11]
	STRB     r1, [r0, #9]
	LDRH     r1, [r4, #0x12]
	STRH     r1, [r0, #0x32]
	LDRH     r1, [r4, #0x14]
	STRH     r1, [r0, #0x18]
	LDRB     r1, [r4, #0x10]
	CMP      r1, #0
	BEQ      |loc_08042B32|
	STRB     r2, [r0, #0xb]
|loc_08042B32|
	POP      {r4, pc}
	LDR      r1, [pc, #0x78]
	MOV      r0, #0x15
	STRB     r0, [r1, #4]
	BX       lr
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	LDR      r5, [pc, #0x70]
	ADD      r4, r0, #0
	LDRB     r0, [r5, #4]
	ADD      r7, r1, #0
	ADD      r6, r3, #0
	CMP      r0, #0
	SUB      sp, #4
	BEQ      |sub_08042B68|
	CMP      r0, #8
	BNE      |loc_08042B56|
	CMP      r4, #1
	BEQ      |sub_08042B68|
|loc_08042B56|
	MOV      r0, #1
	STRH     r0, [r5, #0x14]
	MOV      r1, #1
	MOV      r0, #0xf3
	BL       |loc_0804333c|
	MOV      r0, #1
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
