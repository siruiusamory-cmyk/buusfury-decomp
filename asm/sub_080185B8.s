	CODE16
|sub_080185B8|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1d8]
	SUB      sp, #4
	STR      r0, [r4]
	LDR      r0, [r4, #0x10]
	LDR      r7, [pc, #0x1c4]
	LDR      r6, [pc, #0x1c0]
	CMP      r0, #0
	BEQ      |loc_080185F0|
	LDR      r5, [r0, #8]
	LDRB     r0, [r5]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r5]
	BNE      |loc_080185F0|
	LDRH     r0, [r5, #2]
	CMP      r0, r6
	BEQ      |loc_080185F0|
	MOV      r3, #2
	LDRSH    r1, [r5, r3]
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x112d2
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r5, #2]
|loc_080185F0|
	LDR      r0, [pc, #0x1a0]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	CMP      r1, r6
	BEQ      |loc_08018600|
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08018600|
	LDR      r0, [pc, #0x198]
	STR      r0, [r4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_08018610|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08018610|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
