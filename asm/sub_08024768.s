	CODE16
|sub_08024768|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1d0]
	SUB      sp, #4
	LDR      r5, [pc, #0x1d0]
	STR      r0, [r4]
	LDRB     r0, [r5]
	LDR      r7, [pc, #0x1d0]
	LDR      r6, [pc, #0x1dc]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r5]
	BNE      |loc_0802479A|
	LDRH     r0, [r5, #2]
	CMP      r0, r6
	BEQ      |loc_0802479A|
	MOV      r3, #2
	LDRSH    r1, [r5, r3]
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x112d2
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r5, #2]
|loc_0802479A|
	LDR      r0, [pc, #0x1c0]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	CMP      r1, r6
	BEQ      |loc_080247AA|
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080247AA|
	LDR      r0, [pc, #0x1b4]
	STR      r0, [r4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_080247BA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080247BA|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	ADD      r0, #0x48
	ADD      r5, r1, #0
	LDR      r1, [r4, #0x20]
	LDMIA    r0!, {r2}
	SUB      sp, #0x48
	ADD      r1, r1, r2
	STR      r1, [r4, #0x20]
	LDR      r1, [r4, #0x24]
	LDR      r0, [r0]
	ADD      r0, r1, r0
	STR      r0, [r4, #0x24]
	LDR      r0, [r4, #0x50]
	ADD      r0, #1
	STR      r0, [r4, #0x50]
	ASR      r0, r0, #2
	LSL      r1, r0, #0x18
	LSR      r1, r1, #0x18
	MOV      r0, #0x44
	STRB     r1, [r0, r4]
	CMP      r1, #4
	BLS      |sub_080247FA|
	LDR      r0, [pc, #0x158]
	ADD      r1, r4, #0
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x48
	POP      {r4, r5, r6, pc}
