	CODE16
|sub_0802361A|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1a4]
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11458
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x667e
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r4, [pc, #0x190]
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11426
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x118c6
	LDR      r0, [pc, #0x184]
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_0802372C|
	MOV      r1, #0
	STR      r1, [r0]
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x119ac
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11458
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11426
	MOV      r4, #1
	LSL      r4, r4, #0x1a
	LDRH     r0, [r4]
	LSR      r1, r4, #0x12
	BIC      r0, r1
	STRH     r0, [r4]
	MOV      r0, #0xff
	ADD      r0, #0x1d
	BL       |GBARam_Malloc|
	LDR      r1, [pc, #0x138]
	CMP      r0, #0
	BEQ      |loc_08023696|
	MOV      r2, #0
	STMIA    r0!, {r1, r2}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r2, [r1, #0xc]
	STR      r2, [r1, #8]
	MOV      r3, #0xff
	ADD      r3, #0x15
	STR      r2, [r1, #0x10]
	STRB     r2, [r3, r0]
	LDR      r3, [pc, #0x138]
	STR      r3, [r0]
	STR      r2, [r1, #0x18]
|loc_08023696|
	BL       |inc_0x03d784_0x041118| + 0x11c
	CMP      r0, #2
	BEQ      |sub_080236D8|
	LDRH     r0, [r4]
	MOV      r1, #0x11
	LSL      r1, r1, #8
	ORR      r0, r1
	STRH     r0, [r4]
	MOV      r0, #0xbf
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_080236CE|
	MOV      r5, #1
	ADD      r3, r5, #0
	MOV      r2, #0xd
	MOV      r1, #0x5e
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x5308
	LDR      r0, [pc, #0x10c]
	STR      r0, [r4]
	MOV      r0, #0xb
	LSL      r0, r0, #6
	ADD      r0, r4, r0
	STR      r5, [r0, #0x38]
|loc_080236CE|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
